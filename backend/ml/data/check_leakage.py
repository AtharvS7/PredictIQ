"""
PredictIQ v2 - Dataset Leakage & Data Quality Audit Tool
Audits backend/ml/data/projects_v2.csv against feature leakage, target leakage,
source leakage, duplicate keys, and temporal consistency.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def audit_dataset_leakage(data_path: Path) -> dict:
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    # Compute sha256
    sha256 = hashlib.sha256(data_path.read_bytes()).hexdigest()
    df = pd.read_csv(data_path)

    results = {
        "dataset_path": str(data_path),
        "sha256": sha256,
        "total_rows": len(df),
        "columns": list(df.columns),
        "checks": {},
        "status": "PASS",
    }

    # 1. Banned fabricated features
    banned_features = [
        "T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09", "T10",
        "T11", "T12", "T13", "T14", "T15",
        "Transactions", "Entities", "PointsNonAdjust", "Adjustment",
        "TeamExp", "ManagerExp", "productivity", "risk_score",
    ]
    present_banned = [col for col in df.columns if any(col.startswith(b) for b in banned_features)]
    results["checks"]["banned_features"] = {
        "passed": len(present_banned) == 0,
        "present_banned": present_banned,
    }

    # 2. Duplicate keys & Cross-source duplicate rows
    duplicate_ids = int(df["project_id"].duplicated().sum())
    cross_source_duplicates = int(
        df.duplicated(subset=["size_value", "effort_hours", "duration_months"], keep=False).sum()
    )
    results["checks"]["duplicate_keys"] = {
        "passed": duplicate_ids == 0,
        "duplicate_ids_count": duplicate_ids,
        "duplicate_tuples_count": cross_source_duplicates,
    }

    # 3. Target leakage and single-feature correlation against effort_hours
    target = df["effort_hours"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    feature_correlations = {}
    suspicious_features = []

    for col in numeric_cols:
        if col in ["effort_hours", "year"]:
            continue
        valid_mask = df[col].notna() & target.notna()
        if valid_mask.sum() > 10:
            corr = float(np.corrcoef(df.loc[valid_mask, col], target.loc[valid_mask])[0, 1])
            r2 = float(corr ** 2)
            feature_correlations[col] = {"correlation": round(corr, 4), "r2": round(r2, 4)}
            # Suspicious if feature has near-perfect correlation (> 0.98) unless expected like duration or size
            if r2 > 0.98 and col not in ["size_value", "duration_months"]:
                suspicious_features.append(col)

    results["checks"]["target_leakage"] = {
        "passed": len(suspicious_features) == 0,
        "feature_correlations_with_effort": feature_correlations,
        "suspicious_features": suspicious_features,
    }

    # 4. Temporal consistency
    years = df["year"].dropna()
    year_min = int(years.min()) if len(years) > 0 else None
    year_max = int(years.max()) if len(years) > 0 else None
    results["checks"]["temporal_audit"] = {
        "passed": (year_min is None or (1970 <= year_min <= 2025)) and (year_max is None or (1970 <= year_max <= 2025)),
        "year_min": year_min,
        "year_max": year_max,
        "missing_years": int(df["year"].isna().sum()),
    }

    # 5. Outlier and sanity validation
    prod = df["effort_hours"] / df["size_value"]
    results["checks"]["productivity_sanity"] = {
        "passed": bool((prod > 0).all() and (prod < 1000.0).all()),
        "min_h_per_fp": round(float(prod.min()), 2),
        "median_h_per_fp": round(float(prod.median()), 2),
        "max_h_per_fp": round(float(prod.max()), 2),
    }

    # Overall status
    all_passed = all(bool(check.get("passed", False)) for check in results["checks"].values())
    results["status"] = "PASS" if all_passed else "FAIL"

    return results


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    dataset_file = repo_root / "backend" / "ml" / "data" / "projects_v2.csv"
    report = audit_dataset_leakage(dataset_file)
    print("================================================================================")
    print("DATASET LEAKAGE AUDIT REPORT")
    print("================================================================================")
    print(json.dumps(report, indent=2))
    print("================================================================================")

    output_report_path = repo_root / "docs" / "evidence" / "leakage_audit_report.json"
    output_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Audit report saved to: {output_report_path}")

    if report["status"] != "PASS":
        raise SystemExit(1)
