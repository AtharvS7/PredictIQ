"""
PredictIQ — ML Service Tests
Tests for feature vector construction and prediction pipeline.
"""
import json
import numpy as np
from pathlib import Path
from app.services.ml_service import MLService


ml = MLService()


class TestBuildFeatureVector:
    """Tests for the 27-feature vector builder."""

    def test_returns_dict(self, sample_project_params):
        """_build_feature_vector must return a dictionary."""
        vector = ml._build_feature_vector(sample_project_params)
        assert isinstance(vector, dict)

    def test_has_27_keys(self, sample_project_params):
        """Vector must contain exactly 27 features."""
        vector = ml._build_feature_vector(sample_project_params)
        assert len(vector) == 27

    def test_keys_match_features_json(self, sample_project_params):
        """All vector keys must match the features listed in predictiq_features.json."""
        features_path = Path(__file__).parent.parent / "ml" / "predictiq_features.json"
        if features_path.exists():
            with open(features_path) as f:
                expected_features = json.load(f)
            vector = ml._build_feature_vector(sample_project_params)
            for feature in expected_features:
                assert feature in vector, f"Missing feature: {feature}"

    def test_size_fp_passed_through(self, sample_project_params):
        """size_fp from params should appear in the vector."""
        vector = ml._build_feature_vector(sample_project_params)
        assert vector["size_fp"] == sample_project_params["size_fp"]

    def test_log_size_fp_correct(self, sample_project_params):
        """log_size_fp should equal log1p(size_fp)."""
        vector = ml._build_feature_vector(sample_project_params)
        expected = float(np.log1p(sample_project_params["size_fp"]))
        assert abs(vector["log_size_fp"] - expected) < 0.01

    def test_t_factors_in_range(self, sample_project_params):
        """All T-factors (T01-T15) must be between 1.0 and 5.0."""
        vector = ml._build_feature_vector(sample_project_params)
        for i in range(1, 16):
            key = f"T{i:02d}"
            assert 1.0 <= vector[key] <= 5.0, f"{key}={vector[key]} out of range"

    def test_defaults_with_empty_params(self):
        """Empty params should still produce all 27 keys without errors."""
        vector = ml._build_feature_vector({})
        assert len(vector) == 27
        assert all(isinstance(v, (int, float)) for v in vector.values())


class TestMLServicePredict:
    """Tests for the full ML service prediction pipeline."""

    def test_predict_returns_dict(self, sample_project_params):
        """predict() must return a dictionary."""
        result = ml.predict(sample_project_params)
        assert isinstance(result, dict)

    def test_predict_has_effort_keys(self, sample_project_params):
        """Result must contain effort_hours_likely and related keys."""
        result = ml.predict(sample_project_params)
        assert "effort_hours_likely" in result

    def test_predict_effort_positive(self, sample_project_params):
        """Predicted effort must be positive."""
        result = ml.predict(sample_project_params)
        assert result["effort_hours_likely"] > 0

    def test_get_model_info(self):
        """get_model_info should return a non-empty dict."""
        info = ml.get_model_info()
        assert isinstance(info, dict)
        assert len(info) > 0
