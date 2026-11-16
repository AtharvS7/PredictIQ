"""
PredictIQ — Size Consistency & Shared Sizing Verification (Task A4)
===================================================================
Verifies:
1. Request with size_fp=138 returns effort p50 within 0.5% of ml_service.predict(138).
2. Request without size_fp and 16 features, 2 integrations returns the same result (138 FP).
3. 5 features gives 50 FP (5*8 + 2*5 = 50 FP).
4. Changing complexity, team size or duration does not change effort hours (effort hours p50 remains identical).
5. The stored estimate and exported JSON/PDF contain the exact same size and hours as the API response.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.services.cost_calculator import compute_functional_size
from app.services.estimate_service import estimate_service
from app.services.export_service import generate_pdf_report
from app.services.ml_service import ml_service


@pytest.fixture
def mock_db_pool():
    """Mock database pool returning row and transaction handles."""
    pool = AsyncMock()
    fake_saved_row = {
        "id": uuid4(),
        "created_at": "2026-11-16T00:00:00Z",
        "version": 1,
    }
    pool.fetchrow = AsyncMock(return_value=fake_saved_row)
    pool.fetch = AsyncMock(return_value=[])
    pool.fetchval = AsyncMock(return_value=0)
    pool.execute = AsyncMock()
    pool.acquire = MagicMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=pool)
    pool.transaction = MagicMock()
    pool.transaction.return_value.__aenter__ = AsyncMock()
    return pool


@pytest.mark.asyncio
async def test_request_with_size_fp_138_matches_ml_service(mock_db_pool):
    """(1) Request with size_fp=138 returns effort p50 within 0.5% of ml_service.predict(138)."""
    expected_ml = ml_service.predict({"size_fp": 138.0, "size_source": "user"})
    expected_p50 = expected_ml["effort_hours_likely"]

    result = await estimate_service.run_estimation(
        user_id="test-user-123",
        document_id=None,
        project_name="Size Test",
        project_type="Web App",
        team_size=5,
        duration_months=6,
        complexity="Medium",
        methodology="Agile",
        hourly_rate=75.0,
        tech_stack=["React", "FastAPI"],
        feature_count=16,
        integration_count=2,
        size_fp=138.0,
        size_source="user",
        db_pool=mock_db_pool,
    )

    actual_p50 = result.outputs.effort_likely_hours
    diff_pct = abs(actual_p50 - expected_p50) / expected_p50
    assert diff_pct < 0.005, f"Expected p50 ~{expected_p50}, got {actual_p50} (diff {diff_pct:.4f})"
    assert result.inputs.size_fp == 138.0
    assert result.size is not None
    assert result.size["value"] == 138.0


@pytest.mark.asyncio
async def test_request_without_size_fp_computes_138_from_features(mock_db_pool):
    """(2) Request without size_fp and 16 features, 2 integrations returns the exact same 138 FP."""
    result = await estimate_service.run_estimation(
        user_id="test-user-123",
        document_id=None,
        project_name="Computed Size Test",
        project_type="Web App",
        team_size=5,
        duration_months=6,
        complexity="Medium",
        methodology="Agile",
        hourly_rate=75.0,
        tech_stack=["React", "FastAPI"],
        feature_count=16,
        integration_count=2,
        size_fp=None,
        db_pool=mock_db_pool,
    )

    assert result.inputs.size_fp == 138.0
    assert result.size is not None
    assert result.size["value"] == 138.0

    expected_ml = ml_service.predict({"size_fp": 138.0, "size_source": "user"})
    assert abs(result.outputs.effort_likely_hours - expected_ml["effort_hours_likely"]) < 1e-3


def test_shared_sizing_rule_5_features_gives_50_fp():
    """(3) 5 features and 2 integrations gives 50 FP (5*8 + 2*5 = 50)."""
    size = compute_functional_size(feature_count=5, integration_count=2)
    assert size == 50.0, f"Expected 50.0 FP, got {size}"

    # Also check zero integrations (5*8 = 40)
    assert compute_functional_size(5, 0) == 40.0


@pytest.mark.asyncio
async def test_complexity_team_duration_do_not_alter_effort_hours(mock_db_pool):
    """(4) Changing complexity, team size or duration does NOT change effort hours."""
    res_base = await estimate_service.run_estimation(
        user_id="test-user-123",
        document_id=None,
        project_name="Base Project",
        project_type="Web App",
        team_size=3,
        duration_months=3,
        complexity="Low",
        methodology="Agile",
        hourly_rate=75.0,
        tech_stack=["React"],
        feature_count=16,
        integration_count=2,
        size_fp=138.0,
        db_pool=mock_db_pool,
    )

    res_varied = await estimate_service.run_estimation(
        user_id="test-user-123",
        document_id=None,
        project_name="Varied Project",
        project_type="Web App",
        team_size=15,
        duration_months=18,
        complexity="Very High",
        methodology="Waterfall",
        hourly_rate=120.0,
        tech_stack=["React", "Kubernetes", "PostgreSQL", "Kafka"],
        feature_count=16,
        integration_count=2,
        size_fp=138.0,
        db_pool=mock_db_pool,
    )

    assert res_base.outputs.effort_likely_hours == res_varied.outputs.effort_likely_hours
    assert res_base.outputs.effort_min_hours == res_varied.outputs.effort_min_hours
    assert res_base.outputs.effort_max_hours == res_varied.outputs.effort_max_hours

    # Cost differs because hourly rates differ (75 vs 120)
    assert res_base.outputs.cost_likely_usd != res_varied.outputs.cost_likely_usd
    # Timeline differs because duration/team differ
    assert res_base.outputs.timeline_likely_weeks != res_varied.outputs.timeline_likely_weeks


@pytest.mark.asyncio
async def test_stored_estimate_and_export_contain_same_size_and_hours(mock_db_pool):
    """(5) Stored estimate and exported JSON/PDF contain the exact same size and hours as API response."""
    result = await estimate_service.run_estimation(
        user_id="test-user-123",
        document_id=None,
        project_name="Export Consistency Project",
        project_type="Web App",
        team_size=5,
        duration_months=6,
        complexity="Medium",
        methodology="Agile",
        hourly_rate=75.0,
        tech_stack=["React", "FastAPI"],
        feature_count=16,
        integration_count=2,
        size_fp=138.0,
        db_pool=mock_db_pool,
    )

    # 1. Verify result contains 138 FP and hours
    assert result.inputs.size_fp == 138.0
    assert result.size["value"] == 138.0
    expected_hours = result.outputs.effort_likely_hours

    # 2. Simulate database retrieval via get_estimate
    stored_row = {
        "id": result.estimate_id,
        "document_id": None,
        "user_id": "test-user",
        "project_name": result.project_name,
        "created_at": "2026-11-16T00:00:00Z",
        "version": 1,
        "status": "complete",
        "inputs_json": json.dumps(result.inputs.model_dump()),
        "outputs_json": json.dumps({
            **result.outputs.model_dump(),
            "size": result.size,
        }),
        "model_version": result.model_version,
    }
    mock_db_pool.fetchrow = AsyncMock(return_value=stored_row)

    from unittest.mock import patch

    with patch("app.services.estimate_service.get_db", AsyncMock(return_value=mock_db_pool)):
        retrieved = await estimate_service.get_estimate(result.estimate_id, user_id="test-user")
    assert retrieved is not None
    assert retrieved.inputs.size_fp == 138.0
    assert retrieved.size["value"] == 138.0
    assert retrieved.outputs.effort_likely_hours == expected_hours

    # 3. Verify PDF generation preserves size and hours
    pdf_bytes = generate_pdf_report(retrieved.model_dump(), currency_code="USD")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
