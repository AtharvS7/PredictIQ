"""
Predictify — Currency Service & Endpoint Tests
Tests the live exchange rate fetching, caching, and conversion logic.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from app.services.currency_service import (
    CurrencyService,
    EMERGENCY_FALLBACK_RATES,
)


@pytest.fixture
def fresh_service():
    """Return a fresh CurrencyService instance (no cached rates)."""
    return CurrencyService()


class TestCurrencyService:
    """Tests for the CurrencyService class."""

    def test_convert_usd_to_usd_is_identity(self):
        """Converting USD to USD should return the original amount."""
        service = CurrencyService()
        result = asyncio.run(service.convert(100.0, "USD"))
        assert result == 100.0

    def test_convert_usd_uppercase(self):
        """Currency codes should be case-insensitive."""
        service = CurrencyService()
        result = asyncio.run(service.convert(100.0, "usd"))
        assert result == 100.0

    def test_convert_unknown_currency_returns_usd(self):
        """Unknown currency codes should return the original USD amount."""
        service = CurrencyService()
        result = asyncio.run(service.convert(100.0, "XYZ"))
        assert result == 100.0

    def test_currency_service_has_fallback(self):
        """If API fails on first run, emergency fallback rates are used."""
        service = CurrencyService()

        # Mock the fetch to always fail
        async def mock_fetch():
            return {}

        with patch.object(service, "_fetch_rates", mock_fetch):
            rates = asyncio.run(service.get_rates())
            assert len(rates) > 0
            assert "inr" in rates
            assert rates["inr"] == EMERGENCY_FALLBACK_RATES["inr"]

    def test_get_rate_usd(self):
        """get_rate('USD') should always return 1.0."""
        service = CurrencyService()
        rate = asyncio.run(service.get_rate("USD"))
        assert rate == 1.0

    def test_get_status_initial(self):
        """Status should show zero currencies on fresh instance."""
        service = CurrencyService()
        status = service.get_status()
        assert status["currencies_loaded"] == 0
        assert status["last_fetch_date"] == "never"

    def test_fallback_rates_have_inr(self):
        """Emergency fallback rates must contain INR > 0."""
        assert "inr" in EMERGENCY_FALLBACK_RATES
        assert EMERGENCY_FALLBACK_RATES["inr"] > 0
