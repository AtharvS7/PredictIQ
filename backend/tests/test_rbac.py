"""
Predictify — RBAC Tests
Tests for role-based access control (T2.1).

Tests cover:
  - require_role() dependency factory
  - Role hierarchy enforcement
  - Admin endpoints (user management)
  - Route protection for viewers vs editors
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from app.core.security import ROLE_HIERARCHY, VALID_ROLES, CurrentUser, require_role
from fastapi.testclient import TestClient

# ═══════════════════════════════════════════════════════════════════════
# Module-scoped setup
# ═══════════════════════════════════════════════════════════════════════


def _make_client(role: str = "editor"):
    """Create a TestClient with mocked auth returning the given role."""
    import app.core.database as db_module
    from main import app

    # Mock database pool
    mock_pool = AsyncMock()
    mock_pool.fetchrow = AsyncMock(return_value=None)
    mock_pool.fetch = AsyncMock(return_value=[])
    mock_pool.execute = AsyncMock(return_value="UPDATE 0")
    mock_pool.fetchval = AsyncMock(return_value=0)
    db_module._pool = mock_pool

    # Override auth to return a user with the specified role
    test_user = CurrentUser(id="test-user-rbac", email="rbac@test.com", role=role)
    from app.core.security import get_current_user
    app.dependency_overrides[get_current_user] = lambda: test_user

    client = TestClient(app, raise_server_exceptions=False)
    return client, mock_pool, app


def _cleanup(app):
    """Reset dependency overrides."""
    import app.core.database as db_module
    app.dependency_overrides.clear()
    db_module._pool = None


# ═══════════════════════════════════════════════════════════════════════
# Unit Tests: require_role() dependency
# ═══════════════════════════════════════════════════════════════════════


class TestRoleHierarchy:
    """Tests for the RBAC role hierarchy and constants."""

    def test_valid_roles_contains_three(self):
        """VALID_ROLES should have exactly admin, editor, viewer."""
        assert VALID_ROLES == {"admin", "editor", "viewer"}

    def test_hierarchy_order(self):
        """admin > editor > viewer in hierarchy."""
        assert ROLE_HIERARCHY["admin"] > ROLE_HIERARCHY["editor"]
        assert ROLE_HIERARCHY["editor"] > ROLE_HIERARCHY["viewer"]

    def test_admin_is_highest(self):
        """admin should have the highest privilege level."""
        assert ROLE_HIERARCHY["admin"] == max(ROLE_HIERARCHY.values())

    def test_viewer_is_lowest(self):
        """viewer should have the lowest privilege level."""
        assert ROLE_HIERARCHY["viewer"] == min(ROLE_HIERARCHY.values())


class TestRequireRole:
    """Tests for the require_role() dependency factory."""

    def test_require_role_returns_callable(self):
        """require_role() should return a coroutine function."""
        dep = require_role("admin")
        assert callable(dep)

    def test_require_role_invalid_role_raises(self):
        """require_role() with invalid role should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid role"):
            require_role("superadmin")

    @pytest.mark.asyncio
    async def test_admin_passes_admin_check(self):
        """Admin user should pass admin role check."""
        dep = require_role("admin")
        admin_user = CurrentUser(id="u1", role="admin")
        result = await dep(user=admin_user)
        assert result.id == "u1"

    @pytest.mark.asyncio
    async def test_admin_passes_editor_check(self):
        """Admin user should pass editor role check (hierarchy)."""
        dep = require_role("editor")
        admin_user = CurrentUser(id="u1", role="admin")
        result = await dep(user=admin_user)
        assert result.role == "admin"

    @pytest.mark.asyncio
    async def test_editor_passes_editor_check(self):
        """Editor user should pass editor role check."""
        dep = require_role("editor")
        editor_user = CurrentUser(id="u2", role="editor")
        result = await dep(user=editor_user)
        assert result.role == "editor"

    @pytest.mark.asyncio
    async def test_viewer_fails_editor_check(self):
        """Viewer user should NOT pass editor role check."""
        from fastapi import HTTPException
        dep = require_role("editor")
        viewer_user = CurrentUser(id="u3", role="viewer")
        with pytest.raises(HTTPException) as exc_info:
            await dep(user=viewer_user)
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_viewer_fails_admin_check(self):
        """Viewer user should NOT pass admin role check."""
        from fastapi import HTTPException
        dep = require_role("admin")
        viewer_user = CurrentUser(id="u3", role="viewer")
        with pytest.raises(HTTPException) as exc_info:
            await dep(user=viewer_user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_editor_fails_admin_check(self):
        """Editor user should NOT pass admin role check."""
        from fastapi import HTTPException
        dep = require_role("admin")
        editor_user = CurrentUser(id="u2", role="editor")
        with pytest.raises(HTTPException) as exc_info:
            await dep(user=editor_user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_viewer_passes_viewer_check(self):
        """Viewer user should pass viewer role check."""
        dep = require_role("viewer")
        viewer_user = CurrentUser(id="u3", role="viewer")
        result = await dep(user=viewer_user)
        assert result.role == "viewer"


# ═══════════════════════════════════════════════════════════════════════
# Integration Tests: Route Protection
# ═══════════════════════════════════════════════════════════════════════


class TestViewerRouteAccess:
    """Test that viewers can read but cannot write."""

    def test_viewer_can_read_estimates(self):
        """Viewer should be able to GET /estimates."""
        client, mock_pool, app = _make_client("viewer")
        mock_pool.fetch = AsyncMock(return_value=[])
        mock_pool.fetchval = AsyncMock(return_value=0)
        try:
            resp = client.get("/api/v1/estimates")
            assert resp.status_code == 200
        finally:
            _cleanup(app)

    def test_viewer_cannot_create_estimate(self):
        """Viewer should be blocked from POST /estimates/manual (403)."""
        client, mock_pool, app = _make_client("viewer")
        try:
            resp = client.post("/api/v1/estimates/manual", json={
                "project_name": "Test",
                "project_type": "Web App",
                "team_size": 5,
                "duration_months": 6,
                "complexity": "Medium",
                "methodology": "Agile",
                "hourly_rate_usd": 75.0,
                "tech_stack": [],
            })
            assert resp.status_code == 403
        finally:
            _cleanup(app)

    def test_viewer_cannot_delete_estimate(self):
        """Viewer should be blocked from DELETE /estimates/{id} (403)."""
        client, mock_pool, app = _make_client("viewer")
        try:
            resp = client.delete(f"/api/v1/estimates/{uuid4()}")
            assert resp.status_code == 403
        finally:
            _cleanup(app)

    def test_viewer_can_read_profile(self):
        """Viewer should be able to GET /profile."""
        client, mock_pool, app = _make_client("viewer")
        mock_pool.fetchrow = AsyncMock(return_value={
            "id": "test-user-rbac", "full_name": "Test", "role": "viewer",
            "currency": "USD", "theme": "system", "timezone": "UTC",
            "hourly_rate_usd": 75.0, "avatar_url": "",
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
        })
        try:
            resp = client.get("/api/v1/profile")
            assert resp.status_code == 200
        finally:
            _cleanup(app)

    def test_viewer_cannot_update_profile(self):
        """Viewer should be blocked from PATCH /profile (403)."""
        client, mock_pool, app = _make_client("viewer")
        try:
            resp = client.patch("/api/v1/profile", json={"full_name": "Hacked"})
            assert resp.status_code == 403
        finally:
            _cleanup(app)


class TestEditorRouteAccess:
    """Test that editors can read and write, but not admin."""

    def test_editor_can_create_estimate(self, contract_model_artifacts):
        """Editor should be able to POST /estimates/manual."""
        from ml.inference import predictor

        assert predictor.load(*contract_model_artifacts)
        client, mock_pool, app = _make_client("editor")
        mock_pool.fetchrow = AsyncMock(return_value={
            "id": str(uuid4()), "user_id": "test-user-rbac",
            "project_name": "Test", "status": "complete",
            "created_at": datetime.now(timezone.utc), "version": 1,
        })
        try:
            resp = client.post("/api/v1/estimates/manual", json={
                "project_name": "Test",
                "project_type": "Web App",
                "team_size": 5,
                "duration_months": 6,
                "complexity": "Medium",
                "methodology": "Agile",
                "hourly_rate_usd": 75.0,
                "tech_stack": [],
            })
            assert resp.status_code == 200
        finally:
            _cleanup(app)

    def test_editor_cannot_access_admin(self):
        """Editor should be blocked from GET /admin/users (403)."""
        client, mock_pool, app = _make_client("editor")
        try:
            resp = client.get("/api/v1/admin/users")
            assert resp.status_code == 403
        finally:
            _cleanup(app)

    def test_editor_cannot_change_roles(self):
        """Editor should be blocked from PATCH /admin/users/{id} (403)."""
        client, mock_pool, app = _make_client("editor")
        try:
            resp = client.patch(f"/api/v1/admin/users/{uuid4()}", json={"role": "admin"})
            assert resp.status_code == 403
        finally:
            _cleanup(app)


class TestAdminRouteAccess:
    """Test that admins have full access."""

    def test_admin_can_list_users(self):
        """Admin should be able to GET /admin/users."""
        client, mock_pool, app = _make_client("admin")
        mock_pool.fetch = AsyncMock(return_value=[])
        try:
            resp = client.get("/api/v1/admin/users")
            assert resp.status_code == 200
            data = resp.json()
            assert "users" in data
            assert "total" in data
        finally:
            _cleanup(app)

    def test_admin_can_change_user_role(self):
        """Admin should be able to PATCH /admin/users/{id}."""
        client, mock_pool, app = _make_client("admin")
        target_user_id = "target-user-123"
        mock_pool.fetchrow = AsyncMock(return_value={
            "id": target_user_id, "role": "viewer",
        })
        mock_pool.execute = AsyncMock()

        with patch("app.api.v1.admin.firebase_auth.get_user", return_value=MagicMock(custom_claims={})), \
                patch("app.api.v1.admin.firebase_auth.set_custom_user_claims") as mock_claims:
            try:
                resp = client.patch(
                    f"/api/v1/admin/users/{target_user_id}",
                    json={"role": "editor"},
                )
                assert resp.status_code == 200
                data = resp.json()
                assert data["old_role"] == "viewer"
                assert data["new_role"] == "editor"
                assert data["synced_to_firebase"] is True
                mock_claims.assert_called_once_with(target_user_id, {"role": "editor"})
            finally:
                _cleanup(app)

    def test_admin_cannot_self_demote(self):
        """Admin should NOT be able to demote themselves."""
        client, mock_pool, app = _make_client("admin")
        try:
            resp = client.patch(
                "/api/v1/admin/users/test-user-rbac",  # same as the mock user ID
                json={"role": "viewer"},
            )
            assert resp.status_code == 400
            assert "Cannot demote yourself" in resp.json()["detail"]
        finally:
            _cleanup(app)

    def test_admin_role_update_user_not_found(self):
        """PATCH /admin/users/{id} with non-existent user returns 404."""
        client, mock_pool, app = _make_client("admin")
        mock_pool.fetchrow = AsyncMock(return_value=None)
        try:
            resp = client.patch(
                f"/api/v1/admin/users/{uuid4()}",
                json={"role": "editor"},
            )
            assert resp.status_code == 404
        finally:
            _cleanup(app)

    def test_admin_role_update_invalid_role(self):
        """PATCH /admin/users/{id} with invalid role returns 422."""
        client, mock_pool, app = _make_client("admin")
        try:
            resp = client.patch(
                f"/api/v1/admin/users/{uuid4()}",
                json={"role": "superadmin"},
            )
            assert resp.status_code == 422  # Pydantic Literal validation
        finally:
            _cleanup(app)


class TestCurrentUserModel:
    """Tests for the CurrentUser model with RBAC."""

    def test_default_role_is_editor(self):
        """Default role should be 'editor'."""
        user = CurrentUser(id="u1")
        assert user.role == "editor"

    def test_role_can_be_set(self):
        """Role should be settable to any valid value."""
        for role in ("admin", "editor", "viewer"):
            user = CurrentUser(id="u1", role=role)
            assert user.role == role

    def test_email_is_optional(self):
        """Email should be optional with None default."""
        user = CurrentUser(id="u1")
        assert user.email is None
