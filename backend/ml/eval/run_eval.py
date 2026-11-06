"""CLI runner for Leave-One-Source-Out evaluation of baseline models.

Runs all baselines across the 6 historical data source folds,
computes frozen evaluation metrics, prints structured markdown tables,
and writes results to docs/evidence/CP07_baseline_results.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure repository root is on sys.path for direct script execution
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd

from backend.ml.eval.baselines import (
    AlbrechtNominalPredictor,
    HuberPowerLawBaseline,
    LogLinearBaseline,
    MedianDummyPredictor,
    MedianProductivityPredictor,
)
from backend.ml.eval.metrics import compute_metrics, macro_average_metrics
from backend.ml.eval.protocol import LeaveOneSourceOutSplitter, load_dataset


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_default_baselines() -> dict[str, Any]:
    """Instantiate fresh instances of baseline models."""
    return {
        "MedianDummyPredictor": MedianDummyPredictor(),
        "MedianProductivityPredictor": MedianProductivityPredictor(),
        "AlbrechtNominalPredictor": AlbrechtNominalPredictor(),
        "LogLinearBaseline": LogLinearBaseline(),
        "HuberPowerLawBaseline": HuberPowerLawBaseline(),
    }


def evaluate_baselines_loso(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Execute Leave-One-Source-Out cross-validation for all baselines."""
    splitter = LeaveOneSourceOutSplitter()
    folds = list(splitter.split_df(df))

    baseline_names = list(get_default_baselines().keys())
    results: dict[str, dict[str, Any]] = {
        name: {"folds": {}, "macro_average": {}} for name in baseline_names
    }

    # Track fold metadata
    fold_meta = {}
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

        for name in baseline_names:
            model = get_default_baselines()[name]
            model.fit(train_df, y_train)
            y_pred = model.predict(test_df)

            metrics = compute_metrics(
                y_true=y_test,
                y_pred=y_pred,
                y_train=y_train,
            )
            results[name]["folds"][holdout_source] = metrics

    # Compute macro-averages
    for name in baseline_names:
        fold_metric_list = [results[name]["folds"][s] for s in results[name]["folds"]]
        results[name]["macro_average"] = macro_average_metrics(fold_metric_list)

    return {
        "fold_meta": fold_meta,
        "baselines": results,
    }


def format_markdown_tables(eval_data: dict[str, Any]) -> str:
    """Generate clean GitHub-flavored markdown tables for display and documentation."""
    lines: list[str] = []

    fold_meta = eval_data["fold_meta"]
    baselines = eval_data["baselines"]

    # 1. Macro-Average Comparison Table
    lines.append("### Baseline Macro-Average Comparison (6 LOSO Folds)")
    lines.append("")
    lines.append("| Baseline Model | MdAPE (%) | MAE (hrs) | RMSE (hrs) | $R^2$ | PRED(25) (%) | PRED(30) (%) | SA (%) | MMRE (%) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for name, bdata in baselines.items():
        macro = bdata["macro_average"]
        mdape_val = f"{macro['mdape']:.1f}%"
        mae_val = f"{macro['mae']:.1f}"
        rmse_val = f"{macro['rmse']:.1f}"
        r2_val = f"{macro['r2']:.3f}"
        p25_val = f"{macro['pred25']:.1f}%"
        p30_val = f"{macro['pred30']:.1f}%"
        sa_val = f"{macro['sa']:.1f}%"
        mmre_val = f"{macro['mmre']:.1f}%"
        lines.append(
            f"| `{name}` | **{mdape_val}** | {mae_val} | {rmse_val} | {r2_val} | {p25_val} | {p30_val} | {sa_val} | {mmre_val} |"
        )

    lines.append("")

    # 2. Per-Fold Breakdown Tables for each baseline
    lines.append("### Per-Fold Breakdown by Holdout Source")
    lines.append("")
    lines.append("| Model | Holdout Source | Test N | MdAPE (%) | MAE (hrs) | RMSE (hrs) | $R^2$ | PRED(25) (%) | PRED(30) (%) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for name, bdata in baselines.items():
        for source, smetrics in bdata["folds"].items():
            n_test = fold_meta[source]["n_test"]
            lines.append(
                f"| `{name}` | `{source}` | {n_test} | {smetrics['mdape']:.1f}% | "
                f"{smetrics['mae']:.1f} | {smetrics['rmse']:.1f} | {smetrics['r2']:.3f} | "
                f"{smetrics['pred25']:.1f}% | {smetrics['pred30']:.1f}% |"
            )

    return "\n".join(lines)


def run(
    data_path: Path | str | None = None,
    output_path: Path | str | None = None,
    quiet: bool = False,
) -> dict[str, Any]:
    """Execute evaluation and serialize results."""
    resolved_data_path = Path(data_path) if data_path else Path("backend/ml/data/projects_v2.csv")
    resolved_output_path = (
        Path(output_path) if output_path else Path("docs/evidence/CP07_baseline_results.json")
    )

    if not quiet:
        print(f"Loading dataset from: {resolved_data_path}")

    df = load_dataset(resolved_data_path)
    file_hash = compute_sha256(resolved_data_path)

    if not quiet:
        print(f"Loaded {len(df)} rows across {df['source'].nunique()} sources. SHA256: {file_hash}")
        print("Running Leave-One-Source-Out evaluation across baseline models...")

    eval_data = evaluate_baselines_loso(df)

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(resolved_data_path),
        "dataset_sha256": file_hash,
        "total_records": len(df),
        "source_counts": df["source"].value_counts().to_dict(),
        "fold_meta": eval_data["fold_meta"],
        "baselines": eval_data["baselines"],
    }

    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(resolved_output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    if not quiet:
        print(f"Results saved to: {resolved_output_path}")
        print("\n" + "=" * 80)
        print(format_markdown_tables(eval_data))
        print("=" * 80 + "\n")

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="PredictIQ Baseline Evaluation Harness")
    parser.add_argument(
        "--dataset",
        type=str,
        default="backend/ml/data/projects_v2.csv",
        help="Path to harmonized dataset CSV",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="docs/evidence/CP07_baseline_results.json",
        help="Path to save evaluation JSON results",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console markdown output",
    )
    args = parser.parse_args()

    run(
        data_path=args.dataset,
        output_path=args.output,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    main()
