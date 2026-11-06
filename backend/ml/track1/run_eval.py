"""CLI runner for Leave-One-Source-Out evaluation of Track 1 models.

Evaluates Track 1 candidates across the 6 historical data source folds:
1. MonotonePowerLaw
2. MultivariateMonotoneModel
3. SegmentedMonotoneModel

Uses LeaveOneSourceOutSplitter from backend.ml.eval.protocol and frozen
metrics from backend.ml.eval.metrics. Prints comparison tables against
the CP07 baselines and saves structured results to docs/evidence/CP08_results.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure repository root is on sys.path for direct script execution
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd

from backend.ml.eval.metrics import compute_metrics, macro_average_metrics
from backend.ml.eval.protocol import LeaveOneSourceOutSplitter, load_dataset
from backend.ml.track1.models import (
    MonotonePowerLaw,
    MultivariateMonotoneModel,
    SegmentedMonotoneModel,
)

DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "projects_v2.csv"
)
DEFAULT_OUTPUT_PATH = (
    _REPO_ROOT / "docs" / "evidence" / "CP08_results.json"
)
CP07_BASELINE_PATH = (
    _REPO_ROOT / "docs" / "evidence" / "CP07_baseline_results.json"
)


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_track1_models() -> dict[str, Any]:
    """Instantiate fresh instances of Track 1 candidate models."""
    return {
        "MonotonePowerLaw": MonotonePowerLaw(),
        "MultivariateMonotoneModel": MultivariateMonotoneModel(),
        "SegmentedMonotoneModel": SegmentedMonotoneModel(),
    }


def evaluate_track1_loso(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Execute Leave-One-Source-Out cross-validation for all Track 1 models."""
    splitter = LeaveOneSourceOutSplitter()
    folds = list(splitter.split_df(df))

    model_names = list(get_track1_models().keys())
    results: dict[str, dict[str, Any]] = {
        name: {"folds": {}, "macro_average": {}, "fold_parameters": {}}
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
            model = get_track1_models()[name]
            model.fit(train_df, y_train)
            y_pred = model.predict(test_df)

            metrics = compute_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_train=y_train,
            )
            results[name]["folds"][holdout_source] = metrics

            # Record fold parameter estimates
            if name == "MonotonePowerLaw":
                results[name]["fold_parameters"][holdout_source] = {
                    "a": float(model.a_),
                    "b": float(model.b_),
                    "beta0": float(model.beta0_),
                }
            elif name == "MultivariateMonotoneModel":
                results[name]["fold_parameters"][holdout_source] = {
                    "a_base": float(model.a_base_),
                    "b_base": float(model.b_base_),
                    "has_duration": bool(model.has_duration_),
                    "a": float(model.a_) if model.a_ is not None else None,
                    "b": float(model.b_) if model.b_ is not None else None,
                    "c": float(model.c_) if model.c_ is not None else None,
                }
            elif name == "SegmentedMonotoneModel":
                results[name]["fold_parameters"][holdout_source] = {
                    "beta0": float(model.beta0_),
                    "b1": float(model.b1_),
                    "b2": float(model.b2_),
                    "b3": float(model.b3_),
                }

    # Compute macro-averages
    for name in model_names:
        fold_metric_list = [results[name]["folds"][s] for s in results[name]["folds"]]
        results[name]["macro_average"] = macro_average_metrics(fold_metric_list)

    # Fit full dataset parameters for reference
    full_y = df["effort_hours"].to_numpy()
    full_parameters: dict[str, Any] = {}
    for name in model_names:
        model = get_track1_models()[name]
        model.fit(df, full_y)
        if name == "MonotonePowerLaw":
            full_parameters[name] = {
                "equation": "E = a * S^b",
                "a": float(model.a_),
                "b": float(model.b_),
                "beta0": float(model.beta0_),
            }
        elif name == "MultivariateMonotoneModel":
            full_parameters[name] = {
                "equation_multi": "E = a * S^b * D^c",
                "equation_base": "E = a_base * S^b_base",
                "a": float(model.a_),
                "b": float(model.b_),
                "c": float(model.c_),
                "a_base": float(model.a_base_),
                "b_base": float(model.b_base_),
            }
        elif name == "SegmentedMonotoneModel":
            full_parameters[name] = {
                "equation": "ln(E) = beta0 + b1*phi1(x) + b2*phi2(x) + b3*phi3(x)",
                "bucket_cuts": [150.0, 750.0],
                "tau": 0.25,
                "beta0": float(model.beta0_),
                "b1_small": float(model.b1_),
                "b2_medium": float(model.b2_),
                "b3_large": float(model.b3_),
            }

    return {
        "fold_meta": fold_meta,
        "models": results,
        "full_dataset_parameters": full_parameters,
    }


def load_cp07_baselines() -> dict[str, Any] | None:
    """Load baseline results from CP07 for comparison if available."""
    if CP07_BASELINE_PATH.exists():
        try:
            with open(CP07_BASELINE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def format_markdown_tables(
    eval_data: dict[str, Any],
    cp07_data: dict[str, Any] | None = None,
) -> str:
    """Generate clean GitHub-flavored markdown tables for display and documentation."""
    lines: list[str] = []

    fold_meta = eval_data["fold_meta"]
    models = eval_data["models"]

    # 1. Macro-Average Comparison Table (Track 1 vs CP07 Baselines)
    lines.append("### Track 1 vs CP07 Baselines: Macro-Average Comparison (6 LOSO Folds)")
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
            f"| **Track 1** | **`{mname}`** | **{mdape_val}** | {mae_val} | {rmse_val} | {r2_val} | {p25_val} | {p30_val} | {sa_val} | {mmre_val} |"
        )

    lines.append("")

    # 2. Per-Fold Breakdown Tables for Track 1 Models
    lines.append("### Track 1 Per-Fold Breakdown by Holdout Source")
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

    # 3. Full-Dataset Fitted Parameters
    full_params = eval_data.get("full_dataset_parameters", {})
    if full_params:
        lines.append("### Track 1 Full-Dataset Fitted Parameters")
        lines.append("")
        for name, p in full_params.items():
            lines.append(f"- **`{name}`**:")
            for k, v in p.items():
                if isinstance(v, float):
                    lines.append(f"  - `{k}`: {v:.4f}")
                else:
                    lines.append(f"  - `{k}`: {v}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Leave-One-Source-Out evaluation of Track 1 models on PredictIQ dataset."
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

    print("\nRunning Leave-One-Source-Out (LOSO) cross-validation for Track 1 models...")
    eval_results = evaluate_track1_loso(df)

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

    # Load CP07 baseline data for comparison
    cp07_data = load_cp07_baselines()

    if not args.quiet:
        md_tables = format_markdown_tables(eval_results, cp07_data)
        print("\n" + "=" * 80)
        print(md_tables)
        print("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
