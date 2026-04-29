"""
Predictify — Shared Validation Utilities
Reusable validation functions used across backend services.
"""


def validate_effort_range(effort: float) -> bool:
    """Check if effort hours falls within the valid prediction range."""
    return 1.0 <= effort <= 100000.0


def validate_fp_range(fp: float) -> bool:
    """Check if function points falls within the valid estimation range."""
    return 5.0 <= fp <= 20000.0


def validate_hourly_rate(rate: float) -> bool:
    """Check if hourly rate is within acceptable bounds."""
    return 1.0 <= rate <= 1000.0


def sanitize_text(text: str, max_chars: int = 50000) -> str:
    """Strip whitespace and truncate text to max_chars."""
    cleaned = text.strip()
    if len(cleaned) > max_chars:
        return cleaned[:max_chars]
    return cleaned


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a numeric value to a given range."""
    return max(min_val, min(value, max_val))


def safe_divide(numerator: float, denominator: float, fallback: float = 0.0) -> float:
    """Divide safely, returning fallback if denominator is zero."""
    if denominator == 0:
        return fallback
    return numerator / denominator
