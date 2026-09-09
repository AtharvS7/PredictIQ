"""Validation must reject malformed IDs before any database operation."""
from unittest.mock import AsyncMock

import pytest
from app.api.v1 import estimates, export
from app.core.security import CurrentUser, get_current_user
from app.models.estimate import EstimateInputs, EstimateOverrides, ManualEstimateRequest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError


@pytest.mark.parametrize("method,suffix", [
    ("get", ""), ("post", "/duplicate"), ("delete", ""),
    ("post", "/share"), ("get", "/export/pdf"), ("get", "/export/json"),
])
def test_malformed_estimate_id_never_reaches_database(monkeypatch, method, suffix):
    from app.services import estimate_service

    database = AsyncMock(side_effect=AssertionError("Unexpected database access"))
    monkeypatch.setattr(estimate_service, "get_db", database)
    monkeypatch.setattr(export, "get_db", database)
    app = FastAPI()
    app.include_router(estimates.router)
    app.include_router(export.router)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="owner", role="editor")
    client = TestClient(app)
    response = client.request(method, f"/estimates/not-a-uuid{suffix}", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "estimate_id"]
    database.assert_not_awaited()


def test_historical_inputs_have_unknown_prediction_controls():
    inputs = EstimateInputs(project_type="Web App", tech_stack=[], team_size=5,
        duration_months=6, complexity="Medium", methodology="Agile", hourly_rate_usd=75)
    for name in ("feature_count", "integration_count", "volatility_score", "team_experience", "size_fp"):
        assert getattr(inputs, name) is None


@pytest.mark.parametrize("schema", [ManualEstimateRequest, EstimateOverrides])
@pytest.mark.parametrize("invalid", [
    {"project_name": " "}, {"project_name": "x" * 201},
    {"project_type": " "}, {"project_type": "x" * 101},
    {"tech_stack": ["x"] * 51}, {"tech_stack": ["x" * 101]}, {"tech_stack": [" "]},
])
def test_bounded_estimate_text(schema, invalid):
    with pytest.raises(ValidationError):
        schema.model_validate({"project_name": "Project", **invalid})


@pytest.mark.parametrize("schema", [ManualEstimateRequest, EstimateOverrides])
def test_empty_technology_override_and_trimmed_names_are_valid(schema):
    value = schema.model_validate({"project_name": " Project ", "tech_stack": []})
    assert value.project_name == "Project"
    assert value.tech_stack == []
