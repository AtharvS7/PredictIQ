"""
Predictify — ML Service Tests
Tests for feature vector construction and prediction pipeline.
"""
import json
from pathlib import Path

import numpy as np
import pytest
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

    @pytest.fixture(autouse=True)
    def ready_predictor(self, monkeypatch):
        from unittest.mock import Mock

        from ml.inference import EXPECTED_FEATURES, predictor
        monkeypatch.setattr(predictor, "is_ready", True)
        monkeypatch.setattr(predictor, "feature_names", EXPECTED_FEATURES)
        monkeypatch.setattr(predictor, "n_features", 27)
        monkeypatch.setattr(predictor, "scaler", Mock(transform=lambda x: x))
        monkeypatch.setattr(predictor, "model", Mock(predict=lambda x: np.array([np.log1p(1000)])))

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


def test_unavailable_model_returns_503(monkeypatch, sample_project_params):
    from fastapi import HTTPException
    from ml.inference import predictor
    monkeypatch.setattr(predictor, "is_ready", False)
    with pytest.raises(HTTPException) as error:
        ml.predict(sample_project_params)
    assert error.value.status_code == 503


@pytest.mark.parametrize('field,value', [('size_fp', float('nan')), ('size_fp', -1), ('duration_months', float('inf')), ('team_size', 0)])
def test_invalid_project_numeric_features(field, value):
    with pytest.raises((ValueError, OverflowError)):
        ml._build_feature_vector({field: value})


@pytest.mark.parametrize('complexity', ['Low', 'Medium', 'High', 'Very High'])
def test_adjustment_uses_training_influence_units(complexity):
    vector = ml._build_feature_vector({'complexity': complexity, 'size_fp': 250})
    assert vector['PointsNonAdjust'] * (0.65 + 0.01 * vector['Adjustment']) == pytest.approx(250)
    assert 19 <= vector['Adjustment'] <= 35.000001


def test_dataset_adjustment_provenance_and_derived_features():
    import csv
    rows = list(csv.DictReader((Path(__file__).parent.parent / 'ml' / 'predictiq_merged_dataset.csv').open()))
    observed = [row for row in rows if float(row['Adjustment']) > 0]
    assert len(rows) == 740
    assert len(observed) == 81
    # Source FP values are rounded; one source row differs by 1.62 FP.
    for row in observed:
        expected = float(row['PointsNonAdjust']) * (0.65 + 0.01 * float(row['Adjustment']))
        assert float(row['size_fp']) == pytest.approx(expected, abs=1.63)
    for row in rows:
        assert float(row['complexity_score']) == pytest.approx(sum(float(row[k]) for k in ['T07', 'T10', 'T11']) / 3)
        assert float(row['team_skill_avg']) == pytest.approx(sum(float(row[k]) for k in ['T12', 'T13', 'T14', 'T15']) / 4)
        assert float(row['risk_score']) == pytest.approx((float(row['T08']) + float(row['T09'])) / 2)
        assert float(row['log_effort']) == pytest.approx(np.log1p(float(row['effort_hours'])))
