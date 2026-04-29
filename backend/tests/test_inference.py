"""
Predictify — Inference Engine Tests
Tests for ml/inference.py PredictifyInference singleton.
"""
import pytest
from ml.inference import predictor


class TestInferenceLoad:
    """Tests for model loading."""

    def test_model_info_returns_dict(self):
        """get_model_info should return a dictionary."""
        info = predictor.get_model_info()
        assert isinstance(info, dict)

    def test_model_info_has_mode(self):
        """Model info must indicate live or demo mode."""
        info = predictor.get_model_info()
        assert "model_mode" in info
        assert info["model_mode"] in ("live", "demo")

    def test_model_info_has_version(self):
        """Model info should contain a model_version key."""
        info = predictor.get_model_info()
        assert "model_version" in info


class TestInferencePredict:
    """Tests for predict() method — works in both live and demo mode."""

    def test_predict_returns_dict(self, sample_feature_vector):
        """predict() must return a dictionary."""
        result = predictor.predict(sample_feature_vector)
        assert isinstance(result, dict)

    def test_predict_has_required_keys(self, sample_feature_vector):
        """Result must contain effort and confidence keys."""
        result = predictor.predict(sample_feature_vector)
        required = {"effort_hours_likely", "effort_hours_min", "effort_hours_max", "confidence_pct"}
        assert required.issubset(set(result.keys()))

    def test_predict_effort_positive(self, sample_feature_vector):
        """Predicted effort must be a positive number."""
        result = predictor.predict(sample_feature_vector)
        assert result["effort_hours_likely"] > 0

    def test_predict_min_less_than_likely(self, sample_feature_vector):
        """Minimum effort must be less than most-likely effort."""
        result = predictor.predict(sample_feature_vector)
        assert result["effort_hours_min"] < result["effort_hours_likely"]

    def test_predict_likely_less_than_max(self, sample_feature_vector):
        """Most-likely effort must be less than maximum effort."""
        result = predictor.predict(sample_feature_vector)
        assert result["effort_hours_likely"] < result["effort_hours_max"]

    def test_predict_confidence_range(self, sample_feature_vector):
        """Confidence must be between 0 and 100 inclusive."""
        result = predictor.predict(sample_feature_vector)
        assert 0 < result["confidence_pct"] <= 100

    def test_predict_effort_realistic_range(self, sample_feature_vector):
        """For a 250-FP project, effort should be in a reasonable range."""
        result = predictor.predict(sample_feature_vector)
        assert 50 <= result["effort_hours_likely"] <= 50000

    def test_predict_model_mode_key(self, sample_feature_vector):
        """Result should indicate model_mode (live or demo)."""
        result = predictor.predict(sample_feature_vector)
        assert "model_mode" in result
        assert result["model_mode"] in ("live", "demo")


class TestFeatureImportance:
    """Tests for feature importance retrieval."""

    def test_get_feature_importance_returns_dict(self):
        """Feature importance should return a dictionary or None."""
        importance = predictor.get_feature_importance()
        if importance is not None:
            assert isinstance(importance, dict)
