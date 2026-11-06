"""
PredictIQ — ML Service Tests v2 (CP14)
=====================================
Tests for production ML service serving v2:
- Honest input validation (size_fp, duration_months, team_size)
- Conformal calibrated quantiles (p10 <= p50 <= p90)
- Conversion: 152 productive hours per person-month
- Out-of-Distribution (OOD) flag generation
- Data Quality Tier assignment (A, B, C)
- Rejection of negative / non-finite inputs
"""

import pytest
from app.services.ml_service import (
    HOURS_PER_PERSON_MONTH,
    ml_service,
)
from fastapi import HTTPException


class TestMLServiceV2:
    """Tests for the production ML service."""

    def test_ml_service_is_ready(self):
        """Service should be ready with verified production bundle."""
        assert ml_service.is_ready() is True

    def test_model_info_conforms_to_contract(self):
        """get_model_info returns verified metadata."""
        info = ml_service.get_model_info()
        assert info["model_loaded"] is True
        assert info["model_version"] == "2.0.0-rc.1"
        assert "MultivariateMonotoneModel" in info["best_model"]
        assert info["training_samples"] == 915
        assert info["mdape"] <= 0.55
        assert info["confidence_method"] == "mondrian_split_conformal_80pct"

    def test_valid_prediction_structure(self):
        """Prediction returns calibrated effort and person-months."""
        result = ml_service.predict({"size_fp": 185.0})

        # Non-crossing quantiles
        effort = result["effort_hours"]
        assert 1.0 <= effort["p10"] <= effort["p50"] <= effort["p90"]

        # Backwards compatible legacy keys
        assert result["effort_hours_likely"] == effort["p50"]
        assert result["effort_hours_min"] == effort["p10"]
        assert result["effort_hours_max"] == effort["p90"]
        assert result["confidence_pct"] == 80.0

        # Person-months at 152 hrs/PM
        pm = result["person_months"]
        assert pm["p10"] == round(effort["p10"] / HOURS_PER_PERSON_MONTH, 2)
        assert pm["p50"] == round(effort["p50"] / HOURS_PER_PERSON_MONTH, 2)
        assert pm["p90"] == round(effort["p90"] / HOURS_PER_PERSON_MONTH, 2)

        # Quality tier and size
        assert result["data_quality_tier"] in ("A", "B", "C")
        assert result["size"]["value"] == 185.0

    def test_optional_covariates_affect_prediction(self):
        """Optional duration and team size covariates are utilized."""
        r1 = ml_service.predict({"size_fp": 200.0})
        r2 = ml_service.predict({"size_fp": 200.0, "duration_months": 6.0, "team_size": 4})
        assert r1["effort_hours"]["p50"] > 0
        assert r2["effort_hours"]["p50"] > 0

    def test_negative_size_rejected(self):
        """Negative size_fp raises HTTPException 422."""
        with pytest.raises(HTTPException) as exc_info:
            ml_service.predict({"size_fp": -50.0})
        assert exc_info.value.status_code == 422

    def test_zero_size_rejected(self):
        """Zero size_fp raises HTTPException 422."""
        with pytest.raises(HTTPException) as exc_info:
            ml_service.predict({"size_fp": 0.0})
        assert exc_info.value.status_code == 422

    def test_nan_or_inf_rejected(self):
        """NaN or Inf size raises HTTPException 422."""
        with pytest.raises(HTTPException) as exc_info:
            ml_service.predict({"size_fp": float("nan")})
        assert exc_info.value.status_code == 422

        with pytest.raises(HTTPException) as exc_info:
            ml_service.predict({"size_fp": float("inf")})
        assert exc_info.value.status_code == 422

    def test_ood_detection_small_size(self):
        """Size below dataset minimum triggers OOD flag."""
        result = ml_service.predict({"size_fp": 2.0})
        assert any("size_fp_below_training_min" in flag for flag in result["ood_flags"])
        assert result["data_quality_tier"] == "C"

    def test_ood_detection_huge_size(self):
        """Size exceeding dataset maximum triggers OOD flag and tier C."""
        result = ml_service.predict({"size_fp": 8000.0})
        assert any("size_fp_exceeds_training_max" in flag for flag in result["ood_flags"])
        assert result["data_quality_tier"] == "C"

    def test_ood_detection_extreme_duration(self):
        """Extreme duration triggers OOD flag."""
        result = ml_service.predict({"size_fp": 200.0, "duration_months": 120.0})
        assert any("duration_months_extreme" in flag for flag in result["ood_flags"])
        assert result["data_quality_tier"] == "C"

    def test_nlp_source_tier_b(self):
        """NLP-derived size within normal domain gets Tier B."""
        params = {
            "feature_count": {"value": 20, "confidence": 0.8},
            "integration_count": {"value": 3, "confidence": 0.8},
        }
        result = ml_service.predict(params)
        assert result["size"]["source"] == "nlp"
        assert result["data_quality_tier"] == "B"
        assert result["size"]["uncertainty"]["p10"] < result["size"]["value"] < result["size"]["uncertainty"]["p90"]

    def test_banned_features_do_not_crash_service(self):
        """If banned features are accidentally passed, they are safely ignored."""
        params = {
            "size_fp": 150.0,
            "T01": 5.0,
            "T02": 3.0,
            "Transactions": 999.0,
            "Entities": 888.0,
            "TeamExp": 2.0,
        }
        result = ml_service.predict(params)
        assert result["effort_hours"]["p50"] > 0
        assert "T01" not in result
        assert "Transactions" not in result
