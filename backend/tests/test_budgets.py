"""Exact money arithmetic, hostile input and real persistence/ownership coverage."""
import os
from contextlib import asynccontextmanager
from decimal import Decimal
from uuid import uuid4

import asyncpg
import pytest
from app.api.v1 import budgets
from app.core import database
from app.core.security import CurrentUser, get_current_user
from app.models.budget import BudgetRequest, calculate_budget
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError


def payload():
    return {"project_name": "Release planning", "contingency_pct": "10", "tasks": [
        {"name": "Implementation", "low_hours": "10", "likely_hours": "20", "high_hours": "30", "hourly_rate_usd": "75"},
        {"name": "Review", "low_hours": "2", "likely_hours": "4", "high_hours": "6", "hourly_rate_usd": "100"},
    ]}


def test_known_scenarios_are_not_predictions():
    totals = calculate_budget(BudgetRequest(**payload()))
    assert totals.likely_hours == 24
    assert totals.low_cost_usd == Decimal("1045.00")
    assert totals.likely_cost_usd == Decimal("2090.00")
    assert totals.high_cost_usd == Decimal("3135.00")


def test_round_once_with_decimal_not_binary_float():
    body = payload()
    body["contingency_pct"] = "0"
    task = dict(name="Small task", low_hours="0.05", likely_hours="0.05", high_hours="0.05", hourly_rate_usd="0.10")
    body["tasks"] = [task, task, task]
    assert calculate_budget(BudgetRequest(**body)).likely_cost_usd == Decimal("0.02")


@pytest.mark.parametrize("field,value", [("low_hours", -1), ("low_hours", 21), ("high_hours", 19),
    ("likely_hours", "NaN"), ("hourly_rate_usd", "Infinity"), ("hourly_rate_usd", "1.001"),
    ("hourly_rate_usd", 10001), ("name", " ")])
def test_invalid_task_rejected(field, value):
    body = payload()
    body["tasks"][0][field] = value
    with pytest.raises(ValidationError):
        BudgetRequest(**body)


@pytest.mark.parametrize("change", [{"tasks": []}, {"tasks": payload()["tasks"] * 51},
    {"contingency_pct": 101}, {"contingency_pct": -1}, {"project_name": " "}, {"user_id": "victim"},
    {"totals": {"likely_cost_usd": 1}}])
def test_invalid_request_rejected(change):
    with pytest.raises(ValidationError):
        BudgetRequest(**(payload() | change))


@pytest.mark.integration
def test_budget_persistence_and_authorization(monkeypatch):
    dsn = os.getenv("PREDICTIQ_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("Requires isolated migrated PostgreSQL")
    user = CurrentUser(id="budget-test-" + uuid4().hex, role="editor")
    owner = user.id

    @asynccontextmanager
    async def lifespan(app):
        pool = await asyncpg.create_pool(dsn, min_size=1, max_size=2)
        monkeypatch.setattr(database, "_pool", pool)
        try:
            yield
        finally:
            await pool.execute("DELETE FROM budgets WHERE user_id=$1", owner)
            await pool.close()

    app = FastAPI(lifespan=lifespan)
    app.include_router(budgets.router)
    app.dependency_overrides[get_current_user] = lambda: user
    with TestClient(app) as client:
        created = client.post("/budgets", json=payload())
        assert created.status_code == 201, created.text
        saved = created.json()
        path = "/budgets/" + saved["id"]
        assert saved["method"] == "manual_task_budget_v1"
        assert saved["totals"]["likely_cost_usd"] == "2090.00"
        assert client.get(path).json() == saved
        assert client.get("/budgets").json() == [saved]
        assert client.get("/budgets?offset=1").json() == []
        assert client.get("/budgets?limit=101").status_code == 422
        user.id = "other-owner"
        for role in ("editor", "admin"):
            user.role = role
            assert client.get(path).status_code == 404
            assert client.delete(path).status_code == 404
            assert client.get("/budgets").json() == []
        user.id, user.role = owner, "viewer"
        assert client.get(path).status_code == 200
        assert client.post("/budgets", json=payload()).status_code == 403
        assert client.delete(path).status_code == 403
        app.dependency_overrides.clear()
        assert client.get(path).status_code in (401, 403)
        app.dependency_overrides[get_current_user] = lambda: user
        user.role = "editor"
        assert client.delete(path).status_code == 204
        assert client.get(path).status_code == 404
