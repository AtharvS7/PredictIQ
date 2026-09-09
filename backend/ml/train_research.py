"""Leakage-aware FP/hour experiment. Writes isolated, non-production artifacts.

Run from repository root: backend/.venv/Scripts/python.exe -m ml.train_research
with backend as working directory, or run this file directly.
"""
import hashlib
import json
import math
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import HuberRegressor, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_log_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

ROOT = Path(__file__).resolve().parent
SEED = 20260909


def metrics(actual, predicted) -> dict:
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    if not np.isfinite(predicted).all() or (predicted <= 0).any():
        raise ValueError("Nonpositive or nonfinite predictions")
    relative = np.abs(actual - predicted) / actual
    return {"n": len(actual), "mae_hours": float(mean_absolute_error(actual, predicted)),
            "median_absolute_percentage_error": float(np.median(relative) * 100),
            "pred25_percent": float(np.mean(relative <= 0.25) * 100),
            "rmsle": float(np.sqrt(mean_squared_log_error(actual, predicted))),
            "r2_hours": float(r2_score(actual, predicted))}


def split_projects(data: pd.DataFrame):
    train_cal, test = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
                           .split(data, groups=data.duplicate_group))
    sub = data.iloc[train_cal]
    train, calibration = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=SEED + 1)
                              .split(sub, groups=sub.duplicate_group))
    return train_cal[train], train_cal[calibration], test


def candidates() -> dict:
    estimators = {
        "median": DummyRegressor(strategy="median"),
        "power_law_ridge": Ridge(alpha=1.0),
        "power_law_huber": HuberRegressor(max_iter=1000),
        "random_forest": RandomForestRegressor(n_estimators=250, min_samples_leaf=8,
                                                random_state=SEED, n_jobs=1),
        "hist_gradient_boosting": HistGradientBoostingRegressor(max_iter=150,
                                      max_leaf_nodes=7, l2_regularization=5, random_state=SEED),
    }
    return {name: TransformedTargetRegressor(
        regressor=make_pipeline(FunctionTransformer(np.log1p, validate=True),
                                StandardScaler(), model), func=np.log1p, inverse_func=np.expm1)
            for name, model in estimators.items()}


def conformal_radius(actual, predicted, coverage=0.9) -> float:
    residuals = np.abs(np.log1p(actual) - np.log1p(predicted))
    rank = math.ceil((len(residuals) + 1) * coverage)
    if rank > len(residuals) or rank < 1:
        raise ValueError("Insufficient calibration data for requested coverage")
    return float(np.sort(residuals)[rank - 1])


def main() -> None:
    directory = ROOT / "experiments" / "reconstructed-v1"
    path = directory / "projects.csv"
    data = pd.read_csv(path)
    x, y = data[["size_fp"]], data.effort_hours
    train, calibration, test = split_projects(data)
    models, validation = candidates(), {}
    # Model choice uses training partition ONLY; hold out entire source cohorts.
    for name, model in models.items():
        folds = {}
        for source in sorted(data.source.unique()):
            val = train[data.iloc[train].source.to_numpy() == source]
            fit = train[data.iloc[train].source.to_numpy() != source]
            fit = fit[~data.iloc[fit].duplicate_group.isin(data.iloc[val].duplicate_group)]
            fitted = clone(model).fit(x.iloc[fit], y.iloc[fit])
            folds[source] = metrics(y.iloc[val], fitted.predict(x.iloc[val]))
        validation[name] = {"source_folds": folds,
                            "mean_source_rmsle": float(np.mean([f["rmsle"] for f in folds.values()]))}
    winner = min(validation, key=lambda name: validation[name]["mean_source_rmsle"])
    selected = models[winner].fit(x.iloc[train], y.iloc[train])
    radius = conformal_radius(y.iloc[calibration], selected.predict(x.iloc[calibration]))
    prediction = selected.predict(x.iloc[test])
    lower = np.maximum(0, np.expm1(np.log1p(prediction) - radius))
    upper = np.expm1(np.log1p(prediction) + radius)
    benchmark = models["median"].fit(x.iloc[train], y.iloc[train]).predict(x.iloc[test])
    results = data.iloc[test].copy()
    results["prediction_hours"], results["lower_hours"], results["upper_hours"] = prediction, lower, upper
    durations = []
    for _ in range(100):
        start = time.perf_counter()
        selected.predict(x.iloc[[test[0]]])
        durations.append((time.perf_counter() - start) * 1000)
    report = {
        "schema_version": 1, "seed": SEED, "sklearn_version": sklearn.__version__,
        "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "features": ["size_fp"], "target": "effort_hours", "selected_model": winner,
        "selection": "minimum equally weighted held-out-source RMSLE on training partition",
        "split_counts": {"train": len(train), "calibration": len(calibration), "test": len(test)},
        "validation": validation, "test": metrics(y.iloc[test], prediction),
        "median_baseline_test": metrics(y.iloc[test], benchmark),
        "test_by_source": {source: metrics(frame.effort_hours, frame.prediction_hours)
                           for source, frame in results.groupby("source")},
        "interval": {"nominal_coverage": 0.9, "log_radius": radius,
                     "test_coverage": float(np.mean((y.iloc[test] >= lower) & (y.iloc[test] <= upper))),
                     "median_width_hours": float(np.median(upper - lower))},
        "latency_p95_ms": float(np.percentile(durations, 95)),
        "production_approved": False,
        "promotion_blockers": ["Source licenses and measurement compatibility require verification",
                               "No modern prospective real-world validation",
                               "NLP-derived size differs from recorded completed-project size",
                               "Serving contract is 27 features; candidate uses size only"],
    }
    with (directory / "candidate.pkl").open("wb") as stream:
        pickle.dump(selected, stream, protocol=pickle.HIGHEST_PROTOCOL)
    results.to_csv(directory / "test_predictions.csv", index=False)
    split = data[["source", "project_id", "duplicate_group"]].copy()
    for name, indices in (("train", train), ("calibration", calibration), ("test", test)):
        split.loc[indices, "partition"] = name
    split.to_csv(directory / "splits.csv", index=False)
    (directory / "evaluation.json").write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("selected_model", "split_counts", "test",
                                            "median_baseline_test", "interval", "latency_p95_ms")}, indent=2))


if __name__ == "__main__":
    main()
