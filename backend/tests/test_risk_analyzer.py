"""
PredictIQ — Risk Analyzer Tests
Tests for risk scoring, severity mapping, and risk factor detection.
"""
from app.services.risk_analyzer import analyze_risk


class TestRiskAnalyzer:
    """Tests for the risk analysis engine."""

    def test_returns_dict(self, sample_project_params):
        """analyze_risk must return a dictionary."""
        result = analyze_risk(sample_project_params)
        assert isinstance(result, dict)

    def test_has_required_keys(self, sample_project_params):
        """Result must contain risk_score, risk_level, and top_risks."""
        result = analyze_risk(sample_project_params)
        assert "risk_score" in result
        assert "risk_level" in result
        assert "top_risks" in result

    def test_risk_score_range(self, sample_project_params):
        """Risk score must be between 0 and 100."""
        result = analyze_risk(sample_project_params)
        assert 0 <= result["risk_score"] <= 100

    def test_risk_level_valid(self, sample_project_params):
        """Risk level must be one of the four valid levels."""
        result = analyze_risk(sample_project_params)
        assert result["risk_level"] in ("Low", "Medium", "High", "Critical")

    def test_top_risks_is_list(self, sample_project_params):
        """top_risks must be a list."""
        result = analyze_risk(sample_project_params)
        assert isinstance(result["top_risks"], list)

    def test_top_risks_max_five(self, sample_project_params):
        """top_risks should contain at most 5 items."""
        result = analyze_risk(sample_project_params)
        assert len(result["top_risks"]) <= 5

    def test_high_complexity_raises_risk(self, high_risk_params):
        """Very High complexity + aggressive timeline should produce elevated risk."""
        result = analyze_risk(high_risk_params)
        assert result["risk_score"] > 30

    def test_low_complexity_lowers_risk(self, low_risk_params):
        """Low complexity with reasonable scope should produce lower risk."""
        result = analyze_risk(low_risk_params)
        assert result["risk_score"] < 50

    def test_empty_params_no_crash(self):
        """Empty params should not crash — returns a valid result."""
        result = analyze_risk({})
        assert isinstance(result, dict)
        assert "risk_score" in result

    def test_risk_score_numeric(self, sample_project_params):
        """Risk score should be a numeric type."""
        result = analyze_risk(sample_project_params)
        assert isinstance(result["risk_score"], (int, float))
