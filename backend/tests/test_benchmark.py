"""
PredictIQ — Benchmark Service Tests
Tests for historical dataset comparison logic.
"""
import pytest
from app.services.benchmark import get_benchmark_comparison, load_benchmark_data


class TestBenchmarkComparison:
    """Tests for the benchmark comparison engine."""

    @pytest.fixture(autouse=True)
    def ensure_data_loaded(self):
        """Load benchmark data before each test."""
        load_benchmark_data()

    def test_returns_string(self):
        """get_benchmark_comparison must return a string."""
        result = get_benchmark_comparison(
            size_fp=250.0,
            effort_hours_likely=3500.0,
            cost_likely_usd=262500.0,
            duration_months=8.0,
            hourly_rate=75.0,
        )
        assert isinstance(result, str)

    def test_non_empty_result(self):
        """Result should be a non-empty string."""
        result = get_benchmark_comparison(
            size_fp=250.0,
            effort_hours_likely=3500.0,
            cost_likely_usd=262500.0,
            duration_months=8.0,
            hourly_rate=75.0,
        )
        assert len(result) > 10

    def test_contains_project_reference(self):
        """Result text should reference projects or data."""
        result = get_benchmark_comparison(
            size_fp=250.0,
            effort_hours_likely=3500.0,
            cost_likely_usd=262500.0,
            duration_months=8.0,
            hourly_rate=75.0,
        )
        assert "project" in result.lower() or "data" in result.lower() or "benchmark" in result.lower()

    def test_extreme_fp_handled(self):
        """Extreme FP values should produce a valid result (not crash)."""
        result = get_benchmark_comparison(
            size_fp=50000.0,
            effort_hours_likely=100000.0,
            cost_likely_usd=7500000.0,
            duration_months=36.0,
            hourly_rate=75.0,
        )
        assert isinstance(result, str)

    def test_small_project_comparison(self):
        """Small project benchmark should still return a valid string."""
        result = get_benchmark_comparison(
            size_fp=50.0,
            effort_hours_likely=200.0,
            cost_likely_usd=15000.0,
            duration_months=2.0,
            hourly_rate=75.0,
        )
        assert isinstance(result, str)
