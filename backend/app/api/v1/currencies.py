"""
PredictIQ API — Currency Endpoints
Fetches live exchange rates for frontend use.
Public endpoints — no auth required.
"""

from fastapi import APIRouter
import structlog

from app.services.currency_service import currency_service

router = APIRouter(prefix="/currencies", tags=["Currencies"])
logger = structlog.get_logger()

# Common currencies shown at the top of the currency selector
PRIORITY_CURRENCIES = [
    {"code": "USD", "name": "US Dollar", "symbol": "$"},
    {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
    {"code": "EUR", "name": "Euro", "symbol": "€"},
    {"code": "GBP", "name": "British Pound", "symbol": "£"},
    {"code": "AED", "name": "UAE Dirham", "symbol": "د.إ"},
    {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$"},
    {"code": "CAD", "name": "Canadian Dollar", "symbol": "CA$"},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
    {"code": "CHF", "name": "Swiss Franc", "symbol": "Fr"},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
    {"code": "HKD", "name": "Hong Kong Dollar", "symbol": "HK$"},
    {"code": "MXN", "name": "Mexican Peso", "symbol": "$"},
    {"code": "BRL", "name": "Brazilian Real", "symbol": "R$"},
    {"code": "KRW", "name": "South Korean Won", "symbol": "₩"},
    {"code": "NZD", "name": "New Zealand Dollar", "symbol": "NZ$"},
    {"code": "SEK", "name": "Swedish Krona", "symbol": "kr"},
    {"code": "NOK", "name": "Norwegian Krone", "symbol": "kr"},
    {"code": "DKK", "name": "Danish Krone", "symbol": "kr"},
    {"code": "ZAR", "name": "South African Rand", "symbol": "R"},
]


@router.get("/rates")
async def get_rates():
    """
    Get all exchange rates from USD.

    Response: { base: "USD", rates: {inr: 84.2, eur: 0.92, ...}, status: {...} }
    Frontend caches this response for 1 hour.
    """
    rates = await currency_service.get_rates()
    return {
        "base": "USD",
        "rates": rates,
        "status": currency_service.get_status(),
    }


@router.get("/supported")
async def get_supported():
    """
    Get the list of priority currencies + metadata.

    Used to populate the currency selector dropdown.
    """
    rates = await currency_service.get_rates()
    return {
        "priority": PRIORITY_CURRENCIES,
        "total_available": len(rates),
    }
