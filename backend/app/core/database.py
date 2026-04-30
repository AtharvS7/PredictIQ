"""
Predictify Database Layer
Async connection pool for Neon PostgreSQL via asyncpg.
Includes exponential backoff retry for production resilience (Q5).
"""
import asyncio
import asyncpg
import structlog
from app.core.config import settings

logger = structlog.get_logger()

_pool: asyncpg.Pool | None = None

# Retry configuration
_MAX_RETRIES = 5
_BASE_DELAY_SECONDS = 1.0  # doubles each retry: 1, 2, 4, 8, 16


async def init_db_pool():
    """Create the asyncpg connection pool with exponential backoff retry (Q5).

    Retries up to 5 times with delays of 1s, 2s, 4s, 8s, 16s before giving up.
    This handles transient network failures and cold-start DB delays.
    """
    global _pool
    if _pool is not None:
        return

    last_error = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            _pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=30,
            )
            logger.info(
                "database_pool_created",
                min_size=2,
                max_size=10,
                attempt=attempt,
            )
            return
        except (OSError, asyncpg.PostgresError, asyncpg.InterfaceError) as exc:
            last_error = exc
            delay = _BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                "database_connection_retry",
                attempt=attempt,
                max_retries=_MAX_RETRIES,
                delay_seconds=delay,
                error=str(exc),
            )
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(delay)

    # All retries exhausted
    logger.error(
        "database_connection_failed",
        max_retries=_MAX_RETRIES,
        error=str(last_error),
    )
    raise RuntimeError(
        f"Failed to connect to database after {_MAX_RETRIES} attempts: {last_error}"
    )


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
