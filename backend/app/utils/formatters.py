"""
PredictIQ — Response Formatting Utilities
Standard formatting for API responses, currency, and metrics.
"""


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a monetary amount as a human-readable string."""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def format_hours(hours: float) -> str:
    """Format effort hours as a readable string."""
    if hours >= 10000:
        return f"{hours / 1000:.1f}K hours"
    return f"{hours:,.0f} hours"


def format_weeks(weeks: float) -> str:
    """Format timeline weeks as a readable string."""
    return f"{weeks:.1f} weeks"


def format_confidence(pct: float) -> str:
    """Format confidence percentage as a readable string."""
    return f"{pct:.0f}% confident"


def build_api_response(data: dict, meta: dict | None = None) -> dict:
    """Wrap data in a standard API response envelope."""
    response = {"success": True, "data": data}
    if meta:
        response["meta"] = meta
    return response


def build_error_response(code: str, message: str, request_id: str = "") -> dict:
    """Build a standard error response body."""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        },
    }
