"""Data quality and integrity tests for PredictIQ dataset v2 (projects_v2.csv).

Verifies:
- Finite positive ranges for size and effort
- Zero NaN in core fields (size_value, effort_hours, source, project_id)
- Empirical productivity bounds per source
- No target-derived or circular features
- Split integrity across leave-one-source-out partitions
- Correct China and Albrecht conversions
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

DATA_FILE = Path(__file__).resolve().parent.parent / "ml" / "data" / "projects_v2.csv"


@pytest.fixture(scope="module")
def df_v2() -> pd.DataFrame:
    assert DATA_FILE.exists(), f"Harmonized dataset not found at {DATA_FILE}"
    df = pd.read_csv(DATA_FILE)
    return df


def test_dataset_v2_row_count_and_columns(df_v2: pd.DataFrame):
    """Verify total row count and exact required schema."""
    assert len(df_v2) == 915, f"Expected 915 projects, got {len(df_v2)}"
    required_cols = [
        "project_id",
        "source",
        "year",
        "size_value",
        "size_unit",
        "effort_hours",
        "duration_months",
        "team_size",
        "platform",
        "language",
        "dev_type",
        "notes",
    ]
    for col in required_cols:
        assert col in df_v2.columns, f"Required column '{col}' missing from projects_v2.csv"


def test_positive_finite_size_and_effort(df_v2: pd.DataFrame):
    """Size and effort must be strictly positive and finite."""
    assert (df_v2["size_value"] > 0).all(), "All size values must be > 0"
    assert np.isfinite(df_v2["size_value"]).all(), "All size values must be finite"
    
    assert (df_v2["effort_hours"] > 0).all(), "All effort hours must be > 0"
    assert np.isfinite(df_v2["effort_hours"]).all(), "All effort hours must be finite"


def test_unique_project_ids(df_v2: pd.DataFrame):
    """Every project record must have a unique identifier."""
    assert df_v2["project_id"].is_unique, "Project IDs in projects_v2 must be unique"


def test_source_representation(df_v2: pd.DataFrame):
    """All 6 approved sources must be represented with exact counts."""
    expected_counts = {
        "china": 499,
        "kitchenham": 145,
        "desharnais": 81,
        "maxwell": 62,
        "att_aptness": 104,
        "albrecht": 24,
    }
    actual_counts = df_v2["source"].value_counts().to_dict()
    assert actual_counts == expected_counts, f"Source distribution mismatch: {actual_counts}"


def test_productivity_ranges_per_source(df_v2: pd.DataFrame):
    """Productivity (hours per FP) must fall within physically plausible software engineering bounds."""
    df_calc = df_v2.copy()
    df_calc["hours_per_fp"] = df_calc["effort_hours"] / df_calc["size_value"]
    
    for source, group in df_calc.groupby("source"):
        med_prod = group["hours_per_fp"].median()
        # Plausible median bounds: 1 to 150 hours per function point across all historical domains
        assert 1.0 <= med_prod <= 150.0, f"Unrealistic median productivity {med_prod:.1f} h/FP for source {source}"
        # Extreme minimum check: at least 0.1 hours/FP
        assert (group["hours_per_fp"] >= 0.1).all(), f"Absurdly low hours/FP found in {source}"


def test_china_label_correctness(df_v2: pd.DataFrame):
    """Verify China project 1 effort is 7490 person-hours, not Resource code 4."""
    china_p1 = df_v2[df_v2["project_id"] == "china_001"]
    assert len(china_p1) == 1, "China project 1 must exist"
    row = china_p1.iloc[0]
    assert row["size_value"] == 1587.0
    assert row["effort_hours"] == 7490.0, f"Expected 7490 hours, got {row['effort_hours']}"


def test_albrecht_thousand_hours_conversion(df_v2: pd.DataFrame):
    """Verify Albrecht effort was converted from thousands of work-hours to person-hours."""
    albrecht = df_v2[df_v2["source"] == "albrecht"]
    assert len(albrecht) == 24
    # Minimum raw effort in Albrecht was 0.5 (500 hours); maximum was 105.2 (105,200 hours)
    assert albrecht["effort_hours"].min() >= 500.0, "Albrecht effort must be multiplied by 1000 to reflect hours"
    assert albrecht["effort_hours"].max() <= 200000.0, "Albrecht effort bounds exceeded"


def test_no_leakage_features(df_v2: pd.DataFrame):
    """Ensure no target-derived features or fabricated metrics are stored in projects_v2."""
    banned_prefixes = ["T0", "T1", "Transactions", "Entities", "PointsNonAdjust", "Adjustment", "TeamExp", "ManagerExp"]
    for col in df_v2.columns:
        for banned in banned_prefixes:
            assert not col.startswith(banned), f"Banned fabricated feature column '{col}' present in dataset"
    assert "productivity" not in df_v2.columns, "Productivity must never be a stored feature"


def test_leave_one_source_out_split_integrity(df_v2: pd.DataFrame):
    """Verify that partitioning by source leaves completely disjoint project sets with no ID overlap."""
    sources = df_v2["source"].unique()
    assert len(sources) == 6
    for holdout_source in sources:
        train_set = df_v2[df_v2["source"] != holdout_source]
        test_set = df_v2[df_v2["source"] == holdout_source]
        train_ids = set(train_set["project_id"])
        test_ids = set(test_set["project_id"])
        assert train_ids.isdisjoint(test_ids), f"LOSO fold for {holdout_source} has overlapping IDs!"
        assert len(train_set) + len(test_set) == len(df_v2)

