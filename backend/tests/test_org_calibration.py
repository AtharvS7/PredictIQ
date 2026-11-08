"""Test suite for Empirical Bayes Organization Calibration (Checkpoint S06)."""

from __future__ import annotations

import math

import numpy as np
from app.services.org_calibration import (
    OrgCalibrationService,
)


def test_org_calibration_k_zero():
    """k=0 projects returns uncalibrated global baseline parameters."""
    service = OrgCalibrationService()
    res = service.calibrate([])
    assert res.k_projects == 0
    assert res.shrinkage_weight == 0.0
    assert math.isclose(res.calibrated_a, service.a_global, rel_tol=1e-3)
    assert res.scaling_ratio == 1.0


def test_org_calibration_shrinkage_weight_monotonicity():
    """Shrinkage weight w strictly increases with k towards 1.0."""
    service = OrgCalibrationService()
    k_vals = [1, 2, 3, 5, 10, 20, 50, 100]
    weights = [service.compute_shrinkage_weight(k) for k in k_vals]

    for i in range(len(weights) - 1):
        assert weights[i] < weights[i + 1], f"Weight at k={k_vals[i]} not less than k={k_vals[i+1]}"

    for w in weights:
        assert 0.0 < w < 1.0


def test_org_calibration_slope_preserved():
    """Size elasticity exponent b must remain strictly identical to global b."""
    service = OrgCalibrationService(b_global=0.827)
    sample_data = [
        {"size_fp": 100.0, "actual_hours": 1500.0},
        {"size_fp": 250.0, "actual_hours": 3200.0},
        {"size_fp": 500.0, "actual_hours": 6000.0},
    ]
    res = service.calibrate(sample_data)
    assert math.isclose(res.exponent_b, 0.827, rel_tol=1e-5)


def test_org_calibration_direction_of_shift():
    """Higher productivity org (fewer hours) shifts a downward; lower productivity shifts upward."""
    service = OrgCalibrationService()

    # Fast org (low effort)
    fast_data = [
        {"size_fp": 100.0, "actual_hours": 300.0},
        {"size_fp": 200.0, "actual_hours": 600.0},
        {"size_fp": 500.0, "actual_hours": 1200.0},
    ]
    fast_res = service.calibrate(fast_data)
    assert fast_res.calibrated_a < service.a_global
    assert fast_res.scaling_ratio < 1.0

    # Slow org (high effort)
    slow_data = [
        {"size_fp": 100.0, "actual_hours": 3000.0},
        {"size_fp": 200.0, "actual_hours": 6000.0},
        {"size_fp": 500.0, "actual_hours": 15000.0},
    ]
    slow_res = service.calibrate(slow_data)
    assert slow_res.calibrated_a > service.a_global
    assert slow_res.scaling_ratio > 1.0


def test_apply_calibration_monotonicity_guarantee():
    """Scaling predicted quantiles strictly preserves non-crossing: 1.0 <= p10 <= p25 <= p50 <= p75 <= p90."""
    service = OrgCalibrationService()

    base_quantiles = {
        "p10": np.array([50.0, 200.0, 1000.0]),
        "p25": np.array([80.0, 350.0, 1800.0]),
        "p50": np.array([120.0, 500.0, 2500.0]),
        "p75": np.array([180.0, 750.0, 3800.0]),
        "p90": np.array([280.0, 1200.0, 6000.0]),
    }

    # Test scaling up
    scaled_up = service.apply_calibration(base_quantiles, scaling_ratio=1.45)
    assert np.all(scaled_up["p10"] >= 1.0)
    assert np.all(scaled_up["p10"] <= scaled_up["p25"])
    assert np.all(scaled_up["p25"] <= scaled_up["p50"])
    assert np.all(scaled_up["p50"] <= scaled_up["p75"])
    assert np.all(scaled_up["p75"] <= scaled_up["p90"])

    # Test scaling down
    scaled_down = service.apply_calibration(base_quantiles, scaling_ratio=0.65)
    assert np.all(scaled_down["p10"] >= 1.0)
    assert np.all(scaled_down["p10"] <= scaled_down["p25"])
    assert np.all(scaled_down["p25"] <= scaled_down["p50"])
    assert np.all(scaled_down["p50"] <= scaled_down["p75"])
    assert np.all(scaled_down["p75"] <= scaled_down["p90"])
