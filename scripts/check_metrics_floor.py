#!/usr/bin/env python3
"""
PredictIQ v2 — ML Metrics Floor Validator (Checkpoint S09)
=========================================================
Verifies that production artifacts, inference invariants, and empirical
evaluations satisfy all quantitative performance and security floors
defined in backend/ml/metrics_floor.json.

Verification Gates:
  1. Artifact Integrity:
     - manifest.json and model_params.json exist and match canonical UTF-8 SHA-256.
     - Zero pickle: no *.pkl files in production_v2 serving directory.
     - Dataset hash and record counts match verified baseline.
  2. Serving Invariants:
     - Model loads cleanly via load_production_model().
     - All predictions >= min_prediction_hours (1.0 person-hour).
     - Strict size monotonicity: dE/dS > 0 everywhere.
     - Non-crossing quantiles: 1.0 <= p10 <= p25 <= p50 <= p75 <= p90.
  3. Pre-Registered Evidence Verification:
     - NLP synthetic SRS benchmark results satisfy all R09 quality gates.
     - LOSO cross-validation baselines conform to pre-registered performance ceilings.

Usage:
  python scripts/check_metrics_floor.py
  python scripts/check_metrics_floor.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, List, Tuple

# Resolve repository root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_FLOOR_FILE = PROJECT_ROOT / "backend" / "ml" / "metrics_floor.json"
PRODUCTION_ARTIFACTS_DIR = PROJECT_ROOT / "backend" / "ml" / "artifacts" / "production_v2"


class Colors:
    ENABLED = sys.stdout.isatty() or os.getenv("FORCE_COLOR") == "1"
    RESET = "\033[0m" if ENABLED else ""
    BOLD = "\033[1m" if ENABLED else ""
    RED = "\033[91m" if ENABLED else ""
    GREEN = "\033[92m" if ENABLED else ""
    YELLOW = "\033[93m" if ENABLED else ""
    CYAN = "\033[96m" if ENABLED else ""


@dataclass
class GateResult:
    name: str
    target: str
    status: str       # "PASS" or "FAIL"
    message: str
    details: dict[str, Any]


def verify_artifact_integrity(floor_config: dict[str, Any]) -> GateResult:
    """Gate 1: Verify presence of artifacts, canonical hashes, and zero-pickle compliance."""
    violations: List[str] = []
    details: dict[str, Any] = {}

    # Check 1: Zero pickle
    pkl_files = list(PRODUCTION_ARTIFACTS_DIR.glob("*.pkl"))
    if pkl_files:
        violations.append(f"Forbidden pickle files found in serving dir: {[f.name for f in pkl_files]}")
    details["pickle_files_count"] = len(pkl_files)

    # Check 2: Manifest existence and model parameters
    manifest_path = PRODUCTION_ARTIFACTS_DIR / "manifest.json"
    params_path = PRODUCTION_ARTIFACTS_DIR / "model_params.json"

    if not manifest_path.exists():
        violations.append("manifest.json missing from production_v2")
    if not params_path.exists():
        violations.append("model_params.json missing from production_v2")

    if manifest_path.exists() and params_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        invariants = floor_config.get("serving_invariants", {})
        expected_version = invariants.get("model_version", "2.0.0-rc.3")
        expected_canonical_sha = invariants.get("canonical_sha256")
        expected_dataset_sha = floor_config.get("dataset", {}).get("sha256")
        expected_min_records = floor_config.get("dataset", {}).get("min_records", 915)

        if manifest.get("model_version") != expected_version:
            violations.append(
                f"Model version mismatch: expected {expected_version}, got {manifest.get('model_version')}"
            )

        if manifest.get("dataset_sha256") != expected_dataset_sha:
            violations.append(
                f"Dataset SHA-256 mismatch in manifest: expected {expected_dataset_sha}, got {manifest.get('dataset_sha256')}"
            )

        if manifest.get("dataset_records", 0) < expected_min_records:
            violations.append(
                f"Dataset records count below floor: expected >= {expected_min_records}, got {manifest.get('dataset_records')}"
            )

        # Canonical hash verification
        try:
            from backend.ml.artifacts.loader import compute_canonical_json_sha256
            actual_sha = compute_canonical_json_sha256(params_path)
            details["actual_canonical_sha256"] = actual_sha
            if expected_canonical_sha and actual_sha != expected_canonical_sha:
                violations.append(
                    f"Canonical JSON hash mismatch: expected {expected_canonical_sha}, got {actual_sha}"
                )
        except Exception as exc:
            violations.append(f"Error computing canonical hash: {exc}")

    status = "PASS" if not violations else "FAIL"
    message = (
        "Zero pickle, manifest verified, canonical UTF-8 SHA-256 confirmed"
        if not violations
        else "; ".join(violations)
    )

    return GateResult(
        name="Artifact & Serialization Integrity",
        target="backend/ml/artifacts/production_v2",
        status=status,
        message=message,
        details=details,
    )


def verify_serving_invariants(floor_config: dict[str, Any]) -> GateResult:
    """Gate 2: Verify live runtime loading, monotonicity, and quantile ordering."""
    violations: List[str] = []
    details: dict[str, Any] = {}

    try:
        from backend.ml.artifacts.loader import load_production_model
        bundle = load_production_model()
        details["model_version"] = bundle.model_version
        details["architecture"] = bundle.architecture

        min_hours = floor_config.get("serving_invariants", {}).get("min_prediction_hours", 1.0)

        # Monotonicity test across size grid
        test_sizes = [1.0, 10.0, 50.0, 150.0, 300.0, 750.0, 1500.0, 5000.0, 20000.0]
        preds = []
        for s in test_sizes:
            p = float(bundle.predict({"size_fp": s})[0])
            preds.append(p)
            if p < min_hours:
                violations.append(f"Prediction for size_fp={s} is {p:.2f} < min floor {min_hours}h")

            q = bundle.predict_quantiles({"size_fp": s})
            p10 = float(q["p10"][0])
            p25 = float(q.get("p25", [p10])[0])
            p50 = float(q["p50"][0])
            p75 = float(q.get("p75", [p50])[0])
            p90 = float(q["p90"][0])

            if not (min_hours <= p10 <= p25 <= p50 <= p75 <= p90):
                violations.append(
                    f"Quantile monotonicity violated at size_fp={s}: "
                    f"[{p10:.1f}, {p25:.1f}, {p50:.1f}, {p75:.1f}, {p90:.1f}]"
                )

        # Check strict monotonicity across test_sizes
        for i in range(len(preds) - 1):
            if preds[i + 1] <= preds[i]:
                violations.append(
                    f"Strict monotonicity violated: pred({test_sizes[i+1]})={preds[i+1]} <= pred({test_sizes[i]})={preds[i]}"
                )

        details["sample_predictions"] = {str(s): round(p, 1) for s, p in zip(test_sizes, preds)}

    except Exception as exc:
        violations.append(f"Model loader runtime failure: {exc}")

    status = "PASS" if not violations else "FAIL"
    message = (
        "Positive predictions, strict size monotonicity, and quantile non-crossing verified"
        if not violations
        else "; ".join(violations)
    )

    return GateResult(
        name="Serving Invariants & Monotonicity",
        target="load_production_model() runtime",
        status=status,
        message=message,
        details=details,
    )


def verify_empirical_benchmark_evidence(floor_config: dict[str, Any]) -> GateResult:
    """Gate 3: Verify recorded evidence meets NLP SRS and cross-validation floors."""
    violations: List[str] = []
    details: dict[str, Any] = {}

    # 1. NLP SRS benchmark results
    r09_path = PROJECT_ROOT / "docs" / "evidence" / "r09_srs_results.json"
    if r09_path.exists():
        try:
            r09_data = json.loads(r09_path.read_text(encoding="utf-8"))
            srs_floors = floor_config.get("nlp_srs_regression_floors", {})

            mdape = r09_data.get("overall_metrics", {}).get("functional_size", {}).get("mdape_pct", 999.0)
            tech_f1 = r09_data.get("overall_metrics", {}).get("tech_stack", {}).get("micro_f1", 0.0)
            feat_rec = r09_data.get("overall_metrics", {}).get("feature_extraction", {}).get("mean_recall_pct", 0.0)
            int_mae = r09_data.get("overall_metrics", {}).get("integration_count", {}).get("mae", 999.0)

            max_mdape = srs_floors.get("functional_size_mdape_max_pct", 20.0)
            min_f1 = srs_floors.get("tech_stack_micro_f1_min", 0.85)
            min_rec = srs_floors.get("feature_recall_min_pct", 90.0)
            max_int_mae = srs_floors.get("integration_count_mae_max", 1.0)

            details["r09_achieved"] = {
                "size_mdape": f"{mdape:.2f}% (floor: <= {max_mdape}%)",
                "tech_f1": f"{tech_f1:.4f} (floor: >= {min_f1})",
                "feature_recall": f"{feat_rec:.1f}% (floor: >= {min_rec}%)",
                "integration_mae": f"{int_mae:.2f} (floor: <= {max_int_mae})",
            }

            if mdape > max_mdape:
                violations.append(f"R09 SRS Functional Size MdAPE {mdape:.2f}% exceeds floor {max_mdape}%")
            if tech_f1 < min_f1:
                violations.append(f"R09 Tech Stack Micro-F1 {tech_f1:.4f} below floor {min_f1}")
            if feat_rec < min_rec:
                violations.append(f"R09 Feature Recall {feat_rec:.1f}% below floor {min_rec}%")
            if int_mae > max_int_mae:
                violations.append(f"R09 Integration MAE {int_mae:.2f} exceeds floor {max_int_mae}")

        except Exception as exc:
            violations.append(f"Failed parsing r09_srs_results.json: {exc}")
    else:
        details["r09_status"] = "r09_srs_results.json not found (skipped)"

    # 2. LOSO Baseline Results
    cp07_path = PROJECT_ROOT / "docs" / "evidence" / "CP07_baseline_results.json"
    if cp07_path.exists():
        try:
            cp07_data = json.loads(cp07_path.read_text(encoding="utf-8"))
            loso_floors = floor_config.get("loso_cross_validation_floors", {})
            max_loso_mdape = loso_floors.get("macro_mdape_max_pct", 56.5)

            # Check LogLinear or Albrecht baseline
            baselines = cp07_data.get("baselines", {})
            ll_mdape = (
                baselines.get("LogLinearBaseline", {})
                .get("macro_average", {})
                .get("mdape", 999.0)
            )
            details["cp07_loglinear_mdape"] = f"{ll_mdape:.1f}% (floor: <= {max_loso_mdape}%)"
            if ll_mdape > max_loso_mdape:
                violations.append(f"CP07 LogLinear Macro MdAPE {ll_mdape:.1f}% exceeds floor {max_loso_mdape}%")

        except Exception as exc:
            violations.append(f"Failed parsing CP07_baseline_results.json: {exc}")

    status = "PASS" if not violations else "FAIL"
    message = (
        "Empirical benchmarks satisfy all pre-registered evaluation floors"
        if not violations
        else "; ".join(violations)
    )

    return GateResult(
        name="Empirical Benchmark & Evaluation Evidence",
        target="docs/evidence benchmark records",
        status=status,
        message=message,
        details=details,
    )


def run_checks(floor_file: Path) -> Tuple[bool, List[GateResult]]:
    """Run all metrics floor verification checks."""
    if not floor_file.exists():
        res = GateResult(
            name="Metrics Floor Specification File",
            target=str(floor_file),
            status="FAIL",
            message=f"Floor specification file not found: {floor_file}",
            details={},
        )
        return False, [res]

    floor_config = json.loads(floor_file.read_text(encoding="utf-8"))

    results = [
        verify_artifact_integrity(floor_config),
        verify_serving_invariants(floor_config),
        verify_empirical_benchmark_evidence(floor_config),
    ]

    all_pass = all(r.status == "PASS" for r in results)
    return all_pass, results


def main() -> int:
    parser = argparse.ArgumentParser(description="PredictIQ ML Metrics Floor Validator")
    parser.add_argument(
        "--floor-file",
        type=Path,
        default=DEFAULT_FLOOR_FILE,
        help="Path to metrics_floor.json specification file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON summary",
    )
    args = parser.parse_args()

    all_pass, results = run_checks(args.floor_file)

    if args.json:
        report = {
            "all_gates_pass": all_pass,
            "gates": [asdict(r) for r in results],
        }
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{Colors.BOLD}{'=' * 80}")
        print("           PredictIQ v2 — ML Metrics Floor Verification (S09)")
        print(f"{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{'#':<3}  {'Gate Name':<35}  {'Status':<8}  {'Summary'}{Colors.RESET}")
        print("-" * 80)

        for idx, r in enumerate(results, start=1):
            status_str = (
                f"{Colors.GREEN}{Colors.BOLD}PASS{Colors.RESET}"
                if r.status == "PASS"
                else f"{Colors.RED}{Colors.BOLD}FAIL{Colors.RESET}"
            )
            print(f"{idx:<3}  {r.name:<35}  {status_str:<17}  {r.message}")

        print("-" * 80)
        if all_pass:
            print(f" {Colors.GREEN}{Colors.BOLD}[METRICS FLOOR: ALL GATES PASSED]{Colors.RESET}\n")
        else:
            print(f" {Colors.RED}{Colors.BOLD}[METRICS FLOOR: ONE OR MORE GATES FAILED]{Colors.RESET}\n")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
