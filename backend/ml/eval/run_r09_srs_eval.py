"""
PredictIQ v2 Checkpoint R09 — NLP & Golden SRS Benchmark Evaluation Harness
===========================================================================
Feeds gold-standard Software Requirements Specification (SRS) documents into
backend.app.services.nlp_extractor.extract_features_from_document, compares
extracted values to ground truth annotations across 6 software domains, and computes:
  - Functional Size Relative Error (MdAPE, MAPE, PRED25, PRED30)
  - Tech Stack Classification (Micro/Macro Precision, Recall, F1)
  - Integration Count Accuracy (Exact match, within +/- 1, MAE)
  - Feature Extraction Recall & MdAPE
  - Complexity Classification Accuracy
  - Domain-Level Performance Breakdown (6 domains)
  - Verification of Quality Gates
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

# Resolve repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Ensure backward-compatible extract_features_from_document import
import backend.app.services.nlp_extractor as _nlp_mod

if not hasattr(_nlp_mod, "extract_features_from_document"):
    _nlp_mod.extract_features_from_document = _nlp_mod.nlp_extractor.extract

from backend.app.services.nlp_extractor import extract_features_from_document


def load_gold_srs_suite() -> tuple[Path, dict[str, Any]]:
    """Locate and load the gold SRS annotations and documents directory."""
    srs_dir = _REPO_ROOT / "backend" / "tests" / "fixtures" / "srs"
    if not srs_dir.exists():
        raise FileNotFoundError(f"SRS fixtures directory not found at {srs_dir}")

    annotations_file = srs_dir / "annotations.json"
    if not annotations_file.exists():
        raise FileNotFoundError(f"Annotations file not found at {annotations_file}")

    annotations = json.loads(annotations_file.read_text(encoding="utf-8"))
    return srs_dir, annotations


def evaluate_srs_extractor() -> dict[str, Any]:
    """Execute the full R09 benchmark evaluation suite."""
    srs_dir, annotations = load_gold_srs_suite()

    doc_records: list[dict[str, Any]] = []
    crashes: list[str] = []
    non_finite_outputs: list[str] = []

    for doc_id, meta in annotations.items():
        doc_filename = meta["filename"]
        doc_path = srs_dir / doc_filename

        if not doc_path.exists():
            raise FileNotFoundError(f"SRS document file missing: {doc_path}")

        doc_text = doc_path.read_text(encoding="utf-8")

        try:
            extracted = extract_features_from_document(doc_text)
        except Exception as exc:  # noqa: BLE001
            crashes.append(f"{doc_id}: {type(exc).__name__} - {exc}")
            continue

        gt = meta["ground_truth"]

        # 1. Functional Size (FP)
        true_fp = float(gt["functional_size"]["point_fp"])
        pred_fp = float(extracted.get("size_fp", {}).get("value", 0.0))

        if not (np.isfinite(true_fp) and np.isfinite(pred_fp)):
            non_finite_outputs.append(
                f"{doc_id}: Non-finite size_fp (true={true_fp}, pred={pred_fp})"
            )
            continue

        ape = abs(pred_fp - true_fp) / true_fp if true_fp > 0 else 0.0

        # Uncertainty intervals
        uncertainty = extracted.get("size_fp", {}).get("uncertainty", {})
        p10 = float(uncertainty.get("p10", pred_fp * 0.85))
        p50 = float(uncertainty.get("p50", pred_fp))
        p90 = float(uncertainty.get("p90", pred_fp * 1.15))

        interval_valid = (p10 <= p50 <= p90) and (p10 > 0)

        # 2. Tech Stack Evaluation
        gt_tech = {t.lower() for t in gt["tech_stack"]}
        pred_tech = {
            t.lower() for t in extracted.get("tech_stack", {}).get("value", [])
        }

        tp = len(gt_tech & pred_tech)
        fp = len(pred_tech - gt_tech)
        fn = len(gt_tech - pred_tech)

        tech_precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        tech_recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        tech_f1 = (
            (2.0 * tech_precision * tech_recall) / (tech_precision + tech_recall)
            if (tech_precision + tech_recall) > 0
            else 0.0
        )

        # 3. Integration Count
        gt_int = int(gt["integration_count"])
        pred_int = int(extracted.get("integration_count", {}).get("value", 0))
        int_diff = abs(pred_int - gt_int)

        # 4. Feature Extraction
        gt_features = int(gt["feature_count"])
        pred_features = int(extracted.get("feature_count", {}).get("value", 0))
        feat_recall = min(1.0, pred_features / gt_features) if gt_features > 0 else 1.0
        feat_ape = (
            abs(pred_features - gt_features) / gt_features if gt_features > 0 else 0.0
        )

        # 5. Complexity
        gt_complexity = gt["complexity_level"]
        pred_complexity = extracted.get("complexity", {}).get("value", "Medium")

        # Normalize comparison: "High" matches "High" or "Very High" for enterprise systems
        complexity_match = gt_complexity.lower() == pred_complexity.lower() or (
            gt_complexity.lower() in ("high", "very high")
            and pred_complexity.lower() in ("high", "very high")
        )

        doc_records.append(
            {
                "doc_id": doc_id,
                "domain": meta["domain"],
                "project_name": meta["project_name"],
                "true_fp": true_fp,
                "pred_fp": pred_fp,
                "ape": ape,
                "p10": p10,
                "p50": p50,
                "p90": p90,
                "interval_valid": interval_valid,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tech_precision": tech_precision,
                "tech_recall": tech_recall,
                "tech_f1": tech_f1,
                "gt_int": gt_int,
                "pred_int": pred_int,
                "int_diff": int_diff,
                "gt_features": gt_features,
                "pred_features": pred_features,
                "feat_recall": feat_recall,
                "feat_ape": feat_ape,
                "gt_complexity": gt_complexity,
                "pred_complexity": pred_complexity,
                "complexity_match": complexity_match,
            }
        )

    total_docs = len(doc_records)
    if total_docs == 0:
        raise RuntimeError("No documents were successfully evaluated.")

    # Global Functional Size Metrics
    apes = np.array([r["ape"] for r in doc_records])
    mdape_val = float(np.median(apes)) * 100.0
    mape_val = float(np.mean(apes)) * 100.0
    pred25_val = float(np.mean(apes <= 0.25)) * 100.0
    pred30_val = float(np.mean(apes <= 0.30)) * 100.0

    # Global Tech Stack Classification Metrics
    total_tp = sum(r["tp"] for r in doc_records)
    total_fp = sum(r["fp"] for r in doc_records)
    total_fn = sum(r["fn"] for r in doc_records)

    micro_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
    micro_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
    micro_f1 = (
        (2.0 * micro_prec * micro_rec) / (micro_prec + micro_rec)
        if (micro_prec + micro_rec) > 0
        else 0.0
    )
    macro_f1 = float(np.mean([r["tech_f1"] for r in doc_records]))
    macro_prec = float(np.mean([r["tech_precision"] for r in doc_records]))
    macro_rec = float(np.mean([r["tech_recall"] for r in doc_records]))

    # Global Integration Count Metrics
    int_diffs = np.array([r["int_diff"] for r in doc_records])
    int_exact_pct = float(np.mean(int_diffs == 0)) * 100.0
    int_within1_pct = float(np.mean(int_diffs <= 1)) * 100.0
    int_mae = float(np.mean(int_diffs))

    # Global Feature Extraction Metrics
    feat_recalls = np.array([r["feat_recall"] for r in doc_records])
    feat_recall_pct = float(np.mean(feat_recalls)) * 100.0
    feat_mdape = float(np.median([r["feat_ape"] for r in doc_records])) * 100.0

    # Global Complexity Classification Accuracy
    complexity_acc_pct = (
        float(np.mean([r["complexity_match"] for r in doc_records])) * 100.0
    )

    # Interval Validity Rate
    interval_valid_pct = (
        float(np.mean([r["interval_valid"] for r in doc_records])) * 100.0
    )

    # ── Domain-Specific Breakdown ──────────────────────────────────────────
    domain_groups: dict[str, list[dict[str, Any]]] = {}
    for r in doc_records:
        domain_groups.setdefault(r["domain"], []).append(r)

    domain_metrics: dict[str, dict[str, float]] = {}
    for dom_name, records in sorted(domain_groups.items()):
        dom_apes = np.array([x["ape"] for x in records])
        dom_tp = sum(x["tp"] for x in records)
        dom_fp = sum(x["fp"] for x in records)
        dom_fn = sum(x["fn"] for x in records)
        dom_m_prec = dom_tp / (dom_tp + dom_fp) if (dom_tp + dom_fp) > 0 else 1.0
        dom_m_rec = dom_tp / (dom_tp + dom_fn) if (dom_tp + dom_fn) > 0 else 1.0
        dom_m_f1 = (
            (2 * dom_m_prec * dom_m_rec) / (dom_m_prec + dom_m_rec)
            if (dom_m_prec + dom_m_rec) > 0
            else 0.0
        )

        dom_int_diffs = np.array([x["int_diff"] for x in records])
        dom_feat_rec = np.array([x["feat_recall"] for x in records])

        domain_metrics[dom_name] = {
            "num_docs": len(records),
            "mdape_pct": float(np.median(dom_apes)) * 100.0,
            "mape_pct": float(np.mean(dom_apes)) * 100.0,
            "pred25_pct": float(np.mean(dom_apes <= 0.25)) * 100.0,
            "tech_micro_f1": float(dom_m_f1),
            "tech_micro_precision": float(dom_m_prec),
            "tech_micro_recall": float(dom_m_rec),
            "integration_exact_pct": float(np.mean(dom_int_diffs == 0)) * 100.0,
            "integration_within1_pct": float(np.mean(dom_int_diffs <= 1)) * 100.0,
            "integration_mae": float(np.mean(dom_int_diffs)),
            "feature_recall_pct": float(np.mean(dom_feat_rec)) * 100.0,
            "complexity_acc_pct": float(
                np.mean([x["complexity_match"] for x in records])
            )
            * 100.0,
        }

    # ── Quality Gate Verification ──────────────────────────────────────────
    gate_mdape = mdape_val <= 20.0
    gate_tech_f1 = micro_f1 >= 0.85
    gate_feature_recall = feat_recall_pct >= 90.0
    gate_integration_mae = int_mae <= 1.0
    gate_robustness = len(crashes) == 0 and len(non_finite_outputs) == 0
    gate_all_pass = all(
        [
            gate_mdape,
            gate_tech_f1,
            gate_feature_recall,
            gate_integration_mae,
            gate_robustness,
        ]
    )

    results = {
        "benchmark": "PredictIQ v2 Checkpoint R09 — NLP & Golden SRS Benchmark",
        "sample_size": total_docs,
        "domains_evaluated": len(domain_metrics),
        "quality_gates": {
            "all_gates_pass": gate_all_pass,
            "gate_1_functional_size_mdape": {
                "threshold": "<= 20.0%",
                "achieved": f"{mdape_val:.2f}%",
                "pass": gate_mdape,
            },
            "gate_2_tech_stack_micro_f1": {
                "threshold": ">= 0.8500",
                "achieved": f"{micro_f1:.4f}",
                "pass": gate_tech_f1,
            },
            "gate_3_feature_extraction_recall": {
                "threshold": ">= 90.0%",
                "achieved": f"{feat_recall_pct:.2f}%",
                "pass": gate_feature_recall,
            },
            "gate_4_integration_count_mae": {
                "threshold": "<= 1.00",
                "achieved": f"{int_mae:.2f}",
                "pass": gate_integration_mae,
            },
            "gate_5_zero_crashes_and_finite_outputs": {
                "threshold": "0 crashes, 0 non-finite outputs",
                "achieved": f"{len(crashes)} crashes, {len(non_finite_outputs)} non-finite",
                "pass": gate_robustness,
            },
        },
        "overall_metrics": {
            "functional_size": {
                "mdape_pct": round(mdape_val, 2),
                "mape_pct": round(mape_val, 2),
                "pred25_pct": round(pred25_val, 2),
                "pred30_pct": round(pred30_val, 2),
                "interval_valid_pct": round(interval_valid_pct, 2),
            },
            "tech_stack": {
                "micro_precision": round(micro_prec, 4),
                "micro_recall": round(micro_rec, 4),
                "micro_f1": round(micro_f1, 4),
                "macro_precision": round(macro_prec, 4),
                "macro_recall": round(macro_rec, 4),
                "macro_f1": round(macro_f1, 4),
            },
            "integration_count": {
                "exact_match_pct": round(int_exact_pct, 2),
                "within_plus_minus_1_pct": round(int_within1_pct, 2),
                "mae": round(int_mae, 2),
            },
            "feature_extraction": {
                "mean_recall_pct": round(feat_recall_pct, 2),
                "feature_mdape_pct": round(feat_mdape, 2),
            },
            "complexity_classification": {
                "accuracy_pct": round(complexity_acc_pct, 2),
            },
        },
        "domain_breakdown": domain_metrics,
        "per_document_metrics": doc_records,
        "crashes": crashes,
        "non_finite_outputs": non_finite_outputs,
    }

    # Save output artifacts to docs/evidence
    evidence_dir = _REPO_ROOT / "docs" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_json = evidence_dir / "r09_srs_results.json"
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    return results


def print_summary_tables(results: dict[str, Any]) -> None:
    """Print clean formatted markdown tables of benchmark results."""
    gates = results["quality_gates"]
    overall = results["overall_metrics"]
    domains = results["domain_breakdown"]

    print("\n" + "=" * 90)
    print(" PREDICTIQ v2 — CHECKPOINT R09: NLP & GOLDEN SRS BENCHMARK EVALUATION")
    print("=" * 90)
    print(
        f"Total Golden SRS Documents: {results['sample_size']} across {results['domains_evaluated']} software domains"
    )
    print(
        f"Overall Quality Gate Status: {'[PASS]' if gates['all_gates_pass'] else '[FAIL]'}"
    )
    print("-" * 90)

    print("\n### 1. Mandatory Quality Gates")
    print("| Gate | Criterion | Threshold | Achieved | Status |")
    print("| :--- | :--- | :---: | :---: | :---: |")
    for key, g in gates.items():
        if key == "all_gates_pass":
            continue
        status_str = "PASS" if g["pass"] else "FAIL"
        print(
            f"| {key} | {g.get('threshold', '')} | {g.get('threshold', '')} | {g.get('achieved', '')} | **{status_str}** |"
        )

    print("\n### 2. Overall Performance Metrics")
    print(
        f"- Functional Size MdAPE: {overall['functional_size']['mdape_pct']:.2f}% (MAPE: {overall['functional_size']['mape_pct']:.2f}%, PRED25: {overall['functional_size']['pred25_pct']:.2f}%)"
    )
    print(
        f"- Tech Stack Micro-F1:  {overall['tech_stack']['micro_f1']:.4f} (Precision: {overall['tech_stack']['micro_precision']:.4f}, Recall: {overall['tech_stack']['micro_recall']:.4f})"
    )
    print(
        f"- Integration Count MAE: {overall['integration_count']['mae']:.2f} (Exact: {overall['integration_count']['exact_match_pct']:.2f}%, +/-1: {overall['integration_count']['within_plus_minus_1_pct']:.2f}%)"
    )
    print(
        f"- Feature Recall:        {overall['feature_extraction']['mean_recall_pct']:.2f}% (MdAPE: {overall['feature_extraction']['feature_mdape_pct']:.2f}%)"
    )
    print(
        f"- Complexity Accuracy:   {overall['complexity_classification']['accuracy_pct']:.2f}%"
    )
    print(
        f"- Calibrated Intervals:  {overall['functional_size']['interval_valid_pct']:.2f}% valid non-crossing intervals"
    )

    print("\n### 3. Domain Performance Breakdown")
    print(
        "| Domain | N | Size MdAPE | PRED(25) | Tech Micro-F1 | Integ Exact | Integ +/-1 | Feat Recall |"
    )
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for dom_name, dm in domains.items():
        print(
            f"| {dom_name} | {dm['num_docs']} | {dm['mdape_pct']:.2f}% | {dm['pred25_pct']:.1f}% | {dm['tech_micro_f1']:.4f} | {dm['integration_exact_pct']:.1f}% | {dm['integration_within1_pct']:.1f}% | {dm['feature_recall_pct']:.1f}% |"
        )
    print("-" * 90 + "\n")


if __name__ == "__main__":
    res = evaluate_srs_extractor()
    print_summary_tables(res)
