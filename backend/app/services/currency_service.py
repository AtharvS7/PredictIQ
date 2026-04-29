"""
Predictify Currency Service
===========================
Fetches live exchange rates from fawazahmed0/exchange-api.
No API key required. 200+ currencies. Daily updates via CDN.
Rates are cached in memory for CACHE_TTL_SECONDS (default 3600 = 1 hour).
On cache miss or API failure: falls back to last known rates.
On first-run failure: uses hardcoded emergency fallback rates.
"""

import asyncio
import time
from typing import Optional

import httpx
import structlog

logger = structlog.get_logger()

# Primary and fallback CDN URLs — no API key required
PRIMARY_URL = (
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest"
    "/v1/currencies/usd.json"
)
FALLBACK_URL = "https://latest.currency-api.pages.dev/v1/currencies/usd.json"

# Cache duration: 1 hour (API updates daily — 1hr is conservative)
CACHE_TTL_SECONDS = 3600

# Emergency fallback rates (as of project creation — only used if API is down)
EMERGENCY_FALLBACK_RATES: dict[str, float] = {
    "inr": 84.5,
    "eur": 0.92,
    "gbp": 0.79,
    "jpy": 152.0,
    "aed": 3.67,
    "sgd": 1.34,
    "cad": 1.36,
    "aud": 1.53,
    "chf": 0.90,
    "cny": 7.24,
    "hkd": 7.82,
    "mxn": 17.15,
    "brl": 5.05,
    "krw": 1330.0,
    "thb": 35.0,
    "myr": 4.70,
    "php": 56.5,
    "idr": 15800.0,
    "vnd": 24500.0,
    "nzd": 1.63,
}


class CurrencyService:
    """Thread-safe currency conversion service with in-memory caching."""

    def __init__(self) -> None:
        self._rates: dict[str, float] = {}
        self._last_fetched: float = 0.0
        self._fetch_date: str = "never"
        self._lock = asyncio.Lock()

    @property
    def is_cached(self) -> bool:
        """Check if cached rates are still valid."""
        return (
            bool(self._rates)
            and (time.time() - self._last_fetched) < CACHE_TTL_SECONDS
        )

    async def _fetch_rates(self) -> dict[str, float]:
        """Fetch from primary CDN, fall back to secondary if needed."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            for url in [PRIMARY_URL, FALLBACK_URL]:
                try:
                    r = await client.get(url)
                    r.raise_for_status()
                    data = r.json()
                    rates = data.get("usd", {})
                    if rates:
                        self._fetch_date = data.get("date", "unknown")
                        logger.info(
                            "currency_rates_fetched",
                            url=url,
                            date=self._fetch_date,
                            currencies=len(rates),
                        )
                        return {k.lower(): v for k, v in rates.items()}
                except Exception as e:
                    logger.warning(
                        "currency_fetch_failed",
                        url=url,
                        error=str(e),
                    )
        return {}

    async def get_rates(self) -> dict[str, float]:
        """Return cached rates or fetch fresh ones. Never raises."""
        if self.is_cached:
            return self._rates

        async with self._lock:
            # Double-checked locking: another coroutine may have fetched
            if self.is_cached:
                return self._rates

            fresh = await self._fetch_rates()
            if fresh:
                self._rates = fresh
                self._last_fetched = time.time()
            elif not self._rates:
                # First run failure: use hardcoded emergency fallback
                logger.error(
                    "currency_api_unreachable_first_run",
                    message="Using emergency fallback rates.",
                )
                self._rates = dict(EMERGENCY_FALLBACK_RATES)
                self._last_fetched = time.time()
            # else: keep last known rates — do not reset to empty

        return self._rates

    async def convert(
        self,
        amount_usd: float,
        target_currency: str,
    ) -> float:
        """
        Convert a USD amount to target_currency.

        Returns amount in target currency, or the original USD amount
        if the currency code is unknown.
        """
        code = target_currency.lower().strip()
        if code == "usd":
            return amount_usd

        rates = await self.get_rates()
        rate = rates.get(code)
        if rate is None:
            logger.warning(
                "unknown_currency_code",
                code=code,
                message="Returning USD amount unchanged.",
            )
            return amount_usd
        return amount_usd * rate

    async def get_rate(self, target_currency: str) -> Optional[float]:
        """Return exchange rate from USD to target_currency, or None."""
        code = target_currency.lower().strip()
        if code == "usd":
            return 1.0
        rates = await self.get_rates()
        return rates.get(code)

    def get_status(self) -> dict:
        """Return service status for API response."""
        return {
            "currencies_loaded": len(self._rates),
            "cache_age_seconds": int(time.time() - self._last_fetched)
            if self._last_fetched > 0
            else -1,
            "last_fetch_date": self._fetch_date,
            "is_fresh": self.is_cached,
        }


# Module-level singleton
currency_service = CurrencyService()
