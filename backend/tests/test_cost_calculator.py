"""
Predictify — Cost Calculator Tests
Tests for IFPUG function point estimation and cost conversion.
"""
import pytest
from app.services.cost_calculator import (
    estimate_function_points,
    calculate_cost,
    calculate_timeline,
    calculate_phase_breakdown,
)


class TestFunctionPointEstimation:
    """Tests for the IFPUG function point estimator."""

    def test_fp_small_project(self):
        """Small/Low project should produce modest FP count."""
        fp = estimate_function_points(feature_count=5, complexity="Low")
        assert 50 <= fp <= 200

    def test_fp_large_project(self):
        """Large/Very High project should produce high FP count."""
        fp = estimate_function_points(feature_count=40, complexity="Very High")
        assert fp > 300

    def test_fp_increases_with_complexity(self):
        """Higher complexity should yield more function points."""
        fp_low = estimate_function_points(feature_count=10, complexity="Low")
        fp_med = estimate_function_points(feature_count=10, complexity="Medium")
        fp_high = estimate_function_points(feature_count=10, complexity="High")
        assert fp_low < fp_med < fp_high

    def test_fp_increases_with_features(self):
        """More features should yield more function points."""
        fp_5 = estimate_function_points(feature_count=5, complexity="Medium")
        fp_20 = estimate_function_points(feature_count=20, complexity="Medium")
        assert fp_5 < fp_20

    def test_fp_is_positive(self):
        """Function points must always be positive."""
        fp = estimate_function_points(feature_count=1, complexity="Low")
        assert fp > 0

    def test_fp_clamped_upper(self):
        """Function points should be clamped to max 3000."""
        fp = estimate_function_points(feature_count=200, complexity="Very High")
        assert fp <= 3000

    def test_fp_clamped_lower(self):
        """Function points should be at least 50."""
        fp = estimate_function_points(feature_count=1, complexity="Low")
        assert fp >= 50


class TestCostCalculation:
    """Tests for the parametric cost converter."""

    def test_cost_basic_math(self):
        """Cost should equal effort × hourly rate."""
        costs = calculate_cost(1000, 800, 1200, 100.0)
        assert costs["cost_likely_usd"] == 100000.0

    def test_cost_min_less_than_likely(self):
        """Minimum cost should be less than likely cost."""
        costs = calculate_cost(1000, 800, 1200, 75.0)
        assert costs["cost_min_usd"] < costs["cost_likely_usd"]

    def test_cost_likely_less_than_max(self):
        """Likely cost should be less than maximum cost."""
        costs = calculate_cost(1000, 800, 1200, 75.0)
        assert costs["cost_likely_usd"] < costs["cost_max_usd"]

    def test_cost_all_positive(self):
        """All cost values should be positive."""
        costs = calculate_cost(500, 400, 600, 50.0)
        assert all(v > 0 for v in costs.values())


class TestTimeline:
    """Tests for timeline calculation with Brooks's Law."""

    def test_timeline_positive(self):
        """Timeline should always be positive."""
        tl = calculate_timeline(6.0, 5)
        assert tl["timeline_likely_weeks"] > 0

    def test_timeline_min_less_than_max(self):
        """Min timeline should be less than max timeline."""
        tl = calculate_timeline(6.0, 5)
        assert tl["timeline_min_weeks"] < tl["timeline_max_weeks"]

    def test_timeline_larger_team_shorter(self):
        """Larger team should result in shorter (but not proportionally) calendar time."""
        tl_small = calculate_timeline(12.0, 3)
        tl_large = calculate_timeline(12.0, 10)
        assert tl_large["timeline_likely_weeks"] < tl_small["timeline_likely_weeks"]


class TestPhaseBreakdown:
    """Tests for project phase decomposition."""

    def test_phase_has_six_phases(self):
        """Breakdown should return exactly 6 phases."""
        phases = calculate_phase_breakdown(3500, 262500, 26.0)
        assert len(phases) == 6

    def test_phase_pct_sums_to_100(self):
        """Phase percentages must sum to 100%."""
        phases = calculate_phase_breakdown(3500, 262500, 26.0)
        total_pct = sum(p["pct_of_total"] for p in phases)
        assert abs(total_pct - 100.0) < 1.0

    def test_phase_effort_all_positive(self):
        """All phase effort values should be positive."""
        phases = calculate_phase_breakdown(3500, 262500, 26.0)
        assert all(p["effort_hours"] > 0 for p in phases)

    def test_phase_cost_sums_to_total(self):
        """Sum of phase costs should approximately equal total cost."""
        total_cost = 262500
        phases = calculate_phase_breakdown(3500, total_cost, 26.0)
        phase_cost_sum = sum(p["cost_usd"] for p in phases)
        assert abs(phase_cost_sum - total_cost) < 10
