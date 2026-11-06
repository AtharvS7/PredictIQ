"""
Unit and integration tests for CP06 Actuals Flywheel.
Covers:
- Pydantic schema validation (bounds, positive effort, extra forbid)
- Auth guards (editor/viewer roles, estimate ownership, admin bypass)
- Creation and consent flag persistence
- Isolation of non-consented data in admin export (projects_v2 format)
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import app.core.database as db_module
import pytest
from app.api.v1.actuals import router as actuals_router
from app.core.security import CurrentUser, get_current_user
from app.models.actual import EstimateActual
from app.schemas.actual import ActualCreate
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

# ─────────────────────────────────────────────────────────────────────────────
# 1. Pydantic Schema Validation Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_actual_create_valid():
    """Valid payload should instantiate ActualCreate cleanly."""
    payload = {
        "actual_effort_hours": 120.5,
        "actual_cost_usd": 15000.0,
        "actual_duration_months": 2.5,
        "team_size": 4,
        "functional_size_delivered": 45.0,
        "notes": "Delivered successfully with minor sprint shifts.",
        "consent_for_training": True,
    }
    obj = ActualCreate.model_validate(payload)
    assert obj.actual_effort_hours == 120.5
    assert obj.actual_cost_usd == 15000.0
    assert obj.team_size == 4
    assert obj.consent_for_training is True


def test_actual_create_default_consent_false():
    """Consent must default to False if omitted (critical for flywheel privacy)."""
    obj = ActualCreate.model_validate({"actual_effort_hours": 50.0})
    assert obj.consent_for_training is False
    assert obj.actual_cost_usd is None
    assert obj.team_size is None


@pytest.mark.parametrize("invalid_effort", [0.0, -1.0, -100.5])
def test_actual_create_effort_must_be_strictly_positive(invalid_effort):
    """Effort must be strictly positive (> 0)."""
    with pytest.raises(ValidationError):
        ActualCreate.model_validate({"actual_effort_hours": invalid_effort})


@pytest.mark.parametrize(
    "field,value",
    [
        ("actual_cost_usd", -0.01),
        ("actual_duration_months", -1.0),
        ("team_size", 0),
        ("team_size", -3),
        ("functional_size_delivered", -5.0),
    ],
)
def test_actual_create_sane_bounds(field, value):
    """Negative costs/durations/sizes or non-positive team sizes must be rejected."""
    payload = {"actual_effort_hours": 40.0, field: value}
    with pytest.raises(ValidationError):
        ActualCreate.model_validate(payload)


def test_actual_create_extra_fields_forbidden():
    """Unexpected fields must be rejected (extra='forbid')."""
    with pytest.raises(ValidationError):
        ActualCreate.model_validate(
            {"actual_effort_hours": 40.0, "unknown_field": "injected"}
        )


def test_sqlalchemy_model_attributes():
    """Verify SQLAlchemy model maps required columns."""
    assert EstimateActual.__tablename__ == "estimate_actuals"
    columns = EstimateActual.__table__.columns
    expected_cols = {
        "id",
        "estimate_id",
        "actual_effort_hours",
        "actual_cost_usd",
        "actual_duration_months",
        "team_size",
        "functional_size_delivered",
        "notes",
        "consent_for_training",
        "created_at",
        "created_by_user_id",
    }
    assert expected_cols.issubset(set(columns.keys()))


# ─────────────────────────────────────────────────────────────────────────────
# 2. API Integration Tests (Mocked DB Pool & Auth)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_user() -> CurrentUser:
    """Default test user with editor role."""
    return CurrentUser(id="owner-user-001", email="owner@predictiq.io", role="editor")


@pytest.fixture
def mock_pool():
    """Mock asyncpg connection pool."""
    pool = AsyncMock()
    pool.fetchrow = AsyncMock(return_value=None)
    pool.fetch = AsyncMock(return_value=[])
    pool.fetchval = AsyncMock(return_value=0)
    pool.execute = AsyncMock(return_value="OK")
    return pool


@pytest.fixture
def client(mock_user, mock_pool):
    """FastAPI TestClient with isolated router and dependencies mocked."""
    app = FastAPI()
    app.include_router(actuals_router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    original_pool = db_module._pool
    db_module._pool = mock_pool

    with TestClient(app) as c:
        yield c

    db_module._pool = original_pool


def test_post_actuals_owner_success_with_consent(client, mock_user, mock_pool):
    """Owner successfully submits actuals with explicit training consent."""
    estimate_id = uuid4()
    actual_id = uuid4()
    now = datetime.now(timezone.utc)

    async def custom_fetchrow(query, *args):
        if "FROM estimates" in query:
            return {"id": estimate_id, "user_id": mock_user.id}
        if "INSERT INTO estimate_actuals" in query:
            return {
                "id": actual_id,
                "estimate_id": estimate_id,
                "actual_effort_hours": 150.0,
                "actual_cost_usd": 18000.0,
                "actual_duration_months": 3.0,
                "team_size": 5,
                "functional_size_delivered": 60.0,
                "notes": "Delivered ahead of schedule",
                "consent_for_training": True,
                "created_at": now,
                "created_by_user_id": mock_user.id,
            }
        return None

    mock_pool.fetchrow.side_effect = custom_fetchrow

    payload = {
        "actual_effort_hours": 150.0,
        "actual_cost_usd": 18000.0,
        "actual_duration_months": 3.0,
        "team_size": 5,
        "functional_size_delivered": 60.0,
        "notes": "Delivered ahead of schedule",
        "consent_for_training": True,
    }
    resp = client.post(f"/api/v1/estimates/{estimate_id}/actuals", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == str(actual_id)
    assert data["estimate_id"] == str(estimate_id)
    assert data["actual_effort_hours"] == 150.0
    assert data["consent_for_training"] is True
    assert data["created_by_user_id"] == mock_user.id


def test_post_actuals_default_consent_false(client, mock_user, mock_pool):
    """Submitting actuals without consent flag defaults consent_for_training to False."""
    estimate_id = uuid4()
    actual_id = uuid4()
    now = datetime.now(timezone.utc)

    async def custom_fetchrow(query, *args):
        if "FROM estimates" in query:
            return {"id": estimate_id, "user_id": mock_user.id}
        if "INSERT INTO estimate_actuals" in query:
            return {
                "id": actual_id,
                "estimate_id": estimate_id,
                "actual_effort_hours": 80.0,
                "actual_cost_usd": None,
                "actual_duration_months": None,
                "team_size": None,
                "functional_size_delivered": None,
                "notes": None,
                "consent_for_training": False,
                "created_at": now,
                "created_by_user_id": mock_user.id,
            }
        return None

    mock_pool.fetchrow.side_effect = custom_fetchrow

    resp = client.post(f"/api/v1/estimates/{estimate_id}/actuals", json={"actual_effort_hours": 80.0})
    assert resp.status_code == 201
    data = resp.json()
    assert data["consent_for_training"] is False


def test_post_actuals_sanitizes_notes(client, mock_user, mock_pool):
    """Notes containing HTML/script tags are sanitized before persisting."""
    estimate_id = uuid4()
    actual_id = uuid4()
    now = datetime.now(timezone.utc)
    captured_args = []

    async def custom_fetchrow(query, *args):
        if "FROM estimates" in query:
            return {"id": estimate_id, "user_id": mock_user.id}
        if "INSERT INTO estimate_actuals" in query:
            captured_args.extend(args)
            return {
                "id": actual_id,
                "estimate_id": estimate_id,
                "actual_effort_hours": 50.0,
                "actual_cost_usd": None,
                "actual_duration_months": None,
                "team_size": None,
                "functional_size_delivered": None,
                "notes": "Safe text",
                "consent_for_training": False,
                "created_at": now,
                "created_by_user_id": mock_user.id,
            }
        return None

    mock_pool.fetchrow.side_effect = custom_fetchrow

    resp = client.post(
        f"/api/v1/estimates/{estimate_id}/actuals",
        json={"actual_effort_hours": 50.0, "notes": "<script>alert('pwned')</script>Safe text"},
    )
    assert resp.status_code == 201
    inserted_notes = captured_args[6]
    assert "<script>" not in inserted_notes
    assert "Safe text" in inserted_notes


def test_post_actuals_estimate_not_found(client, mock_pool):
    """POST to non-existent estimate returns 404."""
    mock_pool.fetchrow.return_value = None
    estimate_id = uuid4()

    resp = client.post(
        f"/api/v1/estimates/{estimate_id}/actuals",
        json={"actual_effort_hours": 100.0},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Estimate not found"


def test_post_actuals_forbidden_for_other_user(client, mock_user, mock_pool):
    """User cannot submit actuals for an estimate owned by another user."""
    estimate_id = uuid4()
    mock_pool.fetchrow.return_value = {"id": estimate_id, "user_id": "someone-else"}

    resp = client.post(
        f"/api/v1/estimates/{estimate_id}/actuals",
        json={"actual_effort_hours": 100.0},
    )
    assert resp.status_code == 403
    assert "Not authorized" in resp.json()["detail"]


def test_post_actuals_allowed_for_admin_on_any_estimate(client, mock_user, mock_pool):
    """Admin is permitted to submit actuals for an estimate owned by someone else."""
    mock_user.role = "admin"
    estimate_id = uuid4()
    actual_id = uuid4()
    now = datetime.now(timezone.utc)

    async def custom_fetchrow(query, *args):
        if "FROM estimates" in query:
            return {"id": estimate_id, "user_id": "someone-else"}
        if "INSERT INTO estimate_actuals" in query:
            return {
                "id": actual_id,
                "estimate_id": estimate_id,
                "actual_effort_hours": 200.0,
                "actual_cost_usd": None,
                "actual_duration_months": None,
                "team_size": None,
                "functional_size_delivered": None,
                "notes": "Admin entry",
                "consent_for_training": True,
                "created_at": now,
                "created_by_user_id": mock_user.id,
            }
        return None

    mock_pool.fetchrow.side_effect = custom_fetchrow

    resp = client.post(
        f"/api/v1/estimates/{estimate_id}/actuals",
        json={"actual_effort_hours": 200.0, "notes": "Admin entry", "consent_for_training": True},
    )
    assert resp.status_code == 201
    assert resp.json()["id"] == str(actual_id)


def test_post_actuals_forbidden_for_viewer_role(client, mock_user):
    """Viewer role is rejected by RBAC dependency (requires editor minimum)."""
    mock_user.role = "viewer"
    estimate_id = uuid4()
    resp = client.post(
        f"/api/v1/estimates/{estimate_id}/actuals",
        json={"actual_effort_hours": 100.0},
    )
    assert resp.status_code == 403


def test_get_actuals_owner_success(client, mock_user, mock_pool):
    """Owner successfully retrieves list of actuals for their estimate."""
    estimate_id = uuid4()
    actual_id = uuid4()
    now = datetime.now(timezone.utc)

    mock_pool.fetchrow.return_value = {"id": estimate_id, "user_id": mock_user.id}
    mock_pool.fetch.return_value = [
        {
            "id": actual_id,
            "estimate_id": estimate_id,
            "actual_effort_hours": 110.0,
            "actual_cost_usd": 12000.0,
            "actual_duration_months": 2.0,
            "team_size": 3,
            "functional_size_delivered": 30.0,
            "notes": "Version 1 delivery",
            "consent_for_training": False,
            "created_at": now,
            "created_by_user_id": mock_user.id,
        }
    ]

    resp = client.get(f"/api/v1/estimates/{estimate_id}/actuals")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(actual_id)
    assert data[0]["actual_effort_hours"] == 110.0


def test_get_actuals_forbidden_for_other_user(client, mock_user, mock_pool):
    """User cannot view actuals for another user's estimate."""
    estimate_id = uuid4()
    mock_pool.fetchrow.return_value = {"id": estimate_id, "user_id": "other-user"}

    resp = client.get(f"/api/v1/estimates/{estimate_id}/actuals")
    assert resp.status_code == 403
    assert "Not authorized" in resp.json()["detail"]


def test_get_actuals_estimate_not_found(client, mock_pool):
    """GET for missing estimate returns 404."""
    estimate_id = uuid4()
    mock_pool.fetchrow.return_value = None

    resp = client.get(f"/api/v1/estimates/{estimate_id}/actuals")
    assert resp.status_code == 404


def test_admin_export_json_format_and_projects_v2_compat(client, mock_user, mock_pool):
    """Admin exports consented actuals in JSON formatted for projects_v2 compatibility."""
    mock_user.role = "admin"
    actual_id = uuid4()
    now = datetime(2026, 8, 15, 12, 0, 0, tzinfo=timezone.utc)

    mock_pool.fetch.return_value = [
        {
            "id": actual_id,
            "estimate_id": uuid4(),
            "actual_effort_hours": 1250.0,
            "actual_cost_usd": 95000.0,
            "actual_duration_months": 7.0,
            "team_size": 6,
            "functional_size_delivered": 140.0,
            "notes": "Delivered release v1",
            "created_at": now,
            "inputs_json": {
                "project_type": "Web App",
                "platform": "Web",
                "tech_stack": ["Python", "React"],
            },
        }
    ]

    resp = client.get("/api/v1/admin/actuals/export?format=json")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    row = items[0]

    # Validate strict compatibility with projects_v2 schema
    expected_keys = {
        "project_id",
        "source",
        "year",
        "size_value",
        "size_unit",
        "effort_hours",
        "duration_months",
        "team_size",
        "platform",
        "language",
        "dev_type",
        "notes",
    }
    assert set(row.keys()) == expected_keys
    assert row["project_id"] == f"actual_{str(actual_id)[:8]}"
    assert row["source"] == "actuals_flywheel"
    assert row["year"] == 2026
    assert row["size_value"] == 140.0
    assert row["size_unit"] == "FP"
    assert row["effort_hours"] == 1250.0
    assert row["duration_months"] == 7.0
    assert row["team_size"] == 6
    assert row["platform"] == "Web"
    assert row["language"] == "Python, React"
    assert row["dev_type"] == "Web App"
    assert row["notes"] == "Delivered release v1"


def test_admin_export_csv_format(client, mock_user, mock_pool):
    """Admin exports consented actuals as CSV."""
    mock_user.role = "admin"
    actual_id = uuid4()
    now = datetime(2026, 5, 1, 0, 0, 0, tzinfo=timezone.utc)

    mock_pool.fetch.return_value = [
        {
            "id": actual_id,
            "estimate_id": uuid4(),
            "actual_effort_hours": 500.0,
            "actual_cost_usd": 40000.0,
            "actual_duration_months": 3.0,
            "team_size": 4,
            "functional_size_delivered": 50.0,
            "notes": "Completed on budget",
            "created_at": now,
            "inputs_json": {"project_type": "API Service"},
        }
    ]

    resp = client.get("/api/v1/admin/actuals/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert 'attachment; filename="consented_actuals.csv"' in resp.headers.get("content-disposition", "")
    lines = resp.text.strip().split("\n")
    header = lines[0]
    assert header == "project_id,source,year,size_value,size_unit,effort_hours,duration_months,team_size,platform,language,dev_type,notes"
    assert len(lines) == 2
    assert f"actual_{str(actual_id)[:8]}" in lines[1]
    assert "500.0" in lines[1]


def test_admin_export_isolation_strictly_consented_only(client, mock_user, mock_pool):
    """
    CRITICAL: Verify SQL query strictly isolates consented entries
    using `WHERE ea.consent_for_training = TRUE`.
    """
    mock_user.role = "admin"
    mock_pool.fetch.return_value = []

    resp = client.get("/api/v1/admin/actuals/export")
    assert resp.status_code == 200
    mock_pool.fetch.assert_called_once()
    sql_executed = mock_pool.fetch.call_args[0][0]
    assert "WHERE ea.consent_for_training = TRUE" in sql_executed


@pytest.mark.parametrize("non_admin_role", ["editor", "viewer"])
def test_admin_export_forbidden_for_non_admins(client, mock_user, non_admin_role):
    """Non-admin roles are forbidden from exporting actuals."""
    mock_user.role = non_admin_role
    resp = client.get("/api/v1/admin/actuals/export")
    assert resp.status_code == 403
    assert "admin" in resp.json()["detail"].lower()
