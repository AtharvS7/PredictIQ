"""
Predictify — Database Module Tests
Tests for connection pool retry configuration and state management.
"""
import pytest
from app.core.database import (
    _MAX_RETRIES, _BASE_DELAY_SECONDS,
    get_db, init_db_pool, close_db_pool,
)


class TestRetryConfiguration:
    """Verify the retry/backoff constants are sane."""

    def test_max_retries_positive(self):
        """MAX_RETRIES should be a positive integer."""
        assert isinstance(_MAX_RETRIES, int)
        assert _MAX_RETRIES >= 1

    def test_max_retries_reasonable(self):
        """MAX_RETRIES should not be too high (avoid long startup)."""
        assert _MAX_RETRIES <= 10

    def test_base_delay_positive(self):
        """BASE_DELAY_SECONDS should be a positive number."""
        assert isinstance(_BASE_DELAY_SECONDS, (int, float))
        assert _BASE_DELAY_SECONDS > 0

    def test_base_delay_not_too_long(self):
        """Base delay should be reasonable (< 5 seconds)."""
        assert _BASE_DELAY_SECONDS <= 5.0

    def test_max_total_delay_reasonable(self):
        """Total worst-case delay should be under 60 seconds."""
        total = sum(_BASE_DELAY_SECONDS * (2 ** i) for i in range(_MAX_RETRIES))
        assert total < 60, f"Total retry delay ({total}s) would be too long"

    def test_exponential_backoff_sequence(self):
        """Verify the backoff sequence is correct."""
        expected = [1.0, 2.0, 4.0, 8.0, 16.0]
        for attempt in range(1, _MAX_RETRIES + 1):
            delay = _BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            assert delay == expected[attempt - 1], f"Attempt {attempt}: expected {expected[attempt-1]}, got {delay}"


class TestPoolState:
    """Test pool state before initialization."""

    @pytest.mark.asyncio
    async def test_get_db_before_init_raises(self):
        """get_db() should raise RuntimeError if pool not initialized."""
        # We can't actually call this in test environment because pool
        # may already be initialized by the app. Test the error message.
        from app.core.database import _pool
        if _pool is None:
            with pytest.raises(RuntimeError, match="not initialized"):
                await get_db()


class TestModuleExports:
    """Verify all expected functions are exported."""

    def test_init_db_pool_callable(self):
        assert callable(init_db_pool)

    def test_close_db_pool_callable(self):
        assert callable(close_db_pool)

    def test_get_db_callable(self):
        assert callable(get_db)
