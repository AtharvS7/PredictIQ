"""
Predictify Database Layer
Async connection pool for Neon PostgreSQL via asyncpg.
"""
import asyncpg
import structlog
from app.core.config import settings

logger = structlog.get_logger()

_pool: asyncpg.Pool | None = None


async def init_db_pool():
    """Create the asyncpg connection pool. Called during app startup."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
        logger.info("database_pool_created", min_size=2, max_size=10)


async def close_db_pool():
    """Close the connection pool. Called during app shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("database_pool_closed")


async def get_db() -> asyncpg.Pool:
    """FastAPI dependency — returns the asyncpg connection pool."""
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _pool
