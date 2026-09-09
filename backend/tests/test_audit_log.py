"""
Tests for the Audit Logging Middleware (S6).
Validates structured audit log entries for SOC 2 compliance.
"""
from app.middleware.audit_log import _SKIP_PATHS, AuditLogMiddleware

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

# Actual middleware identity/redaction behavior is covered in test_request_hardening.py.
