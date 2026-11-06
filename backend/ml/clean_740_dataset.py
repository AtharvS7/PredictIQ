"""Clean the 481 corrupted China rows in the 740-row dataset."""
import hashlib
import sys
from pathlib import Path

ML_DIR = Path(r"E:\Codex\PredictIQ-dev\backend\ml")
sys.path.insert(0, str(ML_DIR.parent))

import numpy as np
import pandas as pd

from ml.artifact_safety import REVOKED_DATA_SHA256
from ml.rebuild_dataset import audit_legacy, read_source

BACKUP_CSV = Path(r"E:\Codex\PredictIQ-dev\.tools\dev2-backup\backend\ml\predictiq_merged_dataset.csv")
CHINA_ARFF = ML_DIR / "data" / "research" / "china.arff"

legacy = pd.read_csv(BACKUP_CSV)
china = read_source(CHINA_ARFF)
source = china.apply(pd.to_numeric, errors="raise")

# Build lookup
lookup = {}
for _, row in source.iterrows():
    key = (row.AFP, row.Input + row.Output + row.Enquiry, row.File + row.Interface)
    lookup.setdefault(key, []).append(row)

fixed_count = 0
for index, row in legacy.iterrows():
    matches = lookup.get((row.size_fp, row.Transactions, row.Entities), [])
    bad = [r for r in matches if row.effort_hours == r.Resource and r.Effort != r.Resource]
    if bad:
        correct_effort = float(bad[0].Effort)
        legacy.at[index, "effort_hours"] = correct_effort
        legacy.at[index, "log_effort"] = np.log1p(correct_effort)
        legacy.at[index, "effort_per_fp"] = correct_effort / max(1.0, float(row.size_fp))
        fixed_count += 1

print(f"Fixed {fixed_count} corrupted China rows in 740-row dataset!")

# Verify audit now reports 0 wrong legacy labels
audit = audit_legacy(legacy, china)
print("Audit after fix:", audit["resource_codes_used_as_hours"], "wrong labels")
assert audit["resource_codes_used_as_hours"] == 0, "Still has wrong labels!"

# Ensure exact 30-column order
expected_columns = [
    "TeamExp", "ManagerExp", "duration_months", "effort_hours",
    "Transactions", "Entities", "PointsNonAdjust", "Adjustment", "size_fp",
    "T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09",
    "T10", "T11", "T12", "T13", "T14", "T15",
    "effort_per_fp", "log_size_fp", "log_effort",
    "complexity_score", "team_skill_avg", "risk_score",
]
legacy = legacy[expected_columns]

# Ensure derived features match formulas
for col in ["complexity_score", "team_skill_avg", "risk_score"]:
    if col == "complexity_score":
        legacy[col] = (legacy["T07"] + legacy["T10"] + legacy["T11"]) / 3
    elif col == "team_skill_avg":
        legacy[col] = (legacy["T12"] + legacy["T13"] + legacy["T14"] + legacy["T15"]) / 4
    elif col == "risk_score":
        legacy[col] = (legacy["T08"] + legacy["T09"]) / 2

legacy["log_effort"] = np.log1p(legacy["effort_hours"])
legacy["log_size_fp"] = np.log1p(legacy["size_fp"])
legacy["effort_per_fp"] = legacy["effort_hours"] / legacy["size_fp"].clip(lower=1)

# Write to backend/ml/predictiq_merged_dataset.csv
out_path = ML_DIR / "predictiq_merged_dataset.csv"
legacy.to_csv(out_path, index=False, lineterminator="\n")

sha256 = hashlib.sha256(out_path.read_bytes()).hexdigest()
print(f"Saved cleaned 740-row dataset to {out_path}")
print(f"SHA-256: {sha256}")
print(f"Is in REVOKED_DATA_SHA256: {sha256 in REVOKED_DATA_SHA256}")
assert sha256 not in REVOKED_DATA_SHA256, "Hash is still in revoked list!"
print("SUCCESS: Clean 740-row dataset generated with unrevoked hash!")
