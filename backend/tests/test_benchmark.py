"""
Predictify — Benchmark Service Tests
Tests for historical dataset comparison logic.
"""
import pandas as pd
import pytest
from app.services import benchmark
from app.services.benchmark import get_benchmark_comparison


class TestBenchmarkComparison:
    """Tests for the benchmark comparison engine."""

    @pytest.fixture(autouse=True)
    def ensure_data_loaded(self, monkeypatch):
        """Exercise comparison arithmetic with explicitly valid fixture labels."""
        monkeypatch.setattr(benchmark, "_benchmark_df", pd.DataFrame({
            "size_fp": [50, 200, 250, 300], "effort_hours": [500, 2000, 3000, 4000],
        }))

    def test_comparison_uses_observed_hour_median(self):
        result = get_benchmark_comparison(250, 3000, 225000, 6)
        assert "median: 3,000 hrs" in result

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
