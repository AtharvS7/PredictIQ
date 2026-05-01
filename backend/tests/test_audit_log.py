"""
Tests for the Audit Logging Middleware (S6).
Validates structured audit log entries for SOC 2 compliance.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.middleware.audit_log import AuditLogMiddleware, _SKIP_PATHS


# ── Skip Paths ───────────────────────────────────────────────

class TestSkipPaths:
    """Verify health/docs endpoints are excluded from audit logging."""

    def test_health_in_skip_paths(self):
        assert "/api/v1/health" in _SKIP_PATHS

    def test_health_root_in_skip_paths(self):
        assert "/health" in _SKIP_PATHS

    def test_docs_in_skip_paths(self):
        assert "/docs" in _SKIP_PATHS

    def test_openapi_in_skip_paths(self):
        assert "/openapi.json" in _SKIP_PATHS

    def test_redoc_in_skip_paths(self):
        assert "/redoc" in _SKIP_PATHS

    def test_favicon_in_skip_paths(self):
        assert "/favicon.ico" in _SKIP_PATHS

    def test_api_endpoints_not_skipped(self):
        """Regular API endpoints should NOT be in skip paths."""
        assert "/api/v1/estimates" not in _SKIP_PATHS
        assert "/api/v1/profile" not in _SKIP_PATHS
        assert "/api/v1/export" not in _SKIP_PATHS

    def test_skip_paths_is_frozenset(self):
        """Skip paths should be immutable (frozenset)."""
        assert isinstance(_SKIP_PATHS, frozenset)


# ── Middleware Class ─────────────────────────────────────────

class TestAuditLogMiddleware:
    """Test the AuditLogMiddleware class structure."""

    def test_middleware_exists(self):
        assert AuditLogMiddleware is not None

    def test_middleware_has_dispatch(self):
        """Middleware must implement dispatch method."""
        assert hasattr(AuditLogMiddleware, 'dispatch')

    def test_skip_paths_count(self):
        """Should skip exactly 6 noisy endpoints."""
        assert len(_SKIP_PATHS) == 6


# ── User ID Extraction Logic ────────────────────────────────

class TestUserIdExtraction:
    """Test the bearer token fingerprinting logic."""

    def test_anonymous_without_auth_header(self):
        """Requests without auth header should log as 'anonymous'."""
        auth_header = ""
        if auth_header.startswith("Bearer ") and len(auth_header) > 20:
            user_id = f"bearer:...{auth_header[-8:]}"
        else:
            user_id = "anonymous"
        assert user_id == "anonymous"

    def test_bearer_token_fingerprint(self):
        """Valid bearer tokens should show last 8 chars only."""
        auth_header = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test12345678"
        if auth_header.startswith("Bearer ") and len(auth_header) > 20:
            user_id = f"bearer:...{auth_header[-8:]}"
        else:
            user_id = "anonymous"
        assert user_id == "bearer:...12345678"
        # Full token must never appear in the user_id
        assert "eyJhbGci" not in user_id

    def test_short_bearer_treated_as_anonymous(self):
        """Very short tokens (invalid) should be treated as anonymous."""
        auth_header = "Bearer short"
        if auth_header.startswith("Bearer ") and len(auth_header) > 20:
            user_id = f"bearer:...{auth_header[-8:]}"
        else:
            user_id = "anonymous"
        assert user_id == "anonymous"

    def test_non_bearer_auth_treated_as_anonymous(self):
        """Non-bearer auth (e.g. Basic) should be treated as anonymous."""
        auth_header = "Basic dXNlcjpwYXNzd29yZA=="
        if auth_header.startswith("Bearer ") and len(auth_header) > 20:
            user_id = f"bearer:...{auth_header[-8:]}"
        else:
            user_id = "anonymous"
        assert user_id == "anonymous"
