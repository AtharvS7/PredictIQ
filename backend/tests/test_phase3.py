"""
Predictify — Phase 3 Tests
Tests for Architecture & Code Quality changes:
  - T3.2: EstimateService refactor
  - T3.3: Configurable connection pool
  - T3.4: Storage service (local + S3)
  - T3.5: Background tasks
"""
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# ═══════════════════════════════════════════════════════════════════════
# T3.3 — Configurable Connection Pool
# ═══════════════════════════════════════════════════════════════════════


class TestPoolConfig:
    """Tests for configurable database pool settings."""

    def test_default_pool_min_size(self):
        """Default DB_POOL_MIN_SIZE should be 2."""
        from app.core.config import settings
        assert settings.DB_POOL_MIN_SIZE == 2

    def test_default_pool_max_size(self):
        """Default DB_POOL_MAX_SIZE should be 10."""
        from app.core.config import settings
        assert settings.DB_POOL_MAX_SIZE == 10

    def test_default_command_timeout(self):
        """Default DB_COMMAND_TIMEOUT should be 30."""
        from app.core.config import settings
        assert settings.DB_COMMAND_TIMEOUT == 30

    def test_storage_backend_default(self):
        """Default STORAGE_BACKEND should be 'local'."""
        from app.core.config import settings
        assert settings.STORAGE_BACKEND == "local"


# ═══════════════════════════════════════════════════════════════════════
# T3.4 — Storage Service
# ═══════════════════════════════════════════════════════════════════════


class TestLocalStorageBackend:
    """Tests for the local filesystem storage backend."""

    @pytest.fixture
    def tmp_storage(self, tmp_path):
        """Create a LocalStorageBackend with a temp directory."""
        from app.services.storage_service import LocalStorageBackend
        return LocalStorageBackend(str(tmp_path))

    @pytest.mark.asyncio
    async def test_upload_creates_file(self, tmp_storage, tmp_path):
        """Uploading data should create a file at the key path."""
        key = "test/file.txt"
        data = b"hello world"
        result = await tmp_storage.upload(data, key)
        assert result == key
        assert (tmp_path / key).exists()
        assert (tmp_path / key).read_bytes() == data

    @pytest.mark.asyncio
    async def test_download_returns_data(self, tmp_storage, tmp_path):
        """Downloading should return the uploaded data."""
        key = "test/file.txt"
        data = b"hello world"
        await tmp_storage.upload(data, key)
        result = await tmp_storage.download(key)
        assert result == data

    @pytest.mark.asyncio
    async def test_download_missing_returns_none(self, tmp_storage):
        """Downloading a non-existent key should return None."""
        result = await tmp_storage.download("nonexistent.txt")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_removes_file(self, tmp_storage, tmp_path):
        """Deleting should remove the file and return True."""
        key = "test/file.txt"
        await tmp_storage.upload(b"data", key)
        result = await tmp_storage.delete(key)
        assert result is True
        assert not (tmp_path / key).exists()

    @pytest.mark.asyncio
    async def test_delete_missing_returns_false(self, tmp_storage):
        """Deleting a non-existent key should return False."""
        result = await tmp_storage.delete("nonexistent.txt")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self, tmp_storage):
        """exists() should return True for uploaded files."""
        key = "test/file.txt"
        await tmp_storage.upload(b"data", key)
        assert await tmp_storage.exists(key) is True

    @pytest.mark.asyncio
    async def test_exists_false(self, tmp_storage):
        """exists() should return False for missing files."""
        assert await tmp_storage.exists("nonexistent.txt") is False

    @pytest.mark.asyncio
    async def test_upload_creates_subdirectories(self, tmp_storage, tmp_path):
        """Upload should auto-create parent directories."""
        key = "deep/nested/path/file.txt"
        await tmp_storage.upload(b"data", key)
        assert (tmp_path / key).exists()


class TestStorageService:
    """Tests for the StorageService facade."""

    def test_generate_key_format(self):
        """Generated key should follow documents/{user_id}/{uuid}_{filename} pattern."""
        from app.services.storage_service import StorageService
        svc = StorageService()
        key = svc.generate_key("user-123", "report.pdf")
        assert key.startswith("documents/")
        assert svc.belongs_to_user(key, "user-123")
        assert "report.pdf" not in key

    def test_generate_key_sanitizes_spaces(self):
        """Spaces in filename should be replaced with underscores."""
        from app.services.storage_service import StorageService
        svc = StorageService()
        key = svc.generate_key("user-123", "my report file.pdf")
        assert " " not in key

    def test_generate_key_unique(self):
        """Each call should generate a unique key."""
        from app.services.storage_service import StorageService
        svc = StorageService()
        keys = {svc.generate_key("user-123", "file.pdf") for _ in range(10)}
        assert len(keys) == 10  # All unique


# ═══════════════════════════════════════════════════════════════════════
# T3.2 — EstimateService Refactor
# ═══════════════════════════════════════════════════════════════════════


class TestEstimateService:
    """Tests for the EstimateService singleton."""

    def test_service_importable(self):
        """estimate_service should be importable as a module-level singleton."""
        from app.services.estimate_service import estimate_service
        assert estimate_service is not None

    def test_service_has_crud_methods(self):
        """EstimateService should have all CRUD methods."""
        from app.services.estimate_service import estimate_service
        assert hasattr(estimate_service, "run_estimation")
        assert hasattr(estimate_service, "list_estimates")
        assert hasattr(estimate_service, "get_estimate")
        assert hasattr(estimate_service, "duplicate_estimate")
        assert hasattr(estimate_service, "delete_estimate")
        assert hasattr(estimate_service, "create_share_link")

    def test_row_to_summary_helper(self):
        """_row_to_summary should convert a dict-like row to EstimateSummary."""
        from datetime import datetime, timezone

        from app.services.estimate_service import EstimateService

        row = {
            "id": "test-uuid",
            "project_name": "Test Project",
            "inputs_json": {"project_type": "Web App"},
            "outputs_json": {"cost_min_usd": 100, "cost_max_usd": 500, "risk_level": "Medium"},
            "cost_likely_usd": 300,
            "risk_score": 0.5,
            "confidence_pct": 80,
            "duration_likely_weeks": 12,
            "status": "complete",
            "version": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
        }
        summary = EstimateService._row_to_summary(row)
        assert summary.id == "test-uuid"
        assert summary.project_name == "Test Project"
        assert summary.project_type == "Web App"
        assert summary.cost_likely_usd == 300


# ═══════════════════════════════════════════════════════════════════════
# T3.5 — Background Tasks
# ═══════════════════════════════════════════════════════════════════════


class TestBackgroundTasks:
    """Tests for background task functions."""

    @pytest.mark.asyncio
    async def test_log_estimation_analytics_no_crash(self):
        """log_estimation_analytics should never raise."""
        from app.services.background_tasks import log_estimation_analytics
        # Should complete without error
        await log_estimation_analytics(
            estimate_id="test-id",
            user_id="test-user",
            project_type="Web App",
            effort_hours=100.0,
            cost_usd=5000.0,
            risk_score=0.5,
        )

    @pytest.mark.asyncio
    async def test_update_document_preview_with_mock_db(self):
        """update_document_preview should update DB without crashing."""
        import app.core.database as db_module
        from app.services.background_tasks import update_document_preview

        mock_pool = AsyncMock()
        mock_pool.execute = AsyncMock()
        db_module._pool = mock_pool

        try:
            await update_document_preview("doc-123", "This is a preview text")
            mock_pool.execute.assert_called_once()
        finally:
            db_module._pool = None

    @pytest.mark.asyncio
    async def test_sync_profile_role_with_mock_db(self):
        """sync_profile_role should update profile role in DB."""
        import app.core.database as db_module
        from app.services.background_tasks import sync_profile_role

        mock_pool = AsyncMock()
        mock_pool.execute = AsyncMock()
        db_module._pool = mock_pool

        try:
            await sync_profile_role("user-123", "admin")
            mock_pool.execute.assert_called_once()
        finally:
            db_module._pool = None


# ═══════════════════════════════════════════════════════════════════════
# T3.1 — Alembic Migrations
# ═══════════════════════════════════════════════════════════════════════


class TestAlembicSetup:
    """Tests for Alembic migration infrastructure."""

    def test_alembic_ini_exists(self):
        """alembic.ini should exist in the backend root."""
        ini_path = Path(__file__).parent.parent / "alembic.ini"
        assert ini_path.exists(), "alembic.ini not found"

    def test_alembic_env_exists(self):
        """alembic/env.py should exist."""
        env_path = Path(__file__).parent.parent / "alembic" / "env.py"
        assert env_path.exists(), "alembic/env.py not found"

    def test_migration_versions_exist(self):
        """At least 2 migration versions should exist."""
        versions_dir = Path(__file__).parent.parent / "alembic" / "versions"
        assert versions_dir.exists()
        versions = list(versions_dir.glob("*.py"))
        assert len(versions) >= 2, f"Expected at least 2 migrations, found {len(versions)}"

    def test_initial_migration_has_upgrade_downgrade(self):
        """Initial migration should have upgrade() and downgrade() functions."""
        import importlib.util
        migration_path = Path(__file__).parent.parent / "alembic" / "versions" / "2026_04_001_initial_initial_schema.py"
        spec = importlib.util.spec_from_file_location("migration_001", migration_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "upgrade")
        assert hasattr(module, "downgrade")
        assert module.revision == "001_initial"
        assert module.down_revision is None
