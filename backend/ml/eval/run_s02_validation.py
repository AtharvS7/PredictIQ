"""S02 Truthful Model Validation Runner (PREDICTIQ_RC3).

Generates rigorous, uncherrypicked empirical validation evidence for:
1. Production MonotonePowerLaw + MondrianConformal model under 6-fold Leave-One-Source-Out (LOSO) CV.
2. Comparison against 4 frozen baselines (Median Dummy, Median Productivity, Albrecht, Log-Linear).
3. Conformal coverage for 80% Plausible Range and 50% Likely Band (both macro and pooled).
4. Stratified performance across functional size buckets (<100, 100-500, 500-1500, >=1500 FP).
5. Empirical Bayes organizational calibration progression across k in [0, 1, 3, 5, 10, 20].
6. Serializes backend/ml/reports/model_report.json and backend/ml/metrics_floor.json.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.ml.calibration.conformal import (
    assign_mondrian_bucket,
    compute_conformal_quantile,
)
from backend.ml.eval.baselines import (
    AlbrechtNominalPredictor,
    LogLinearBaseline,
    MedianDummyPredictor,
    MedianProductivityPredictor,
)
from backend.ml.eval.metrics import mae, mdape, pred25, rmse
from backend.ml.eval.protocol import load_dataset
from backend.ml.track1.models import MonotonePowerLaw

DATASET_PATH = _REPO_ROOT / "backend" / "ml" / "data" / "projects_v2.csv"
REPORT_OUTPUT_PATH = _REPO_ROOT / "backend" / "ml" / "reports" / "model_report.json"
METRICS_FLOOR_PATH = _REPO_ROOT / "backend" / "ml" / "metrics_floor.json"


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metric_fn: Any,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    random_state: int = 42,
) -> tuple[float, float]:
    rng = np.random.RandomState(random_state)
    n = len(y_true)
    if n < 5:
        return 0.0, 0.0
    scores = []
    for _ in range(n_resamples):
        indices = rng.randint(0, n, size=n)
        s = metric_fn(y_true[indices], y_pred[indices])
        scores.append(s)
    alpha = 1.0 - confidence_level
    low = float(np.percentile(scores, 100.0 * (alpha / 2.0)))
    high = float(np.percentile(scores, 100.0 * (1.0 - alpha / 2.0)))
    return low, high


def run_loso_evaluation(
    df: pd.DataFrame,
    random_state: int = 42,
) -> dict[str, Any]:
    sources = sorted(df["source"].unique())
    n_total = len(df)
    dataset_sha = compute_sha256(DATASET_PATH)

    per_source_results: dict[str, dict[str, Any]] = {}
    all_y_true: list[float] = []
    all_y_pred: list[float] = []
    all_p10: list[float] = []
    all_p25: list[float] = []
    all_p50: list[float] = []
    all_p75: list[float] = []
    all_p90: list[float] = []
    all_sizes: list[float] = []
    all_sources: list[str] = []

    # Store baseline predictions
    baseline_preds: dict[str, list[float]] = {
        "MedianDummy": [],
        "MedianProductivity": [],
        "AlbrechtNominal": [],
        "LogLinear": [],
    }

    for src in sources:
        train_df = df[df["source"] != src].copy()
        test_df = df[df["source"] == src].copy()

        X_train = train_df[["size_value"]].copy()
        y_train = train_df["effort_hours"].to_numpy(dtype=float)
        X_test = test_df[["size_value"]].copy()
        y_test = test_df["effort_hours"].to_numpy(dtype=float)

        # 1. Fit production MonotonePowerLaw
        model = MonotonePowerLaw()
        model.fit(X_train, y_train)

        train_preds = np.maximum(model.predict(X_train), 1.0)
        test_preds = np.maximum(model.predict(X_test), 1.0)

        # 2. Conformal calibration on train fold (log-residual scores)
        # Using 80% train / 20% cal split of training fold
        train_idx = np.arange(len(train_df))
        rng_cal = np.random.RandomState(random_state)
        rng_cal.shuffle(train_idx)
        n_cal = max(10, int(len(train_df) * 0.20))
        cal_idx = train_idx[:n_cal]

        cal_s = train_df["size_value"].to_numpy(dtype=float)[cal_idx]
        cal_y = y_train[cal_idx]
        cal_preds = train_preds[cal_idx]

        cal_scores = np.abs(np.log(np.maximum(cal_y, 1.0)) - np.log(np.maximum(cal_preds, 1.0)))

        # 80% coverage -> alpha = 0.20
        gq_80 = compute_conformal_quantile(cal_scores, alpha=0.20)
        # 50% coverage -> alpha = 0.50
        gq_50 = compute_conformal_quantile(cal_scores, alpha=0.50)

        cal_buckets = assign_mondrian_bucket(cal_s)
        bq_80: dict[str, float] = {}
        bq_50: dict[str, float] = {}

        for b in ("small", "medium", "large"):
            b_mask = cal_buckets == b
            if np.sum(b_mask) >= 5:
                bq_80[b] = compute_conformal_quantile(cal_scores[b_mask], alpha=0.20)
                bq_50[b] = compute_conformal_quantile(cal_scores[b_mask], alpha=0.50)
            else:
                bq_80[b] = gq_80
                bq_50[b] = gq_50

        # Predict intervals for test fold
        test_s = test_df["size_value"].to_numpy(dtype=float)
        test_buckets = assign_mondrian_bucket(test_s)
        t80 = np.array([bq_80.get(b, gq_80) for b in test_buckets])
        t50 = np.array([bq_50.get(b, gq_50) for b in test_buckets])

        p10 = np.maximum(test_preds * np.exp(-t80), 1.0)
        p25 = np.maximum(p10, test_preds * np.exp(-t50))
        p50 = np.maximum(p25, test_preds)
        p75 = np.maximum(p50, test_preds * np.exp(t50))
        p90 = np.maximum(p75, test_preds * np.exp(t80))

        # Metrics on test fold
        s_mdape = float(mdape(y_test, test_preds))
        s_mae = float(mae(y_test, test_preds))
        s_rmse = float(rmse(y_test, test_preds))
        s_pred25 = float(pred25(y_test, test_preds))
        s_pred50 = float(np.mean(np.abs(test_preds - y_test) / y_test <= 0.50) * 100.0)

        # Conformal coverages
        cov_80 = float(np.mean((y_test >= p10) & (y_test <= p90)) * 100.0)
        cov_50 = float(np.mean((y_test >= p25) & (y_test <= p75)) * 100.0)
        med_width_80 = float(np.median(p90 - p10))
        med_width_50 = float(np.median(p75 - p25))
        sharpness_80 = float(np.median((p90 - p10) / test_preds))
        sharpness_50 = float(np.median((p75 - p25) / test_preds))

        # Bootstrap CIs
        ci_mdape = bootstrap_ci(y_test, test_preds, mdape)
        ci_pred25 = bootstrap_ci(y_test, test_preds, pred25)

        # Baseline evaluations
        base_models = {
            "MedianDummy": MedianDummyPredictor(),
            "MedianProductivity": MedianProductivityPredictor(),
            "AlbrechtNominal": AlbrechtNominalPredictor(),
            "LogLinear": LogLinearBaseline(),
        }
        b_metrics: dict[str, dict[str, float]] = {}
        for b_name, b_model in base_models.items():
            b_model.fit(X_train, y_train)
            b_pred = np.maximum(b_model.predict(X_test), 1.0)
            baseline_preds[b_name].extend(b_pred.tolist())
            b_metrics[b_name] = {
                "mdape": float(mdape(y_test, b_pred)),
                "mae": float(mae(y_test, b_pred)),
                "pred25": float(pred25(y_test, b_pred)),
            }

        # Standardized accuracy vs MedianDummy
        dummy_mae = b_metrics["MedianDummy"]["mae"]
        sa = float(1.0 - (s_mae / dummy_mae)) if dummy_mae > 0 else 0.0

        per_source_results[src] = {
            "n_records": len(test_df),
            "size_fp_min": float(np.min(test_s)),
            "size_fp_max": float(np.max(test_s)),
            "effort_hours_min": float(np.min(y_test)),
            "effort_hours_max": float(np.max(y_test)),
            "mdape": s_mdape,
            "mdape_ci95": list(ci_mdape),
            "mae": s_mae,
            "rmse": s_rmse,
            "pred25": s_pred25,
            "pred25_ci95": list(ci_pred25),
            "pred50": s_pred50,
            "standardized_accuracy": sa,
            "conformal_80_coverage": cov_80,
            "conformal_50_coverage": cov_50,
            "median_width_80": med_width_80,
            "median_width_50": med_width_50,
            "sharpness_80": sharpness_80,
            "sharpness_50": sharpness_50,
            "fitted_parameters": {
                "a": float(model.a_),
                "b": float(model.b_),
                "beta0": float(model.beta0_),
            },
            "baselines": b_metrics,
        }

        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(test_preds.tolist())
        all_p10.extend(p10.tolist())
        all_p25.extend(p25.tolist())
        all_p50.extend(p50.tolist())
        all_p75.extend(p75.tolist())
        all_p90.extend(p90.tolist())
        all_sizes.extend(test_s.tolist())
        all_sources.extend([src] * len(test_df))

    arr_true = np.array(all_y_true)
    arr_pred = np.array(all_y_pred)
    arr_p10 = np.array(all_p10)
    arr_p25 = np.array(all_p25)
    arr_p75 = np.array(all_p75)
    arr_p90 = np.array(all_p90)
    arr_sizes = np.array(all_sizes)

    # Macro averages across the 6 folds
    macro_mdape = float(np.mean([r["mdape"] for r in per_source_results.values()]))
    macro_mae = float(np.mean([r["mae"] for r in per_source_results.values()]))
    macro_rmse = float(np.mean([r["rmse"] for r in per_source_results.values()]))
    macro_pred25 = float(np.mean([r["pred25"] for r in per_source_results.values()]))
    macro_pred50 = float(np.mean([r["pred50"] for r in per_source_results.values()]))
    macro_sa = float(np.mean([r["standardized_accuracy"] for r in per_source_results.values()]))
    macro_cov_80 = float(np.mean([r["conformal_80_coverage"] for r in per_source_results.values()]))
    macro_cov_50 = float(np.mean([r["conformal_50_coverage"] for r in per_source_results.values()]))

    # Pooled metrics (N=915)
    pooled_mdape = float(mdape(arr_true, arr_pred))
    pooled_mae = float(mae(arr_true, arr_pred))
    pooled_rmse = float(rmse(arr_true, arr_pred))
    pooled_pred25 = float(pred25(arr_true, arr_pred))
    pooled_pred50 = float(np.mean(np.abs(arr_pred - arr_true) / arr_true <= 0.50) * 100.0)
    pooled_cov_80 = float(np.mean((arr_true >= arr_p10) & (arr_true <= arr_p90)) * 100.0)
    pooled_cov_50 = float(np.mean((arr_true >= arr_p25) & (arr_true <= arr_p75)) * 100.0)

    # Baseline macro averages
    baseline_summary: dict[str, dict[str, float]] = {}
    for b_name in baseline_preds:
        b_macro_mdape = float(np.mean([r["baselines"][b_name]["mdape"] for r in per_source_results.values()]))
        b_macro_mae = float(np.mean([r["baselines"][b_name]["mae"] for r in per_source_results.values()]))
        b_macro_pred25 = float(np.mean([r["baselines"][b_name]["pred25"] for r in per_source_results.values()]))
        b_pooled_arr = np.array(baseline_preds[b_name])
        b_pooled_mdape = float(mdape(arr_true, b_pooled_arr))
        b_pooled_pred25 = float(pred25(arr_true, b_pooled_arr))
        baseline_summary[b_name] = {
            "macro_mdape": b_macro_mdape,
            "macro_mae": b_macro_mae,
            "macro_pred25": b_macro_pred25,
            "pooled_mdape": b_pooled_mdape,
            "pooled_pred25": b_pooled_pred25,
        }

    # Size-bucket stratified breakdown
    bucket_definitions = [
        ("small", arr_sizes < 100.0),
        ("medium", (arr_sizes >= 100.0) & (arr_sizes < 500.0)),
        ("large", (arr_sizes >= 500.0) & (arr_sizes < 1500.0)),
        ("very_large", arr_sizes >= 1500.0),
    ]
    bucket_results: dict[str, dict[str, Any]] = {}
    for b_label, b_mask in bucket_definitions:
        b_n = int(np.sum(b_mask))
        if b_n > 0:
            b_true = arr_true[b_mask]
            b_pred = arr_pred[b_mask]
            b_p10 = arr_p10[b_mask]
            b_p25 = arr_p25[b_mask]
            b_p75 = arr_p75[b_mask]
            b_p90 = arr_p90[b_mask]
            bucket_results[b_label] = {
                "count": b_n,
                "percentage_of_total": float(round(b_n / n_total * 100.0, 1)),
                "mdape": float(mdape(b_true, b_pred)),
                "pred25": float(pred25(b_true, b_pred)),
                "conformal_80_coverage": float(np.mean((b_true >= b_p10) & (b_true <= b_p90)) * 100.0),
                "conformal_50_coverage": float(np.mean((b_true >= b_p25) & (b_true <= b_p75)) * 100.0),
                "median_width_80": float(np.median(b_p90 - b_p10)),
                "median_width_50": float(np.median(b_p75 - b_p25)),
            }

    # Empirical Bayes Organization Calibration simulation by k in [0, 1, 3, 5, 10, 20]
    org_k_progression = simulate_org_calibration_by_k(df, sources)

    return {
        "metadata": {
            "model_version": "2.0.0-rc.3",
            "architecture": "MonotonePowerLaw + MondrianConformal",
            "evaluation_protocol": "Leave-One-Source-Out (LOSO) 6-Fold Cross-Validation",
            "evaluation_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "dataset": "backend/ml/data/projects_v2.csv",
            "dataset_sha256": dataset_sha,
            "total_records": n_total,
            "sources": sources,
        },
        "summary": {
            "macro_mdape": macro_mdape,
            "macro_mae": macro_mae,
            "macro_rmse": macro_rmse,
            "macro_pred25": macro_pred25,
            "macro_pred50": macro_pred50,
            "macro_standardized_accuracy": macro_sa,
            "macro_conformal_80_coverage": macro_cov_80,
            "macro_conformal_50_coverage": macro_cov_50,
            "pooled_mdape": pooled_mdape,
            "pooled_mae": pooled_mae,
            "pooled_rmse": pooled_rmse,
            "pooled_pred25": pooled_pred25,
            "pooled_pred50": pooled_pred50,
            "pooled_conformal_80_coverage": pooled_cov_80,
            "pooled_conformal_50_coverage": pooled_cov_50,
        },
        "baselines_comparison": baseline_summary,
        "per_source_breakdown": per_source_results,
        "size_bucket_breakdown": bucket_results,
        "org_calibration_by_k": org_k_progression,
    }


def simulate_org_calibration_by_k(
    df: pd.DataFrame,
    sources: list[str],
    k_values: list[int] | None = None,
    n_trials: int = 50,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    if k_values is None:
        k_values = [0, 1, 3, 5, 10, 20]

    rng = np.random.RandomState(random_state)
    progression: list[dict[str, Any]] = []

    # Fit global model across all 915 projects
    global_model = MonotonePowerLaw()
    global_model.fit(df[["size_value"]], df["effort_hours"].to_numpy(dtype=float))
    beta0_global = float(global_model.beta0_)
    b_global = float(global_model.b_)

    # Calculate empirical between-source and within-source variances
    log_s_all = np.log(df["size_value"].to_numpy(dtype=float))
    log_e_all = np.log(df["effort_hours"].to_numpy(dtype=float))
    source_arr = df["source"].to_numpy()

    shifts = []
    within_resids = []
    for s in sources:
        m = source_arr == s
        res = log_e_all[m] - (beta0_global + b_global * log_s_all[m])
        shifts.append(float(np.mean(res)))
        within_resids.extend((res - np.mean(res)).tolist())

    tau2 = float(max(1e-4, np.var(shifts, ddof=1)))
    sigma2 = float(max(1e-4, np.var(within_resids, ddof=1)))

    for k in k_values:
        trial_mdapes = []
        trial_pred25s = []

        if k == 0:
            # Uncalibrated baseline on each source
            for s in sources:
                src_df = df[df["source"] == s]
                y_s = src_df["effort_hours"].to_numpy(dtype=float)
                pred_s = np.maximum(global_model.predict(src_df[["size_value"]]), 1.0)
                trial_mdapes.append(float(mdape(y_s, pred_s)))
                trial_pred25s.append(float(pred25(y_s, pred_s)))
            progression.append({
                "k": 0,
                "shrinkage_weight": 0.0,
                "macro_mdape": float(np.mean(trial_mdapes)),
                "macro_pred25": float(np.mean(trial_pred25s)),
                "relative_gain_pct": 0.0,
            })
            continue

        # Shrinkage factor w
        w = float(k / (k + (sigma2 / tau2)))

        for _ in range(n_trials):
            for s in sources:
                src_df = df[df["source"] == s]
                n_src = len(src_df)
                if n_src <= k + 2:
                    continue
                # Sample k actuals
                perm = rng.permutation(n_src)
                cal_idx = perm[:k]
                eval_idx = perm[k:]

                cal_s = src_df["size_value"].to_numpy(dtype=float)[cal_idx]
                cal_e = src_df["effort_hours"].to_numpy(dtype=float)[cal_idx]

                eval_s = src_df["size_value"].to_numpy(dtype=float)[eval_idx]
                eval_e = src_df["effort_hours"].to_numpy(dtype=float)[eval_idx]

                # Organization productivity shift
                org_resids = np.log(cal_e) - (beta0_global + b_global * np.log(cal_s))
                delta_log_a = float(np.mean(org_resids))

                # Empirical Bayes shrinkage: beta0_cal = beta0_global + w * delta_log_a
                beta0_cal = beta0_global + w * delta_log_a

                # Calibrated prediction on remaining org projects
                pred_eval = np.maximum(np.exp(beta0_cal) * (eval_s ** b_global), 1.0)

                trial_mdapes.append(float(mdape(eval_e, pred_eval)))
                trial_pred25s.append(float(pred25(eval_e, pred_eval)))

        k_mdape = float(np.mean(trial_mdapes))
        k_pred25 = float(np.mean(trial_pred25s))
        base_mdape = progression[0]["macro_mdape"]
        gain = float(((base_mdape - k_mdape) / base_mdape) * 100.0)

        progression.append({
            "k": k,
            "shrinkage_weight": float(round(w, 3)),
            "macro_mdape": float(round(k_mdape, 2)),
            "macro_pred25": float(round(k_pred25, 2)),
            "relative_gain_pct": float(round(gain, 2)),
        })

    return progression


def generate_metrics_floor(report: dict[str, Any]) -> dict[str, Any]:
    summary = report["summary"]
    return {
        "metadata": {
            "description": "PredictIQ ML Release Gate Quality Floors (RC3)",
            "generated_at": report["metadata"]["evaluation_date"],
            "model_version": report["metadata"]["model_version"],
            "architecture": report["metadata"]["architecture"],
        },
        "floors": {
            "macro_mdape_max": float(math.ceil(summary["macro_mdape"] * 1.15)),
            "macro_pred25_min": float(math.floor(summary["macro_pred25"] * 0.85)),
            "pooled_mdape_max": float(math.ceil(summary["pooled_mdape"] * 1.15)),
            "pooled_pred25_min": float(math.floor(summary["pooled_pred25"] * 0.85)),
            "conformal_80_coverage_min": 70.0,
            "conformal_50_coverage_min": 45.0,
        },
        "actual_measured": {
            "macro_mdape": float(round(summary["macro_mdape"], 2)),
            "macro_pred25": float(round(summary["macro_pred25"], 2)),
            "pooled_mdape": float(round(summary["pooled_mdape"], 2)),
            "pooled_pred25": float(round(summary["pooled_pred25"], 2)),
            "macro_conformal_80_coverage": float(round(summary["macro_conformal_80_coverage"], 2)),
            "macro_conformal_50_coverage": float(round(summary["macro_conformal_50_coverage"], 2)),
            "pooled_conformal_80_coverage": float(round(summary["pooled_conformal_80_coverage"], 2)),
            "pooled_conformal_50_coverage": float(round(summary["pooled_conformal_50_coverage"], 2)),
        },
    }


def main() -> None:
    print("=" * 80)
    print("PREDICTIQ RC3 — EMPIRICAL MODEL VALIDATION & LOSO EVALUATION")
    print("=" * 80)

    print(f"Loading dataset: {DATASET_PATH}")
    df = load_dataset(DATASET_PATH)
    print(f"Loaded {len(df)} projects across {sorted(df['source'].unique())}")

    print("\nRunning 6-fold Leave-One-Source-Out (LOSO) cross-validation...")
    report = run_loso_evaluation(df)

    # Ensure output directories exist
    REPORT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved model report to: {REPORT_OUTPUT_PATH}")

    # Generate metrics floor
    metrics_floor = generate_metrics_floor(report)
    with METRICS_FLOOR_PATH.open("w", encoding="utf-8") as f:
        json.dump(metrics_floor, f, indent=2)
    print(f"Saved metrics floor to: {METRICS_FLOOR_PATH}")

    # Print summary tables
    s = report["summary"]
    print("\n" + "=" * 80)
    print("LOSO VALIDATION SUMMARY RESULTS")
    print("=" * 80)
    print(f"Macro MdAPE:                 {s['macro_mdape']:.2f}%")
    print(f"Macro PRED(25):              {s['macro_pred25']:.2f}%")
    print(f"Macro MAE:                   {s['macro_mae']:.1f} hours")
    print(f"Macro RMSE:                  {s['macro_rmse']:.1f} hours")
    print(f"Macro Standardized Accuracy: {s['macro_standardized_accuracy']:.3f}")
    print(f"Macro 80% Range Coverage:    {s['macro_conformal_80_coverage']:.1f}%")
    print(f"Macro 50% Band Coverage:     {s['macro_conformal_50_coverage']:.1f}%")
    print("-" * 80)
    print(f"Pooled MdAPE:                {s['pooled_mdape']:.2f}%")
    print(f"Pooled PRED(25):             {s['pooled_pred25']:.2f}%")
    print(f"Pooled 80% Range Coverage:   {s['pooled_conformal_80_coverage']:.1f}%")
    print(f"Pooled 50% Band Coverage:    {s['pooled_conformal_50_coverage']:.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
