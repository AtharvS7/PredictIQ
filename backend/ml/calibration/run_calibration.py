"""Leave-One-Source-Out (LOSO) Calibration Evaluation Runner for CP11.

Evaluates conformal prediction wrappers (Split and Mondrian) across the 6 historical
data source folds from projects_v2.csv:
1. MultivariateMonotoneModel (Primary Track 1 Estimator)
2. MonotonePowerLaw (Single-Feature Track 1 Estimator)

Outputs coverage tables, interval width analysis, and serializes results to
docs/evidence/CP11_results.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add repository root to sys.path if not present
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

from backend.ml.calibration.conformal import (  # noqa: E402
    MONDRIAN_BUCKETS,
    ConformalIntervalPredictor,
    assign_mondrian_bucket,
)
from backend.ml.eval.protocol import LeaveOneSourceOutSplitter, load_dataset  # noqa: E402
from backend.ml.track1.models import (  # noqa: E402
    MonotonePowerLaw,
    MultivariateMonotoneModel,
)

DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "projects_v2.csv"
)
DEFAULT_OUTPUT_PATH = _REPO_ROOT / "docs" / "evidence" / "CP11_results.json"


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def evaluate_calibration_loso(
    df: pd.DataFrame,
    alpha: float = 0.20,
    cal_size: float = 0.20,
    random_state: int = 42,
) -> dict[str, Any]:
    """Execute Leave-One-Source-Out calibration evaluation for Track 1 models.

    Parameters
    ----------
    df : pd.DataFrame
        Full harmonized projects_v2 dataset.
    alpha : float
        Target significance level (default 0.20 -> 80% nominal interval).
    cal_size : float
        Fraction of training fold allocated to calibration (default 0.20).
    random_state : int
        Random seed for train/calibration split.

    Returns
    -------
    dict[str, Any]
        Structured evaluation results.
    """
    splitter = LeaveOneSourceOutSplitter()
    folds = list(splitter.split_df(df))

    model_factories: dict[str, Any] = {
        "MultivariateMonotoneModel": lambda: MultivariateMonotoneModel(),
        "MonotonePowerLaw": lambda: MonotonePowerLaw(),
    }

    results: dict[str, Any] = {}

    for model_name, factory in model_factories.items():
        results[model_name] = {
            "mondrian": {"folds": {}, "macro_average": {}, "pooled": {}},
            "split": {"folds": {}, "macro_average": {}, "pooled": {}},
        }

        for method in ["mondrian", "split"]:
            is_mondrian = method == "mondrian"
            fold_results = {}
            total_test_samples = 0
            total_covered = 0
            all_covs = []
            all_cal_covs = []
            all_widths = []
            all_rel_widths = []

            for fold in folds:
                holdout_source = fold.fold_name
                train_df = fold.train_df
                test_df = fold.test_df
                n_test = len(test_df)
                total_test_samples += n_test

                y_test = test_df["effort_hours"].to_numpy(dtype=np.float64)

                # Split train_df into proper training and calibration
                proper_tr, cal_df = train_test_split(
                    train_df,
                    test_size=cal_size,
                    random_state=random_state,
                )

                # Instantiate and fit base estimator
                base_est = factory()
                base_est.fit(proper_tr, proper_tr["effort_hours"].to_numpy())

                # Instantiate and calibrate conformal wrapper
                calibrator = ConformalIntervalPredictor(
                    estimator=base_est,
                    alpha=alpha,
                    mondrian=is_mondrian,
                    score_type="log_residual",
                    random_state=random_state,
                )
                calibrator.calibrate(cal_df, cal_df["effort_hours"].to_numpy())

                # 1. Calibration split coverage check
                cal_quantiles = calibrator.predict_quantiles(cal_df)
                y_cal = cal_df["effort_hours"].to_numpy(dtype=np.float64)
                cal_covered = (y_cal >= cal_quantiles["p10"]) & (
                    y_cal <= cal_quantiles["p90"]
                )
                cal_cov = float(np.mean(cal_covered) * 100.0)
                all_cal_covs.append(cal_cov)

                # 2. Out-of-Domain Holdout Test evaluation
                test_quantiles = calibrator.predict_quantiles(test_df)
                p10 = test_quantiles["p10"]
                p50 = test_quantiles["p50"]
                p90 = test_quantiles["p90"]

                # Quantile monotonicity verification: p10 <= p50 <= p90
                monotone_ok = bool(
                    (p10 <= p50 + 1e-6).all()
                    and (p50 <= p90 + 1e-6).all()
                    and (p10 >= 1.0).all()
                )

                # Empirical coverage on holdout source
                test_covered = (y_test >= p10) & (y_test <= p90)
                n_covered = int(np.sum(test_covered))
                total_covered += n_covered
                test_cov = float(np.mean(test_covered) * 100.0)
                all_covs.append(test_cov)

                # Interval width metrics
                widths = p90 - p10
                rel_widths = widths / p50
                med_width = float(np.median(widths))
                mean_width = float(np.mean(widths))
                med_rel_width = float(np.median(rel_widths))

                all_widths.append(med_width)
                all_rel_widths.append(med_rel_width)

                # Bucket-level conditional coverage on test fold
                test_buckets = assign_mondrian_bucket(
                    test_df["size_value"].to_numpy()
                )
                bucket_cov: dict[str, float | None] = {}
                bucket_counts: dict[str, int] = {}
                for b in MONDRIAN_BUCKETS:
                    b_mask = test_buckets == b
                    b_count = int(np.sum(b_mask))
                    bucket_counts[b] = b_count
                    if b_count > 0:
                        bucket_cov[b] = float(np.mean(test_covered[b_mask]) * 100.0)
                    else:
                        bucket_cov[b] = None

                fold_results[holdout_source] = {
                    "n_test": n_test,
                    "n_train": len(train_df),
                    "n_cal": len(cal_df),
                    "test_coverage_pct": round(test_cov, 2),
                    "calibration_coverage_pct": round(cal_cov, 2),
                    "meets_75pct_threshold": bool(test_cov >= 75.0),
                    "quantile_monotonicity_verified": monotone_ok,
                    "global_quantile": round(float(calibrator.global_quantile_), 4),
                    "bucket_quantiles": {
                        k: round(v, 4)
                        for k, v in calibrator.bucket_quantiles_.items()
                    },
                    "bucket_counts": bucket_counts,
                    "bucket_coverage_pct": bucket_cov,
                    "median_interval_width_hours": round(med_width, 1),
                    "mean_interval_width_hours": round(mean_width, 1),
                    "median_relative_interval_width": round(med_rel_width, 3),
                }

            macro_cov = float(np.mean(all_covs))
            macro_cal_cov = float(np.mean(all_cal_covs))
            pooled_cov = float((total_covered / total_test_samples) * 100.0)
            macro_med_width = float(np.mean(all_widths))
            macro_rel_width = float(np.mean(all_rel_widths))

            results[model_name][method] = {
                "folds": fold_results,
                "macro_average": {
                    "test_coverage_pct": round(macro_cov, 2),
                    "calibration_coverage_pct": round(macro_cal_cov, 2),
                    "meets_75pct_nominal": bool(macro_cov >= 75.0),
                    "median_interval_width_hours": round(macro_med_width, 1),
                    "median_relative_width": round(macro_rel_width, 3),
                },
                "pooled": {
                    "total_test_samples": total_test_samples,
                    "total_covered_samples": total_covered,
                    "pooled_coverage_pct": round(pooled_cov, 2),
                    "meets_75pct_nominal": bool(pooled_cov >= 75.0),
                },
            }

    return results


def print_summary_tables(results: dict[str, Any], alpha: float) -> None:
    """Print ASCII comparison tables of calibration results."""
    nominal_cov = round((1.0 - alpha) * 100.0, 1)
    print("=" * 88)
    print(
        f"PREDICTIQ v2 - CP11 CALIBRATED UNCERTAINTY (Alpha = {alpha:.2f}, Nominal Coverage = {nominal_cov}%)"
    )
    print("=" * 88)

    for model_name, methods in results.items():
        print(f"\n--- Estimator: {model_name} ---")
        headers = [
            "Source",
            "N_test",
            "Mondrian Cov (%)",
            "Split Cov (%)",
            "Mondrian Width (h)",
            "Split Width (h)",
            "Status (>=75%)",
        ]
        col_w = [14, 8, 18, 16, 20, 18, 16]
        header_line = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_w))
        print("-" * len(header_line))
        print(header_line)
        print("-" * len(header_line))

        m_folds = methods["mondrian"]["folds"]
        s_folds = methods["split"]["folds"]

        for source in m_folds:
            mf = m_folds[source]
            sf = s_folds[source]
            status = "PASS" if mf["test_coverage_pct"] >= 75.0 else "OOD-DEGRADED"
            row = [
                source,
                str(mf["n_test"]),
                f"{mf['test_coverage_pct']:.1f}%",
                f"{sf['test_coverage_pct']:.1f}%",
                f"{mf['median_interval_width_hours']:.1f}",
                f"{sf['median_interval_width_hours']:.1f}",
                status,
            ]
            print(" | ".join(f"{v:<{w}}" for v, w in zip(row, col_w)))

        print("-" * len(header_line))
        m_macro = methods["mondrian"]["macro_average"]
        s_macro = methods["split"]["macro_average"]
        m_pool = methods["mondrian"]["pooled"]
        s_pool = methods["split"]["pooled"]

        macro_status = "PASS (>=75%)" if m_macro["meets_75pct_nominal"] else "FAIL"
        macro_row = [
            "MACRO AVERAGE",
            "915",
            f"{m_macro['test_coverage_pct']:.1f}%",
            f"{s_macro['test_coverage_pct']:.1f}%",
            f"{m_macro['median_interval_width_hours']:.1f}",
            f"{s_macro['median_interval_width_hours']:.1f}",
            macro_status,
        ]
        print(" | ".join(f"{v:<{w}}" for v, w in zip(macro_row, col_w)))

        pool_row = [
            "POOLED (ALL)",
            "915",
            f"{m_pool['pooled_coverage_pct']:.1f}%",
            f"{s_pool['pooled_coverage_pct']:.1f}%",
            "-",
            "-",
            "PASS" if m_pool["meets_75pct_nominal"] else "FAIL",
        ]
        print(" | ".join(f"{v:<{w}}" for v, w in zip(pool_row, col_w)))
        print("-" * len(header_line))


def main() -> int:
    """CLI Entrypoint for running calibration evaluation."""
    parser = argparse.ArgumentParser(
        description="Leave-One-Source-Out Conformal Prediction Calibration Runner (CP11)."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to harmonized projects_v2.csv dataset.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to save serialized JSON results.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.20,
        help="Significance level alpha (default 0.20 for 80% intervals).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for train/calibration splitting.",
    )
    args = parser.parse_args()

    print(f"Loading dataset from: {args.dataset}")
    df = load_dataset(args.dataset)
    dataset_sha = compute_sha256(args.dataset)
    print(f"Dataset loaded: {len(df)} rows across {df['source'].nunique()} sources.")
    print(f"Dataset SHA-256: {dataset_sha}")

    eval_results = evaluate_calibration_loso(
        df=df,
        alpha=args.alpha,
        cal_size=0.20,
        random_state=args.seed,
    )

    print_summary_tables(eval_results, args.alpha)

    # Structure payload for JSON serialization
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(args.dataset.resolve()),
        "dataset_sha256": dataset_sha,
        "total_records": len(df),
        "source_counts": df["source"].value_counts().to_dict(),
        "nominal_significance_alpha": args.alpha,
        "nominal_coverage_rate": 1.0 - args.alpha,
        "size_bucket_cutoffs": [150.0, 750.0],
        "size_bucket_names": ["small", "medium", "large"],
        "models": eval_results,
    }

    # Ensure parent output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"\nSerialized results saved to: {args.output}")

    # Check whether primary model MultivariateMonotoneModel meets >= 75%
    multi_mondrian_macro = eval_results["MultivariateMonotoneModel"]["mondrian"][
        "macro_average"
    ]["test_coverage_pct"]
    if multi_mondrian_macro >= 75.0:
        print(
            f"SUCCESS: Macro OOD coverage ({multi_mondrian_macro:.1f}%) meets >= 75% nominal threshold."
        )
        return 0
    else:
        print(
            f"WARNING: Macro OOD coverage ({multi_mondrian_macro:.1f}%) below 75% nominal threshold."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
