"""Version allocation checks, including optional disposable PostgreSQL integration."""
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import asyncpg
import pytest
from app.services.estimate_service import EstimateService


@pytest.mark.asyncio
async def test_missing_estimate_does_not_allocate_version():
    user_id = "missing-owner"
    connection = MagicMock()
    connection.fetchrow = AsyncMock(return_value=None)
    connection.fetchval = AsyncMock()
    connection.transaction.return_value.__aenter__ = AsyncMock()
    pool = MagicMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=connection)
    with patch("app.services.estimate_service.get_db", AsyncMock(return_value=pool)):
        assert await EstimateService().duplicate_estimate(str(uuid4()), user_id) is None
    connection.fetchval.assert_not_called()


@pytest.mark.asyncio
async def test_concurrent_versions_with_real_postgres():
    """Use only explicitly supplied disposable test DB; never application settings."""
    dsn = os.getenv("PREDICTIQ_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("Set PREDICTIQ_TEST_DATABASE_URL to a disposable PostgreSQL database")
    user_id = "lineage-test-" + uuid4().hex
    admin = await asyncpg.connect(dsn)
    pool = None
    try:
        first = await admin.fetchval(
            """INSERT INTO estimates(user_id,project_name,version,inputs_json,outputs_json,model_version,
                   effort_likely_hours,cost_likely_usd,duration_likely_weeks,risk_score,confidence_pct)
               VALUES($1,'Same name',3,'{}','{}','trained-model',100,1000,10,20,70) RETURNING id""", user_id
        )
        second = await admin.fetchval(
            """INSERT INTO estimates(user_id,project_name,version,inputs_json,outputs_json,
                   effort_likely_hours,cost_likely_usd,duration_likely_weeks,risk_score,confidence_pct)
               VALUES($1,'Same name',3,'{}','{}',100,1000,10,20,70) RETURNING id""", user_id
        )
        assert await admin.fetchval("SELECT count(DISTINCT lineage_id) FROM estimates WHERE user_id=$1", user_id) == 2
        pool = await asyncpg.create_pool(dsn, min_size=2, max_size=12)
        service = EstimateService()
        with patch("app.services.estimate_service.get_db", AsyncMock(return_value=pool)):
            # Identical names are independent historical lineages.
            independent = await service.duplicate_estimate(str(second), user_id)
            assert independent.version == 4
            child = await service.duplicate_estimate(str(first), user_id)
            assert child.version == 4
            await admin.execute("UPDATE estimates SET project_name='Renamed' WHERE id=$1", first)
            results = await asyncio.gather(*[
                service.duplicate_estimate(str(first if i % 2 else child.id), user_id)
                for i in range(12)
            ])
            assert sorted(row.version for row in results) == list(range(5, 17))
            assert await service.duplicate_estimate(str(first), "other-user") is None
            await admin.execute("UPDATE estimates SET status='deleted' WHERE user_id=$1 AND version=16", user_id)
            assert (await service.duplicate_estimate(str(first), user_id)).version == 17
        assert await admin.fetchval(
            "SELECT count(*) FROM estimates WHERE lineage_id=(SELECT lineage_id FROM estimates WHERE id=$1) AND model_version='trained-model'",
            first,
        ) == 15
        with pytest.raises(asyncpg.UniqueViolationError):
            await admin.execute(
                """INSERT INTO estimates(user_id,project_name,lineage_id,version)
                   SELECT user_id,project_name,lineage_id,version FROM estimates WHERE id=$1""", first,
            )
    finally:
        if pool is not None:
            await pool.close()
        await admin.execute("DELETE FROM estimates WHERE user_id=$1", user_id)
        await admin.close()
