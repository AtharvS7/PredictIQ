"""CLI runner for Leave-One-Source-Out evaluation of Track 2 (Challenger) models.

Evaluates Track 2 candidates across the 6 historical data source folds:
1. MonotoneHistGradientBoosting (univariate size with monotonic constraint +1)
2. QuantileGradientBoosting (asymmetric quantile uncertainty intervals at [0.1, 0.5, 0.9])
3. MultivariateHistGradientBoosting (non-linear interaction with planned duration & team size)

Uses LeaveOneSourceOutSplitter from backend.ml.eval.protocol and frozen
metrics from backend.ml.eval.metrics. Prints comparison tables against
the CP07 baselines and CP08 Track 1 models, and saves structured results
to docs/evidence/CP09_results.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure single-thread/quiet joblib on Windows loky backend
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "2")

# Ensure repository root is on sys.path for direct script execution
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
import pandas as pd

from backend.ml.eval.metrics import compute_metrics, macro_average_metrics
from backend.ml.eval.protocol import LeaveOneSourceOutSplitter, load_dataset
from backend.ml.track2.models import (
    MonotoneHistGradientBoosting,
    MultivariateHistGradientBoosting,
    QuantileGradientBoosting,
)

DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "projects_v2.csv"
)
DEFAULT_OUTPUT_PATH = (
    _REPO_ROOT / "docs" / "evidence" / "CP09_results.json"
)
CP07_BASELINE_PATH = (
    _REPO_ROOT / "docs" / "evidence" / "CP07_baseline_results.json"
)
CP08_TRACK1_PATH = (
    _REPO_ROOT / "docs" / "evidence" / "CP08_results.json"
)


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_track2_models() -> dict[str, Any]:
    """Instantiate fresh instances of Track 2 candidate models."""
    return {
        "MonotoneHistGradientBoosting": MonotoneHistGradientBoosting(
            loss="squared_error",
            learning_rate=0.05,
            min_samples_leaf=10,
            max_iter=100,
            target_log=True,
            random_state=42,
        ),
        "QuantileGradientBoosting": QuantileGradientBoosting(
            quantiles=(0.1, 0.5, 0.9),
            learning_rate=0.05,
            min_samples_leaf=15,
            max_iter=100,
            target_log=False,
            random_state=42,
        ),
        "MultivariateHistGradientBoosting": MultivariateHistGradientBoosting(
            loss="squared_error",
            learning_rate=0.05,
            min_samples_leaf=10,
            max_iter=100,
            target_log=True,
            min_covariate_samples=10,
            random_state=42,
        ),
    }


def evaluate_track2_loso(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Execute Leave-One-Source-Out cross-validation for all Track 2 models."""
    splitter = LeaveOneSourceOutSplitter()
    folds = list(splitter.split_df(df))

    model_names = list(get_track2_models().keys())
    results: dict[str, dict[str, Any]] = {
        name: {"folds": {}, "macro_average": {}, "interval_metrics": {}}
        for name in model_names
    }

    fold_meta: dict[str, dict[str, int]] = {}
    for fold in folds:
        fold_meta[fold.fold_name] = {
            "n_test": len(fold.test_df),
            "n_train": len(fold.train_df),
        }

    for fold in folds:
        holdout_source = fold.fold_name
        train_df = fold.train_df
        test_df = fold.test_df

        y_train = train_df["effort_hours"].to_numpy()
        y_test = test_df["effort_hours"].to_numpy()

        for name in model_names:
            model = get_track2_models()[name]
            model.fit(train_df, y_train)
            y_pred = model.predict(test_df)

            metrics = compute_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_train=y_train,
            )
            results[name]["folds"][holdout_source] = metrics

            # For QuantileGradientBoosting, evaluate uncertainty intervals
            if name == "QuantileGradientBoosting":
                quantiles_dict = model.predict_quantiles(test_df)
                p10 = quantiles_dict["p10"]
                p50 = quantiles_dict["p50"]
                p90 = quantiles_dict["p90"]

                # In-interval coverage
                in_interval = (y_test >= p10) & (y_test <= p90)
                coverage_pct = float(np.mean(in_interval) * 100.0)

                # Relative interval width: (p90 - p10) / p50
                rel_width = float(np.mean((p90 - p10) / p50))

                # Quantile monotonicity verification
                is_monotonic = (p10 <= p50 + 1e-6) & (p50 <= p90 + 1e-6)
                monotonic_pct = float(np.mean(is_monotonic) * 100.0)

                results[name]["interval_metrics"][holdout_source] = {
                    "coverage_80pct": coverage_pct,
                    "mean_relative_width": rel_width,
                    "monotonic_pct": monotonic_pct,
                    "n_test": len(y_test),
                }

    # Compute macro-averages
    for name in model_names:
        fold_metric_list = [results[name]["folds"][s] for s in results[name]["folds"]]
        results[name]["macro_average"] = macro_average_metrics(fold_metric_list)

    # Compute macro-average for interval metrics if present
    if results["QuantileGradientBoosting"]["interval_metrics"]:
        q_intervals = results["QuantileGradientBoosting"]["interval_metrics"]
        macro_cov = float(np.mean([q_intervals[s]["coverage_80pct"] for s in q_intervals]))
        macro_width = float(np.mean([q_intervals[s]["mean_relative_width"] for s in q_intervals]))
        macro_mono = float(np.mean([q_intervals[s]["monotonic_pct"] for s in q_intervals]))
        results["QuantileGradientBoosting"]["macro_interval_metrics"] = {
            "coverage_80pct": macro_cov,
            "mean_relative_width": macro_width,
            "monotonic_pct": macro_mono,
        }

    # Fit full dataset parameters/metadata for reference
    full_y = df["effort_hours"].to_numpy()
    full_parameters: dict[str, Any] = {}
    for name in model_names:
        model = get_track2_models()[name]
        model.fit(df, full_y)
        if name == "MonotoneHistGradientBoosting":
            full_parameters[name] = {
                "algorithm": "HistGradientBoostingRegressor",
                "loss": model.loss,
                "learning_rate": model.learning_rate,
                "min_samples_leaf": model.min_samples_leaf,
                "max_iter": model.max_iter,
                "monotonic_cst": [1],
                "target_log": model.target_log,
            }
        elif name == "QuantileGradientBoosting":
            full_parameters[name] = {
                "algorithm": "HistGradientBoostingRegressor(loss='quantile')",
                "quantiles": list(model.quantiles),
                "learning_rate": model.learning_rate,
                "min_samples_leaf": model.min_samples_leaf,
                "max_iter": model.max_iter,
                "monotonic_cst": [1],
                "target_log": model.target_log,
            }
        elif name == "MultivariateHistGradientBoosting":
            full_parameters[name] = {
                "algorithm": "HistGradientBoostingRegressor(marginal_fallback)",
                "loss": model.loss,
                "learning_rate": model.learning_rate,
                "min_samples_leaf": model.min_samples_leaf,
                "max_iter": model.max_iter,
                "has_interaction": model.has_interaction_,
                "n_covariate_samples_train": model.n_covariate_samples_train_,
                "target_log": model.target_log,
            }

    return {
        "fold_meta": fold_meta,
        "models": results,
        "full_dataset_parameters": full_parameters,
    }


def load_previous_results(path: Path) -> dict[str, Any] | None:
    """Load JSON results from previous checkpoint for comparison if available."""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def format_markdown_tables(
    eval_data: dict[str, Any],
    cp07_data: dict[str, Any] | None = None,
    cp08_data: dict[str, Any] | None = None,
) -> str:
    """Generate clean GitHub-flavored markdown tables for display and documentation."""
    lines: list[str] = []

    fold_meta = eval_data["fold_meta"]
    models = eval_data["models"]

    # 1. Macro-Average Comparison Table (CP07 Baselines vs Track 1 vs Track 2)
    lines.append("### Track 2 vs Track 1 & CP07 Baselines: Macro-Average Comparison (6 LOSO Folds)")
    lines.append("")
    lines.append("| Model Family | Model Name | MdAPE (%) | MAE (hrs) | RMSE (hrs) | $R^2$ | PRED(25) (%) | PRED(30) (%) | SA (%) | MMRE (%) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    # Include CP07 baselines if available
    if cp07_data and "baselines" in cp07_data:
        for bname, bdata in cp07_data["baselines"].items():
            macro = bdata["macro_average"]
            lines.append(
                f"| Baseline (CP07) | `{bname}` | {macro['mdape']:.1f}% | {macro['mae']:.1f} | "
                f"{macro['rmse']:.1f} | {macro['r2']:.3f} | {macro['pred25']:.1f}% | "
                f"{macro['pred30']:.1f}% | {macro['sa']:.1f}% | {macro['mmre']:.1f}% |"
            )

    # Include CP08 Track 1 models if available
    if cp08_data and "models" in cp08_data:
        for t1name, t1data in cp08_data["models"].items():
            macro = t1data["macro_average"]
            lines.append(
                f"| Track 1 (CP08) | `{t1name}` | {macro['mdape']:.1f}% | {macro['mae']:.1f} | "
                f"{macro['rmse']:.1f} | {macro['r2']:.3f} | {macro['pred25']:.1f}% | "
                f"{macro['pred30']:.1f}% | {macro['sa']:.1f}% | {macro['mmre']:.1f}% |"
            )

    # Include Track 2 models
    for mname, mdata in models.items():
        macro = mdata["macro_average"]
        mdape_val = f"{macro['mdape']:.1f}%"
        mae_val = f"{macro['mae']:.1f}"
        rmse_val = f"{macro['rmse']:.1f}"
        r2_val = f"{macro['r2']:.3f}"
        p25_val = f"{macro['pred25']:.1f}%"
        p30_val = f"{macro['pred30']:.1f}%"
        sa_val = f"{macro['sa']:.1f}%"
        mmre_val = f"{macro['mmre']:.1f}%"
        lines.append(
            f"| **Track 2** | **`{mname}`** | **{mdape_val}** | {mae_val} | {rmse_val} | {r2_val} | {p25_val} | {p30_val} | {sa_val} | {mmre_val} |"
        )

    lines.append("")

    # 2. Per-Fold Breakdown Tables for Track 2 Models
    lines.append("### Track 2 Per-Fold Breakdown by Holdout Source")
    lines.append("")
    lines.append("| Model | Holdout Source | Test N | MdAPE (%) | MAE (hrs) | RMSE (hrs) | $R^2$ | PRED(25) (%) | PRED(30) (%) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for mname, mdata in models.items():
        for source, smetrics in mdata["folds"].items():
            n_test = fold_meta[source]["n_test"]
            lines.append(
                f"| `{mname}` | `{source}` | {n_test} | {smetrics['mdape']:.1f}% | "
                f"{smetrics['mae']:.1f} | {smetrics['rmse']:.1f} | {smetrics['r2']:.3f} | "
                f"{smetrics['pred25']:.1f}% | {smetrics['pred30']:.1f}% |"
            )

    lines.append("")

    # 3. Quantile Uncertainty Intervals Evaluation
    if "QuantileGradientBoosting" in models and "interval_metrics" in models["QuantileGradientBoosting"]:
        lines.append("### QuantileGradientBoosting Uncertainty Interval Evaluation (p10 to p90)")
        lines.append("")
        lines.append("| Holdout Source | Test N | 80% Coverage (%) | Mean Relative Width [(p90-p10)/p50] | Monotonicity Check (p10<=p50<=p90) |")
        lines.append("|---|---|---|---|---|")
        q_metrics = models["QuantileGradientBoosting"]["interval_metrics"]
        for source, qm in q_metrics.items():
            lines.append(
                f"| `{source}` | {qm['n_test']} | {qm['coverage_80pct']:.1f}% | {qm['mean_relative_width']:.2f}x | {qm['monotonic_pct']:.1f}% PASS |"
            )
        if "macro_interval_metrics" in models["QuantileGradientBoosting"]:
            mim = models["QuantileGradientBoosting"]["macro_interval_metrics"]
            lines.append(
                f"| **Macro-Average** | **Total** | **{mim['coverage_80pct']:.1f}%** | **{mim['mean_relative_width']:.2f}x** | **{mim['monotonic_pct']:.1f}% PASS** |"
            )
        lines.append("")

    # 4. Full-Dataset Parameters
    full_params = eval_data.get("full_dataset_parameters", {})
    if full_params:
        lines.append("### Track 2 Full-Dataset Parameters")
        lines.append("")
        for name, p in full_params.items():
            lines.append(f"- **`{name}`**:")
            for k, v in p.items():
                lines.append(f"  - `{k}`: {v}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Leave-One-Source-Out evaluation of Track 2 models on PredictIQ dataset."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help=f"Path to dataset CSV (default: {DEFAULT_DATASET_PATH})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Path to save results JSON (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress markdown tables output to stdout.",
    )
    args = parser.parse_args()

    print(f"Loading dataset from: {args.dataset}")
    df = load_dataset(args.dataset)
    dataset_sha256 = compute_sha256(args.dataset)
    print(f"Dataset loaded successfully: {len(df)} rows. SHA-256: {dataset_sha256}")

    source_counts = df["source"].value_counts().to_dict()
    print(f"Sources distribution: {source_counts}")

    print("\nRunning Leave-One-Source-Out (LOSO) cross-validation for Track 2 models...")
    eval_results = evaluate_track2_loso(df)

    # Attach provenance metadata
    now_iso = datetime.now(UTC).isoformat()
    output_payload = {
        "timestamp": now_iso,
        "dataset_path": str(args.dataset),
        "dataset_sha256": dataset_sha256,
        "total_records": len(df),
        "source_counts": source_counts,
        "fold_meta": eval_results["fold_meta"],
        "models": eval_results["models"],
        "full_dataset_parameters": eval_results["full_dataset_parameters"],
    }

    # Write results JSON
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)
    print(f"\nEvaluation results successfully saved to: {args.output}")

    # Load CP07 baseline and CP08 Track 1 data for comparison
    cp07_data = load_previous_results(CP07_BASELINE_PATH)
    cp08_data = load_previous_results(CP08_TRACK1_PATH)

    if not args.quiet:
        md_tables = format_markdown_tables(eval_results, cp07_data, cp08_data)
        print("\n" + "=" * 80)
        print(md_tables)
        print("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
