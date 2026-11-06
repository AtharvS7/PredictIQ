"""Automated test suite for Track 1 effort estimation models.

Tests strictly enforce:
1. Monotonicity: forall S1 < S2 => E(S1) <= E(S2).
2. Fitting on harmonized projects_v2.csv dataset.
3. Handling of missing covariates without synthetic imputation.
4. Contract compliance: strict prohibition and rejection of banned features (T01-T15, Transactions, etc.).
5. Finite, strictly positive predictions (>= 1.0 hour).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from typing import Any

import numpy as np
import pandas as pd
import pytest

from backend.ml.eval.protocol import load_dataset
from backend.ml.track1 import (
    BANNED_FEATURES,
    MonotonePowerLaw,
    MultivariateMonotoneModel,
    SegmentedMonotoneModel,
    validate_and_extract_inputs,
)


@pytest.fixture
def projects_df() -> pd.DataFrame:
    """Fixture providing loaded harmonized projects_v2.csv dataset."""
    return load_dataset()


# =====================================================================
# 1. Monotonicity Verification Tests
# =====================================================================


def test_monotone_power_law_monotonicity(projects_df: pd.DataFrame) -> None:
    """Verify MonotonePowerLaw produces strictly increasing predictions across size domain."""
    model = MonotonePowerLaw()
    model.fit(projects_df, projects_df["effort_hours"])

    assert model.b_ is not None and model.b_ > 0.0
    assert model.a_ is not None and model.a_ > 0.0

    # Test over dense grid from 1 to 20,000 FP
    sizes = np.linspace(1.0, 20000.0, 2000)
    preds = model.predict(sizes)

    # Invariant: S1 < S2 => E(S1) < E(S2)
    diffs = np.diff(preds)
    assert (diffs > 0.0).all(), "MonotonePowerLaw predictions must be strictly increasing."

    # Analytical derivative must be strictly positive
    derivs = model.derivative(sizes)
    assert (derivs > 0.0).all(), "MonotonePowerLaw derivative dE/dS must be strictly positive."


def test_segmented_monotone_model_monotonicity(projects_df: pd.DataFrame) -> None:
    """Verify SegmentedMonotoneModel is strictly monotonic across all buckets and smoothed boundaries."""
    model = SegmentedMonotoneModel(bucket_cuts=(150.0, 750.0), tau=0.25)
    model.fit(projects_df, projects_df["effort_hours"])

    assert model.b1_ is not None and model.b1_ > 0.0
    assert model.b2_ is not None and model.b2_ > 0.0
    assert model.b3_ is not None and model.b3_ > 0.0

    # 1. Test overall dense grid
    sizes = np.linspace(1.0, 15000.0, 3000)
    preds = model.predict(sizes)
    diffs = np.diff(preds)
    assert (diffs > 0.0).all(), "SegmentedMonotoneModel predictions must be strictly non-decreasing everywhere."

    # 2. Test boundary regions specifically
    # Boundary 1: around 150 FP (140 to 160 FP)
    b1_sizes = np.linspace(140.0, 160.0, 500)
    b1_preds = model.predict(b1_sizes)
    assert (np.diff(b1_preds) > 0.0).all(), "Boundary 1 (150 FP) must be strictly non-decreasing without dip."

    # Boundary 2: around 750 FP (740 to 760 FP)
    b2_sizes = np.linspace(740.0, 760.0, 500)
    b2_preds = model.predict(b2_sizes)
    assert (np.diff(b2_preds) > 0.0).all(), "Boundary 2 (750 FP) must be strictly non-decreasing without dip."

    # 3. Test analytical derivative dE/dS > 0 everywhere
    derivs = model.derivative(sizes)
    assert (derivs > 0.0).all(), "Analytical derivative dE/dS must be strictly positive everywhere."


def test_multivariate_monotone_model_monotonicity(projects_df: pd.DataFrame) -> None:
    """Verify MultivariateMonotoneModel is monotonic with respect to size and duration."""
    model = MultivariateMonotoneModel()
    model.fit(projects_df, projects_df["effort_hours"])

    assert model.b_base_ is not None and model.b_base_ > 0.0
    assert model.b_ is not None and model.b_ > 0.0
    assert model.c_ is not None and model.c_ >= 0.0

    # For fixed duration, predictions must be strictly increasing with size
    for d_val in [3.0, 6.0, 12.0, 24.0]:
        sizes = np.linspace(10.0, 5000.0, 500)
        df_eval = pd.DataFrame({"size_fp": sizes, "duration_months": d_val})
        preds = model.predict(df_eval)
        assert (np.diff(preds) > 0.0).all(), f"Effort must strictly increase with size for D={d_val}"

    # For fixed size, predictions must be non-decreasing with duration (since c >= 0)
    for s_val in [100.0, 500.0, 2000.0]:
        durations = np.linspace(1.0, 48.0, 100)
        df_eval = pd.DataFrame({"size_fp": s_val, "duration_months": durations})
        preds = model.predict(df_eval)
        assert (np.diff(preds) >= 0.0).all(), f"Effort must be non-decreasing with duration for S={s_val}"


# =====================================================================
# 2. Dataset Fitting & Parameter Sanity Tests
# =====================================================================


def test_fitting_on_projects_v2(projects_df: pd.DataFrame) -> None:
    """Verify all Track 1 models fit successfully on projects_v2.csv with realistic parameters."""
    y = projects_df["effort_hours"].to_numpy()

    # Model 1
    mpl = MonotonePowerLaw()
    mpl.fit(projects_df, y)
    assert 1.0 <= mpl.a_ <= 100.0, f"Expected realistic scale parameter a, got {mpl.a_}"
    assert 0.5 <= mpl.b_ <= 1.5, f"Expected realistic software exponent b, got {mpl.b_}"

    # Model 2
    mmm = MultivariateMonotoneModel()
    mmm.fit(projects_df, y)
    assert mmm.has_duration_ is True
    assert 0.5 <= mmm.b_base_ <= 1.5
    assert 0.4 <= mmm.b_ <= 1.2
    assert 0.0 <= mmm.c_ <= 1.2

    # Model 3
    smm = SegmentedMonotoneModel()
    smm.fit(projects_df, y)
    assert 0.4 <= smm.b1_ <= 1.5
    assert 0.4 <= smm.b2_ <= 1.5
    assert 0.4 <= smm.b3_ <= 1.5


# =====================================================================
# 3. Handling of Missing Covariates (Zero Imputation) Tests
# =====================================================================


def test_multivariate_model_missing_covariates_handling(projects_df: pd.DataFrame) -> None:
    """Verify MultivariateMonotoneModel handles missing duration without imputation."""
    y = projects_df["effort_hours"].to_numpy()
    model = MultivariateMonotoneModel()
    model.fit(projects_df, y)

    # Construct test dataframe with a mix of present, NaN, and negative duration
    test_df = pd.DataFrame({
        "size_fp": [100.0, 200.0, 300.0, 400.0],
        "duration_months": [6.0, np.nan, None, -5.0],
    })

    preds = model.predict(test_df)
    assert len(preds) == 4
    assert np.isfinite(preds).all()
    assert (preds >= 1.0).all()

    # For index 0 (valid duration 6.0), should match multivariate formula
    expected_0 = model.a_ * (100.0 ** model.b_) * (6.0 ** model.c_)
    assert np.isclose(preds[0], max(expected_0, 1.0))

    # For indices 1, 2, 3 (missing or invalid duration), should match exact base marginal model
    for idx, s_val in [(1, 200.0), (2, 300.0), (3, 400.0)]:
        expected_base = model.a_base_ * (s_val ** model.b_base_)
        assert np.isclose(preds[idx], max(expected_base, 1.0)), (
            f"Row {idx} with missing duration must evaluate to marginal base model without imputation."
        )


def test_multivariate_model_when_no_duration_in_training() -> None:
    """Verify MultivariateMonotoneModel falls back cleanly when training data has zero duration."""
    train_df = pd.DataFrame({
        "size_fp": [50.0, 100.0, 250.0, 500.0, 1000.0],
    })
    y = np.array([500.0, 950.0, 2300.0, 4400.0, 8500.0])

    model = MultivariateMonotoneModel(min_duration_samples=3)
    model.fit(train_df, y)

    assert model.has_duration_ is False
    assert model.a_ == model.a_base_
    assert model.b_ == model.b_base_

    preds = model.predict(train_df)
    assert len(preds) == 5
    assert (np.diff(preds) > 0.0).all()


# =====================================================================
# 4. ML Contract Compliance: Banned Features Ban Tests
# =====================================================================


@pytest.mark.parametrize("banned_col", list(BANNED_FEATURES)[:10])
def test_contract_compliance_banned_features_rejected(banned_col: str) -> None:
    """Verify that any presence of banned features raises a ValueError contract violation."""
    bad_df = pd.DataFrame({
        "size_fp": [100.0, 200.0],
        banned_col: [1.0, 2.0],
    })
    y = np.array([1000.0, 2000.0])

    models: list[Any] = [
        MonotonePowerLaw(),
        MultivariateMonotoneModel(),
        SegmentedMonotoneModel(),
    ]

    for model in models:
        # Banned column in fit() must raise ValueError
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            model.fit(bad_df, y)

        # Fit with clean data first, then test banned column in predict()
        clean_df = pd.DataFrame({"size_fp": [100.0, 200.0]})
        model.fit(clean_df, y)
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            model.predict(bad_df)


def test_contract_compliance_case_insensitive_banned_detection() -> None:
    """Verify that banned features are detected case-insensitively (e.g. 'T01', 'Risk_Score')."""
    bad_df = pd.DataFrame({
        "size_fp": [150.0],
        "T01": [5.0],
        "Risk_Score": [0.8],
    })
    y = np.array([1200.0])

    with pytest.raises(ValueError, match="ML Contract Violation"):
        MonotonePowerLaw().fit(bad_df, y)


# =====================================================================
# 5. Input Validation & Error Handling Tests
# =====================================================================


def test_validate_and_extract_inputs_invalid_size() -> None:
    """Verify non-positive or non-finite size values are rejected."""
    # Negative size
    with pytest.raises(ValueError, match="strictly positive"):
        validate_and_extract_inputs(np.array([-10.0, 100.0]))

    # Zero size
    with pytest.raises(ValueError, match="strictly positive"):
        validate_and_extract_inputs(np.array([0.0, 100.0]))

    # NaN / Inf size
    with pytest.raises(ValueError, match="strictly positive and finite"):
        validate_and_extract_inputs(np.array([np.nan, 100.0]))


def test_target_validation_mismatched_length() -> None:
    """Verify mismatched sample lengths between X and y raise ValueError."""
    model = MonotonePowerLaw()
    with pytest.raises(ValueError, match="does not match target rows"):
        model.fit(np.array([100.0, 200.0]), np.array([1000.0]))


def test_target_validation_negative_or_zero_effort() -> None:
    """Verify non-positive target effort values raise ValueError."""
    model = MonotonePowerLaw()
    with pytest.raises(ValueError, match="Target effort values must be strictly positive"):
        model.fit(np.array([100.0, 200.0]), np.array([1000.0, -50.0]))


def test_predict_before_fit_raises_runtime_error() -> None:
    """Verify calling predict() before fit() raises RuntimeError."""
    models_to_check: list[Any] = [
        MonotonePowerLaw(),
        MultivariateMonotoneModel(),
        SegmentedMonotoneModel(),
    ]
    for model in models_to_check:
        with pytest.raises(RuntimeError, match="must be fit before predict"):
            model.predict(np.array([100.0]))


# =====================================================================
# 6. Bounds & Positive Output Invariants
# =====================================================================


def test_predictions_strictly_positive_under_extreme_extrapolation() -> None:
    """Verify predictions remain positive, finite, and >= 1.0 even under extreme extrapolation."""
    s = np.array([50.0, 100.0, 500.0])
    y = np.array([500.0, 1000.0, 4500.0])

    models: list[Any] = [
        MonotonePowerLaw(),
        MultivariateMonotoneModel(),
        SegmentedMonotoneModel(),
    ]

    for model in models:
        model.fit(s, y)
        extreme_sizes = np.array([1e-3, 0.1, 1.0, 1e5, 1e7])
        preds = model.predict(extreme_sizes)
        assert np.isfinite(preds).all(), f"Predictions for {model.__class__.__name__} must be finite."
        assert (preds >= 1.0).all(), f"Predictions for {model.__class__.__name__} must be >= 1.0 hour."
