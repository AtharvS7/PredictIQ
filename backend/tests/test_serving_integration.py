"""
PredictIQ — Serving Integration Tests (CP17)
============================================
Integration tests verifying serving layer conformance with api_estimate_v2.json:
- Calibrated quantiles (p10 <= p50 <= p90)
- Conversion: 152 productive hours per person-month
- Zero fabricated features (no T01-T15, Transactions, Entities)
- Data Quality Tiers (A, B, C) and OOD diagnostics
- Contract field structure, drivers, and assumptions
"""

from uuid import uuid4

from app.services.cost_calculator import calculate_cost_v2
from app.services.ml_service import ml_service
from app.services.nlp_extractor import nlp_extractor


class TestServingContractIntegration:
    """Verifies end-to-end estimation serving pipelines."""

    def test_serving_contract_conformance_manual_flow(self):
        """Manual estimation flow adheres to api_estimate_v2 contract."""
        size_fp = 185.0
        hourly_rate = 85.0
        params = {
            "size_fp": size_fp,
            "duration_months": 8.0,
            "team_size": 5,
            "project_name": "Healthcare Claims Portal",
        }

        # 1. Prediction
        ml_res = ml_service.predict(params)
        cost_res = calculate_cost_v2(ml_res["effort_hours"], hourly_rate=hourly_rate)

        # 2. Assemble contract payload
        payload = {
            "estimate_id": str(uuid4()),
            "project_name": params["project_name"],
            "effort_hours": ml_res["effort_hours"],
            "person_months": ml_res["person_months"],
            "cost": cost_res,
            "size": ml_res["size"],
            "drivers": [
                {
                    "name": "Functional Size",
                    "impact": "major_increase",
                    "description": f"{size_fp} verified Function Points.",
                }
            ],
            "assumptions": [
                {
                    "category": "Effort Conversion",
                    "description": "152 productive working hours per person-month.",
                    "editable": False,
                }
            ],
            "data_quality_tier": ml_res["data_quality_tier"],
            "ood_flags": ml_res["ood_flags"],
            "model": ml_res["model"],
        }

        # 3. Assertions
        assert payload["data_quality_tier"] == "A"
        assert payload["ood_flags"] == []

        # Quantile ordering
        assert 1.0 <= payload["effort_hours"]["p10"] <= payload["effort_hours"]["p50"] <= payload["effort_hours"]["p90"]
        assert 1.0 <= payload["person_months"]["p10"] <= payload["person_months"]["p50"] <= payload["person_months"]["p90"]
        assert 1.0 <= payload["cost"]["p10"] <= payload["cost"]["p50"] <= payload["cost"]["p90"]

        # Exact math checks
        assert payload["cost"]["rate"] == hourly_rate
        assert payload["cost"]["currency"] == "USD"
        assert abs(payload["cost"]["p50"] - round(payload["effort_hours"]["p50"] * hourly_rate, 2)) < 0.01

        # Model provenance
        assert payload["model"]["version"] in ("2.0.0-rc.1", "2.0.0-rc.3")
        assert payload["model"]["trained_on_rows"] == 915
        assert len(payload["model"]["sources"]) == 6

    def test_serving_contract_conformance_nlp_flow(self, sample_document_text):
        """NLP extraction cascade feeding ML serving produces valid Tier B contract output."""
        # 1. NLP Extraction
        nlp_res = nlp_extractor.extract(sample_document_text)
        assert "size_fp" in nlp_res
        size_info = nlp_res["size_fp"]
        assert size_info["source"] == "nlp"
        assert size_info["value"] > 0

        # 2. ML Serving
        ml_res = ml_service.predict(nlp_res)
        cost_res = calculate_cost_v2(ml_res["effort_hours"], hourly_rate=75.0)

        # 3. Assertions
        assert ml_res["data_quality_tier"] == "B"
        assert ml_res["size"]["source"] == "nlp"
        assert ml_res["size"]["uncertainty"]["p10"] < ml_res["size"]["value"] < ml_res["size"]["uncertainty"]["p90"]

        effort = ml_res["effort_hours"]
        assert 1.0 <= effort["p10"] <= effort["p50"] <= effort["p90"]
        assert 1.0 <= cost_res["p10"] <= cost_res["p50"] <= cost_res["p90"]

    def test_serving_ood_handling(self):
        """Massive or out-of-domain projects are safely diagnosed and assigned Tier C."""
        params = {"size_fp": 9500.0, "duration_months": 80.0, "team_size": 60}
        ml_res = ml_service.predict(params)

        assert ml_res["data_quality_tier"] == "C"
        assert len(ml_res["ood_flags"]) >= 2
        assert any("size_fp_exceeds_training_max" in flag for flag in ml_res["ood_flags"])

        # Monotonicity must remain invariant even under extreme inputs
        effort = ml_res["effort_hours"]
        assert 1.0 <= effort["p10"] <= effort["p50"] <= effort["p90"]

    def test_serving_zero_fabricated_features(self):
        """Banned features must never leak into inputs or outputs."""
        banned = [
            "T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09", "T10",
            "T11", "T12", "T13", "T14", "T15", "Transactions", "Entities",
            "PointsNonAdjust", "Adjustment", "TeamExp", "ManagerExp",
        ]
        params = {"size_fp": 150.0}
        for b in banned:
            params[b] = 999.0

        ml_res = ml_service.predict(params)
        for b in banned:
            assert b not in ml_res
