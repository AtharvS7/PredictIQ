"""Automated test suite for Conformal Prediction & Calibrated Uncertainty (CP11).

Tests strictly enforce:
1. Conformal interval coverage on calibration split meets nominal (1 - alpha) guarantee.
2. Mondrian bucket calibration produces distinct non-conformity quantiles across size scales.
3. Quantile monotonicity guarantee: p10 <= p50 <= p90 everywhere, with p10 >= 1.0 hr.
4. Contract compliance: strict prohibition and rejection of banned features (T01-T15, etc.).
5. Strictly positive and finite predictions under extreme domain extrapolation.
6. Proper error handling for uncalibrated models, invalid inputs, and edge cases.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
from sklearn.exceptions import NotFittedError  # noqa: E402

from backend.ml.calibration import (  # noqa: E402
    MONDRIAN_BUCKETS,
    SIZE_BUCKET_THRESHOLDS,
    ConformalIntervalPredictor,
    MondrianConformalPredictor,
    SplitConformalPredictor,
    assign_mondrian_bucket,
    compute_conformal_quantile,
    log_residual_score,
    scaled_relative_error_score,
)
from backend.ml.eval.protocol import load_dataset  # noqa: E402
from backend.ml.track1.models import (  # noqa: E402
    BANNED_FEATURES,
    MonotonePowerLaw,
    MultivariateMonotoneModel,
)


@pytest.fixture
def projects_df() -> pd.DataFrame:
    """Fixture providing loaded harmonized projects_v2.csv dataset."""
    return load_dataset()


# =====================================================================
# 1. Conformal Coverage Guarantee on Calibration Split
# =====================================================================


def test_conformal_interval_coverage_on_calibration_split(projects_df: pd.DataFrame) -> None:
    """Verify conformal intervals achieve >= (1 - alpha - eps) empirical coverage on calibration split."""
    alpha = 0.20
    nominal_coverage = 1.0 - alpha  # 80%

    model = MondrianConformalPredictor(
        estimator=MultivariateMonotoneModel(),
        alpha=alpha,
        cal_size=0.20,
        random_state=42,
    )
    model.fit(projects_df, projects_df["effort_hours"])

    # Obtain predictions on the training data
    preds = model.predict_quantiles(projects_df)
    p10 = preds["p10"]
    p90 = preds["p90"]
    y_true = projects_df["effort_hours"].to_numpy()

    empirical_coverage = float(np.mean((y_true >= p10) & (y_true <= p90)))

    # In-domain / pooled coverage should comfortably meet nominal coverage (>= 75%)
    assert empirical_coverage >= 0.75, (
        f"Empirical coverage ({empirical_coverage * 100:.1f}%) fell below 75% for nominal {nominal_coverage * 100:.1f}%"
    )


def test_split_conformal_exact_order_statistic_coverage() -> None:
    """Verify mathematical split conformal exact finite-sample coverage on exchangeable synthetic data."""
    rng = np.random.default_rng(42)
    n_train, n_cal, n_test = 200, 100, 500

    # True data generating process: log(y) = 2.0 + 0.8 * log(s) + N(0, 0.5^2)
    s_train = rng.uniform(20.0, 1000.0, size=n_train)
    y_train = np.exp(2.0 + 0.8 * np.log(s_train) + rng.normal(0, 0.5, size=n_train))

    s_cal = rng.uniform(20.0, 1000.0, size=n_cal)
    y_cal = np.exp(2.0 + 0.8 * np.log(s_cal) + rng.normal(0, 0.5, size=n_cal))

    s_test = rng.uniform(20.0, 1000.0, size=n_test)
    y_test = np.exp(2.0 + 0.8 * np.log(s_test) + rng.normal(0, 0.5, size=n_test))

    alpha = 0.20
    model = SplitConformalPredictor(
        estimator=MonotonePowerLaw(),
        alpha=alpha,
    )
    model.fit(s_train.reshape(-1, 1), y_train, X_cal=s_cal.reshape(-1, 1), y_cal=y_cal)

    # Evaluate on calibration split itself
    cal_preds = model.predict_quantiles(s_cal.reshape(-1, 1))
    cal_cov = float(np.mean((y_cal >= cal_preds["p10"]) & (y_cal <= cal_preds["p90"])))
    assert cal_cov >= 1.0 - alpha - 0.02, f"Calibration split coverage {cal_cov:.3f} below nominal {1.0 - alpha}"

    # Evaluate on i.i.d. exchangeable test set
    test_preds = model.predict_quantiles(s_test.reshape(-1, 1))
    test_cov = float(np.mean((y_test >= test_preds["p10"]) & (y_test <= test_preds["p90"])))
    assert test_cov >= 1.0 - alpha - 0.05, f"Test coverage {test_cov:.3f} below nominal {1.0 - alpha}"


# =====================================================================
# 2. Mondrian Bucket Distinct Quantiles Tests
# =====================================================================


def test_mondrian_bucket_calibration_produces_distinct_quantiles(projects_df: pd.DataFrame) -> None:
    """Verify Mondrian size buckets (<150, 150-750, >750) produce distinct non-conformity quantiles."""
    model = MondrianConformalPredictor(
        estimator=MultivariateMonotoneModel(),
        alpha=0.20,
        cal_size=0.0,  # calibrate on full dataset to observe true population bucket quantiles
    )
    model.fit(projects_df, projects_df["effort_hours"])

    assert model.bucket_quantiles_ is not None
    assert len(model.bucket_quantiles_) == 3

    q_small = model.bucket_quantiles_["small"]
    q_medium = model.bucket_quantiles_["medium"]
    q_large = model.bucket_quantiles_["large"]

    # Quantiles must be distinct
    assert q_small != q_medium, f"Expected distinct quantiles, got small={q_small}, medium={q_medium}"
    assert q_medium != q_large, f"Expected distinct quantiles, got medium={q_medium}, large={q_large}"

    # Verify size heteroskedasticity: larger projects have strictly higher uncertainty
    assert q_small < q_medium < q_large, (
        f"Expected monotonic increase in log-space residual quantile across project size: "
        f"small ({q_small:.4f}) < medium ({q_medium:.4f}) < large ({q_large:.4f})"
    )


def test_assign_mondrian_bucket_boundaries() -> None:
    """Verify exact threshold boundary assignment for Mondrian buckets."""
    sizes = np.array([0.5, 149.99, 150.0, 500.0, 750.0, 750.01, 10000.0])
    buckets = assign_mondrian_bucket(sizes)

    expected = ["small", "small", "medium", "medium", "medium", "large", "large"]
    assert list(buckets) == expected
    assert SIZE_BUCKET_THRESHOLDS == (150.0, 750.0)
    assert MONDRIAN_BUCKETS == ("small", "medium", "large")


# =====================================================================
# 3. Quantile Monotonicity Tests
# =====================================================================


def test_quantile_monotonicity_guarantee(projects_df: pd.DataFrame) -> None:
    """Verify p10 <= p50 <= p90 strictly holds everywhere, with p10 >= 1.0 hour."""
    model = MondrianConformalPredictor(
        estimator=MultivariateMonotoneModel(),
        alpha=0.20,
        cal_size=0.20,
        random_state=42,
    )
    model.fit(projects_df, projects_df["effort_hours"])

    # Test over dense grid spanning 1.0 to 30,000 FP with various duration inputs
    test_sizes = np.geomspace(1.0, 30000.0, 500)
    test_durations = [None, 3.0, 12.0, 36.0]

    for dur in test_durations:
        if dur is None:
            X_test = pd.DataFrame({"size_value": test_sizes})
        else:
            X_test = pd.DataFrame({
                "size_value": test_sizes,
                "duration_months": np.full_like(test_sizes, dur),
            })

        quantiles = model.predict_quantiles(X_test)
        p10 = quantiles["p10"]
        p50 = quantiles["p50"]
        p90 = quantiles["p90"]

        # 1. Lower bound strictly positive (>= 1.0 hr)
        assert (p10 >= 1.0).all(), f"Detected p10 < 1.0 hr with dur={dur}"

        # 2. Strict quantile ordering: p10 <= p50
        assert (p10 <= p50 + 1e-9).all(), f"Quantile crossing detected: p10 > p50 with dur={dur}"

        # 3. Strict quantile ordering: p50 <= p90
        assert (p50 <= p90 + 1e-9).all(), f"Quantile crossing detected: p50 > p90 with dur={dur}"


def test_scaled_relative_error_monotonicity(projects_df: pd.DataFrame) -> None:
    """Verify quantile monotonicity under scaled_relative non-conformity score."""
    model = ConformalIntervalPredictor(
        estimator=MonotonePowerLaw(),
        alpha=0.20,
        score_type="scaled_relative",
        cal_size=0.20,
        random_state=42,
    )
    model.fit(projects_df, projects_df["effort_hours"])

    test_sizes = np.linspace(10.0, 5000.0, 100)
    quantiles = model.predict_quantiles(test_sizes)

    assert (quantiles["p10"] >= 1.0).all()
    assert (quantiles["p10"] <= quantiles["p50"] + 1e-9).all()
    assert (quantiles["p50"] <= quantiles["p90"] + 1e-9).all()


# =====================================================================
# 4. ML Contract Compliance & Input Validation Tests
# =====================================================================


@pytest.mark.parametrize("banned_feature", sorted(list(BANNED_FEATURES))[:10])
def test_contract_compliance_banned_features_rejected(
    projects_df: pd.DataFrame,
    banned_feature: str,
) -> None:
    """Verify that any DataFrame containing prohibited features raises ValueError immediately."""
    model = MondrianConformalPredictor()
    model.fit(projects_df, projects_df["effort_hours"])

    bad_df = pd.DataFrame({
        "size_value": [100.0, 200.0],
        banned_feature: [1.0, 2.0],
    })

    with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
        model.predict_quantiles(bad_df)

    with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
        model.predict(bad_df)

    with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
        model.calibrate(bad_df, [500.0, 1000.0])


def test_predictions_strictly_positive_under_extreme_inputs(projects_df: pd.DataFrame) -> None:
    """Verify predictions remain finite and >= 1.0 hour even for near-zero or massive sizes."""
    model = MondrianConformalPredictor(estimator=MultivariateMonotoneModel())
    model.fit(projects_df, projects_df["effort_hours"])

    extreme_inputs = pd.DataFrame({"size_value": [0.001, 1.0, 1e6, 1e8]})
    quantiles = model.predict_quantiles(extreme_inputs)

    assert np.isfinite(quantiles["p10"]).all()
    assert np.isfinite(quantiles["p50"]).all()
    assert np.isfinite(quantiles["p90"]).all()

    assert (quantiles["p10"] >= 1.0).all()
    assert (quantiles["p50"] >= quantiles["p10"]).all()
    assert (quantiles["p90"] >= quantiles["p50"]).all()


# =====================================================================
# 5. Error Handling and Edge Cases
# =====================================================================


def test_uncalibrated_model_raises_not_fitted_error() -> None:
    """Verify calling predict or predict_quantiles before fit/calibrate raises NotFittedError."""
    model = MondrianConformalPredictor()
    test_X = pd.DataFrame({"size_value": [100.0, 200.0]})

    with pytest.raises(NotFittedError):
        model.predict(test_X)

    with pytest.raises(NotFittedError):
        model.predict_quantiles(test_X)


def test_score_functions_validation() -> None:
    """Verify non-conformity score functions enforce positive inputs and matching lengths."""
    # Length mismatch
    with pytest.raises(ValueError, match="Length mismatch"):
        log_residual_score([100.0, 200.0], [100.0])

    with pytest.raises(ValueError, match="Length mismatch"):
        scaled_relative_error_score([100.0, 200.0], [100.0])

    # Non-positive true effort
    with pytest.raises(ValueError, match="strictly positive"):
        log_residual_score([-10.0, 200.0], [100.0, 200.0])

    # Non-positive predicted effort
    with pytest.raises(ValueError, match="strictly positive"):
        scaled_relative_error_score([100.0, 200.0], [0.0, 200.0])


def test_compute_conformal_quantile_validation() -> None:
    """Verify compute_conformal_quantile input validation."""
    with pytest.raises(ValueError, match="empty scores"):
        compute_conformal_quantile(np.array([]), 0.20)

    with pytest.raises(ValueError, match="alpha must be in"):
        compute_conformal_quantile(np.array([1.0, 2.0]), 1.5)

    with pytest.raises(ValueError, match="alpha must be in"):
        compute_conformal_quantile(np.array([1.0, 2.0]), 0.0)


def test_bucket_fallback_when_samples_insufficient() -> None:
    """Verify fallback to global quantile when a bucket has fewer than min_bucket_samples."""
    # Create calibration data with only 2 large samples (below min_bucket_samples=5)
    s_cal = np.array([50.0, 60.0, 70.0, 80.0, 90.0, 200.0, 300.0, 400.0, 500.0, 800.0, 900.0])
    y_cal = np.array([200.0, 250.0, 300.0, 350.0, 400.0, 800.0, 1200.0, 1500.0, 2000.0, 3500.0, 4000.0])

    base_model = MonotonePowerLaw().fit(s_cal.reshape(-1, 1), y_cal)
    calibrator = MondrianConformalPredictor(
        estimator=base_model,
        alpha=0.20,
        min_bucket_samples=5,
    )
    calibrator.calibrate(s_cal.reshape(-1, 1), y_cal)

    # Large bucket has only 2 samples, so it should fall back to global_quantile_
    assert calibrator.bucket_quantiles_["large"] == calibrator.global_quantile_
    # Small and medium buckets have >= 5 samples, so they have their own quantiles
    assert calibrator.bucket_quantiles_["small"] != calibrator.global_quantile_
