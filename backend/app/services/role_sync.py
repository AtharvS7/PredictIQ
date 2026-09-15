"""PostgreSQL is authoritative for application-managed roles; Firebase is reconciled."""
import asyncio

import structlog
from firebase_admin import auth
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db

logger = structlog.get_logger()


def sync_claims(user_id, role):
    record = auth.get_user(user_id)
    claims = dict(record.custom_claims or {})
    claims['role'] = role
    auth.set_custom_user_claims(user_id, claims)


async def sync_pending(user_id=None):
    pool = await get_db()
    async with pool.acquire() as connection:
        async with connection.transaction():
            row = await connection.fetchrow(
                'SELECT id, role FROM profiles WHERE role_sync_pending '
                'AND (($1::text IS NULL AND role_sync_after <= NOW()) OR id=$1) '
                'ORDER BY role_sync_after FOR UPDATE SKIP LOCKED LIMIT 1', user_id)
            if row is None:
                return None
            try:
                await run_in_threadpool(sync_claims, row['id'], row['role'])
            except Exception as exc:
                # Durable delay lets later accounts proceed and survives worker restarts.
                await connection.execute(
                    "UPDATE profiles SET role_sync_after=NOW() + INTERVAL '30 seconds' WHERE id=$1", row['id'])
                logger.warning('role_sync_pending', error_type=type(exc).__name__)
                return False
            await connection.execute('UPDATE profiles SET role_sync_pending=FALSE WHERE id=$1', row['id'])
            return True


async def reconcile_roles():
    while True:
        try:
            for _ in range(25):
                if await sync_pending() is None:
                    break
        except Exception as exc:
            logger.warning('role_reconciliation_failed', error_type=type(exc).__name__)
        await asyncio.sleep(30)
