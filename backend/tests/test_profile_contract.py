"""Profile routes must use the validated schema, not an unbounded duplicate."""
from unittest.mock import AsyncMock

import pytest
from app.api.v1 import profile
from app.core.security import CurrentUser, get_current_user
from app.models.user import UserProfileUpdate
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.mark.parametrize("method", ["post", "patch"])
@pytest.mark.parametrize("payload", [
    {"hourly_rate_usd": -1}, {"hourly_rate_usd": 501},
    {"hourly_rate_usd": "NaN"}, {"hourly_rate_usd": "Infinity"},
    {"full_name": "x" * 201}, {"theme": "unknown"},
    {"currency": "USD\r\nInjected"}, {"timezone": "x" * 101},
    {"avatar_url": "javascript:alert(1)"}, {"avatar_url": "data:text/html,unsafe"},
])
def test_invalid_profile_never_reaches_database(monkeypatch, method, payload):
    database = AsyncMock(side_effect=AssertionError("Unexpected database access"))
    monkeypatch.setattr(profile, "get_db", database)
    app = FastAPI()
    app.include_router(profile.router)
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="owner", role="editor")
    response = TestClient(app).request(method, "/profile", json=payload)
    assert response.status_code == 422
    database.assert_not_awaited()


@pytest.mark.parametrize("currency", ["USD", "JPY", "CAD", "AED"])
def test_profile_preserves_supported_currency_choices(currency):
    assert UserProfileUpdate(currency=currency).currency == currency


@pytest.mark.parametrize("avatar", [None, "", "https://example.com/avatar.png"])
def test_valid_avatar_and_clear_are_supported(avatar):
    assert UserProfileUpdate(avatar_url=avatar).avatar_url == avatar
