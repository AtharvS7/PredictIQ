"""Actual ASGI/auth/serialization boundaries, without cloud credentials."""
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.core import security
from app.middleware.body_limit import BodyLimitMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient


@pytest.mark.parametrize("headers,chunks,expected", [
    ([], [b"abcd", b"ef"], 413),
    ([(b"content-length", b"1")], [b"abcd", b"ef"], 413),
    ([(b"content-length", b"bad")], [], 400),
    ([(b"content-length", b"-1")], [], 400),
    ([(b"content-length", b"1"), (b"content-length", b"1")], [], 400),
    ([(b"content-length", b"3")], [b"a"], 400),
    ([], [b"abc", b"de"], 200),
])
async def test_actual_body_limit(headers, chunks, expected):
    called = []
    messages = []
    async def downstream(scope, receive, send):
        called.append(await receive())
        await send({"type": "http.response.start", "status": 200, "headers": []})
    receive = AsyncMock(side_effect=[{"type": "http.request", "body": chunk,
        "more_body": index < len(chunks) - 1} for index, chunk in enumerate(chunks)])
    async def send(message):
        messages.append(message)
    await BodyLimitMiddleware(downstream, json_limit=5)({"type": "http", "headers": headers}, receive, send)
    assert messages[0]["status"] == expected
    assert bool(called) == (expected == 200)
    if called:
        assert called[0]["body"] == b"abcde"


async def test_auth_checks_revocation_and_sets_verified_identity(monkeypatch):
    verify = Mock(return_value={"uid": "verified-user", "role": "admin"})
    monkeypatch.setattr(security.firebase_auth, "verify_id_token", verify)
    request = Request({"type": "http"})
    user = await security.get_current_user(request, HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token"))
    verify.assert_called_once_with("test-token", check_revoked=True)
    assert request.state.user_id == user.id == "verified-user"


@pytest.mark.parametrize("error_type", [security.firebase_auth.RevokedIdTokenError,
    security.firebase_auth.UserDisabledError, security.firebase_auth.InvalidIdTokenError])
async def test_invalid_tokens_rejected_without_provider_details(monkeypatch, error_type):
    monkeypatch.setattr(security.firebase_auth, "verify_id_token", Mock(side_effect=error_type("private detail")))
    with pytest.raises(HTTPException) as error:
        await security.get_current_user(Request({"type": "http"}), HTTPAuthorizationCredentials(scheme="Bearer", credentials="x"))
    assert error.value.status_code == 401
    assert "private" not in error.value.detail


def test_audit_uses_verified_user_and_route_template(monkeypatch):
    from app.middleware import audit_log
    logger = Mock()
    monkeypatch.setattr(audit_log, "logger", logger)
    app = FastAPI()
    app.add_middleware(audit_log.AuditLogMiddleware)
    @app.get("/items/{item_id}")
    async def item(request: Request, item_id: str):
        request.state.user_id = "verified-user"
        return {"ok": True}
    with TestClient(app) as client:
        assert client.get("/items/private-id?password=private-query", headers={"Authorization": "Bearer private-token"}).status_code == 200
    fields = logger.info.call_args.kwargs
    assert fields["user"] == "verified-user"
    assert fields["path"] == "/items/{item_id}"
    assert "private" not in str(fields)


def test_json_export_serializes_postgres_types(monkeypatch):
    from app.api.v1 import export
    identifier = uuid4()
    pool = AsyncMock()
    pool.fetchrow.return_value = {"id": identifier, "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "cost": Decimal("123.45"), "private_bytes": b"binary"}
    monkeypatch.setattr(export, "get_db", AsyncMock(return_value=pool))
    app = FastAPI()
    app.include_router(export.router)
    app.dependency_overrides[security.get_current_user] = lambda: security.CurrentUser(id="owner")
    with TestClient(app) as client:
        response = client.get(f"/estimates/{identifier}/export/json")
    assert response.status_code == 200
    assert response.json()["id"] == str(identifier)
    assert response.json()["cost"] == 123.45
    assert "private_bytes" not in response.json()


@pytest.mark.parametrize("method,status", [("get", 404), ("post", 422)])
def test_share_errors_are_private(method, status):
    from app.core.rate_limit import limiter
    from main import app

    limiter.reset()
    try:
        # Exercise real middleware without starting external providers.
        client = TestClient(app)
        response = getattr(client, method)("/api/v1/shared/invalid-token")
        assert response.status_code == status
        assert response.headers["Referrer-Policy"] == "no-referrer"
        assert response.headers["Cache-Control"] == "no-store"
    finally:
        limiter.reset()


def test_global_rate_limit_is_enforced():
    from app.core.rate_limit import limiter
    from main import app
    limiter.reset()
    # No lifespan needed: root exercises the actual middleware without providers.
    client = TestClient(app)
    try:
        for _ in range(200):
            assert client.get("/").status_code == 200
        assert client.get("/").status_code == 429
    finally:
        limiter.reset()
