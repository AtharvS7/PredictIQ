"""Automated test suite for Track 2 (Challenger) effort estimation models.

Tests strictly enforce:
1. Monotonicity verification: forall S1 < S2 => E(S1) <= E(S2).
2. Quantile monotonicity: forall x, p10(x) <= p50(x) <= p90(x).
3. Fitting on harmonized projects_v2.csv dataset across all models.
4. Handling of missing covariates (planned duration / team size) without synthetic imputation.
5. Contract compliance: strict prohibition and rejection of banned features (T01-T15, Transactions, etc.).
6. Finite, strictly positive predictions (>= 1.0 hour) even under extreme domain extrapolation.
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
from sklearn.exceptions import NotFittedError

from backend.ml.eval.protocol import load_dataset
from backend.ml.track2 import (
    MonotoneHistGradientBoosting,
    MultivariateHistGradientBoosting,
    QuantileGradientBoosting,
    validate_and_extract_inputs,
)


@pytest.fixture
def projects_df() -> pd.DataFrame:
    """Fixture providing loaded harmonized projects_v2.csv dataset."""
    return load_dataset()


# =====================================================================
# 1. Monotonicity Verification Tests
# =====================================================================


def test_monotone_hist_gradient_boosting_monotonicity(projects_df: pd.DataFrame) -> None:
    """Verify MonotoneHistGradientBoosting produces non-decreasing predictions across size domain."""
    model = MonotoneHistGradientBoosting(random_state=42)
    model.fit(projects_df, projects_df["effort_hours"])

    assert model.estimator_ is not None

    # Test over dense grid from 1 to 20,000 FP
    sizes = np.linspace(1.0, 20000.0, 2000)
    preds = model.predict(sizes)

    # Invariant: S1 < S2 => E(S1) <= E(S2)
    diffs = np.diff(preds)
    assert (diffs >= -1e-9).all(), "MonotoneHistGradientBoosting predictions must be non-decreasing everywhere."


def test_quantile_gradient_boosting_quantile_monotonicity(projects_df: pd.DataFrame) -> None:
    """Verify QuantileGradientBoosting produces non-crossing quantiles: p10 <= p50 <= p90."""
    model = QuantileGradientBoosting(random_state=42)
    model.fit(projects_df, projects_df["effort_hours"])

    assert model.estimators_ is not None

    # 1. Test across the empirical dataset
    q_empirical = model.predict_quantiles(projects_df)
    p10_emp = q_empirical["p10"]
    p50_emp = q_empirical["p50"]
    p90_emp = q_empirical["p90"]

    assert len(p10_emp) == len(projects_df)
    assert (p10_emp <= p50_emp + 1e-6).all(), "Empirical test: p10 must be <= p50 everywhere."
    assert (p50_emp <= p90_emp + 1e-6).all(), "Empirical test: p50 must be <= p90 everywhere."
    assert (p10_emp >= 1.0).all(), "p10 must be >= 1.0 hour."

    # 2. Test over dense synthetic grid
    dense_sizes = np.linspace(1.0, 15000.0, 1500)
    q_grid = model.predict_quantiles(dense_sizes)
    p10_grid = q_grid["p10"]
    p50_grid = q_grid["p50"]
    p90_grid = q_grid["p90"]

    assert (p10_grid <= p50_grid + 1e-6).all(), "Dense grid: p10 must be <= p50 everywhere."
    assert (p50_grid <= p90_grid + 1e-6).all(), "Dense grid: p50 must be <= p90 everywhere."

    # 3. Quantile monotonicity check: p10 <= p50 <= p90 across the entire grid
    assert (p10_grid <= p50_grid).all(), "p10 must be <= p50 across entire grid."
    assert (p50_grid <= p90_grid).all(), "p50 must be <= p90 across entire grid."

    # 4. Standard predict() should return p50
    std_preds = model.predict(dense_sizes)
    np.testing.assert_allclose(std_preds, p50_grid, rtol=1e-7)


def test_multivariate_hist_gradient_boosting_size_monotonicity(projects_df: pd.DataFrame) -> None:
    """Verify MultivariateHistGradientBoosting maintains positive size monotonicity at fixed duration."""
    model = MultivariateHistGradientBoosting(random_state=42)
    model.fit(projects_df, projects_df["effort_hours"])

    assert model.base_estimator_ is not None
    assert model.has_interaction_ is True

    sizes = np.linspace(5.0, 5000.0, 500)

    # Test at several fixed duration levels
    for fixed_dur in [3.0, 6.0, 12.0, 24.0]:
        test_df = pd.DataFrame({
            "size_value": sizes,
            "duration_months": np.full_like(sizes, fixed_dur),
        })
        preds = model.predict(test_df)
        diffs = np.diff(preds)
        assert (diffs >= -1e-9).all(), f"Multivariate model must be non-decreasing in size at duration={fixed_dur}"


# =====================================================================
# 2. Dataset Fitting & Zero-Imputation Tests
# =====================================================================


def test_fitting_on_projects_v2(projects_df: pd.DataFrame) -> None:
    """Verify all Track 2 candidate models fit on projects_v2.csv and yield valid predictions."""
    models: list[Any] = [
        MonotoneHistGradientBoosting(loss="squared_error"),
        MonotoneHistGradientBoosting(loss="absolute_error", target_log=False),
        QuantileGradientBoosting(),
        MultivariateHistGradientBoosting(),
    ]

    y = projects_df["effort_hours"].to_numpy()

    for model in models:
        model.fit(projects_df, y)
        preds = model.predict(projects_df)

        assert len(preds) == len(projects_df)
        assert np.isfinite(preds).all(), f"{model.__class__.__name__} produced non-finite predictions."
        assert (preds >= 1.0).all(), f"{model.__class__.__name__} produced predictions < 1.0 hour."


def test_multivariate_handling_of_missing_duration(projects_df: pd.DataFrame) -> None:
    """Verify MultivariateHistGradientBoosting falls back to base model when duration is missing."""
    model = MultivariateHistGradientBoosting(random_state=42)
    model.fit(projects_df, projects_df["effort_hours"])

    # Create test samples: some with duration, some with NaN duration, some with 0 duration
    test_df = pd.DataFrame({
        "size_value": [50.0, 100.0, 200.0, 500.0],
        "duration_months": [np.nan, 6.0, 0.0, -1.0],
    })

    preds = model.predict(test_df)
    assert len(preds) == 4
    assert np.isfinite(preds).all()
    assert (preds >= 1.0).all()

    # For sample 0 (NaN duration), sample 2 (0.0 duration), sample 3 (-1.0 duration),
    # predictions must match base estimator predictions on size alone
    assert model.base_estimator_ is not None
    base_preds = model.base_estimator_.predict(np.array([[50.0], [200.0], [500.0]]))
    if model.target_log:
        expected_base = np.exp(base_preds)
    else:
        expected_base = base_preds

    np.testing.assert_allclose(preds[[0, 2, 3]], expected_base, rtol=1e-5)


def test_multivariate_when_no_duration_in_training() -> None:
    """Verify MultivariateHistGradientBoosting operates safely when no duration is in training data."""
    synth_df = pd.DataFrame({
        "size_value": [50.0, 150.0, 300.0, 600.0, 1200.0],
        "effort_hours": [500.0, 1200.0, 2500.0, 4800.0, 9500.0],
    })

    model = MultivariateHistGradientBoosting(min_covariate_samples=5)
    model.fit(synth_df, synth_df["effort_hours"])

    assert model.has_interaction_ is False
    assert model.interaction_estimator_ is None

    preds = model.predict(synth_df)
    assert len(preds) == 5
    assert (preds >= 1.0).all()


# =====================================================================
# 3. Contract Compliance Tests (Banned Features Prohibition)
# =====================================================================


@pytest.mark.parametrize("banned_col", [
    "t01", "t04", "t05", "t08", "t10", "t12", "t13", "t14",
    "transactions", "entities", "pointsnonadjust", "adjustment",
    "teamexp", "managerexp", "risk_score"
])
def test_contract_compliance_banned_features_rejected(
    projects_df: pd.DataFrame,
    banned_col: str,
) -> None:
    """Verify all Track 2 models reject DataFrames containing contract-banned features."""
    tainted_df = projects_df.copy()
    tainted_df[banned_col] = 1.0

    models: list[Any] = [
        MonotoneHistGradientBoosting(),
        QuantileGradientBoosting(),
        MultivariateHistGradientBoosting(),
    ]

    for model in models:
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            model.fit(tainted_df, tainted_df["effort_hours"])

        # Also test on predict
        clean_model: Any = model.__class__()
        clean_model.fit(projects_df, projects_df["effort_hours"])
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            clean_model.predict(tainted_df)


def test_contract_compliance_case_insensitive_detection(projects_df: pd.DataFrame) -> None:
    """Verify banned feature detection is strictly case-insensitive."""
    tainted_df = projects_df.copy()
    tainted_df["Risk_Score"] = 0.85

    model = MonotoneHistGradientBoosting()
    with pytest.raises(ValueError, match="ML Contract Violation"):
        model.fit(tainted_df, tainted_df["effort_hours"])


def test_validate_and_extract_inputs_invalid_size() -> None:
    """Verify validate_and_extract_inputs raises ValueError on invalid size values."""
    with pytest.raises(ValueError, match="strictly positive and finite"):
        validate_and_extract_inputs(np.array([10.0, -5.0, 20.0]))

    with pytest.raises(ValueError, match="strictly positive and finite"):
        validate_and_extract_inputs(np.array([10.0, 0.0, 20.0]))

    with pytest.raises(ValueError, match="strictly positive and finite"):
        validate_and_extract_inputs(np.array([10.0, np.nan, 20.0]))

    with pytest.raises(ValueError, match="cannot be empty"):
        validate_and_extract_inputs(np.array([]))


def test_target_validation() -> None:
    """Verify target checks reject invalid y targets."""
    model = MonotoneHistGradientBoosting()
    X = np.array([[10.0], [20.0], [30.0]])

    with pytest.raises(ValueError, match="does not match target rows"):
        model.fit(X, np.array([100.0, 200.0]))

    with pytest.raises(ValueError, match="strictly positive and finite"):
        model.fit(X, np.array([100.0, -50.0, 300.0]))

    with pytest.raises(ValueError, match="strictly positive and finite"):
        model.fit(X, np.array([100.0, 0.0, 300.0]))


def test_predict_before_fit_raises_not_fitted_error() -> None:
    """Verify predict on unfitted model raises NotFittedError."""
    m1 = MonotoneHistGradientBoosting()
    with pytest.raises(NotFittedError):
        m1.predict(np.array([100.0]))

    m2 = QuantileGradientBoosting()
    with pytest.raises(NotFittedError):
        m2.predict(np.array([100.0]))
    with pytest.raises(NotFittedError):
        m2.predict_quantiles(np.array([100.0]))

    m3 = MultivariateHistGradientBoosting()
    with pytest.raises(NotFittedError):
        m3.predict(np.array([100.0]))


def test_predictions_strictly_positive_under_extreme_extrapolation(
    projects_df: pd.DataFrame,
) -> None:
    """Verify predictions remain positive and finite (>= 1.0 hour) under extreme extrapolation."""
    models: list[Any] = [
        MonotoneHistGradientBoosting(),
        QuantileGradientBoosting(),
        MultivariateHistGradientBoosting(),
    ]

    for model in models:
        model.fit(projects_df, projects_df["effort_hours"])

        extreme_sizes = np.array([0.001, 0.01, 0.1, 100000.0, 500000.0])
        preds = model.predict(extreme_sizes)

        assert (preds >= 1.0).all()
        assert np.isfinite(preds).all()
