"""
Predictify — Export Service Tests
Tests for PDF generation and currency formatting in export_service.py
"""
import pytest
from app.services.export_service import (
    _format_currency, generate_pdf_report,
    CURRENCY_SYMBOLS, BRAND_BLUE, BRAND_DARK,
)


# ── Sample estimate fixture ────────────────────────────────────

def _make_estimate(project_name="Test Project"):
    """Create a minimal estimate dict for testing PDF generation."""
    return {
        "project_name": project_name,
        "inputs": {
            "project_type": "Web App",
            "complexity": "Medium",
            "methodology": "Agile",
            "team_size": 5,
            "duration_months": 6,
            "hourly_rate_usd": 75.0,
            "tech_stack": ["Python", "React"],
        },
        "outputs": {
            "cost_min_usd": 50000,
            "cost_likely_usd": 85000,
            "cost_max_usd": 120000,
            "effort_min_hours": 500,
            "effort_likely_hours": 850,
            "effort_max_hours": 1200,
            "timeline_min_weeks": 12.0,
            "timeline_likely_weeks": 18.0,
            "timeline_max_weeks": 24.0,
            "confidence_pct": 72,
            "risk_score": 45,
            "risk_level": "Medium",
            "phase_breakdown": [
                {"phase": "Planning", "effort_hours": 100, "cost_usd": 7500,
                 "duration_weeks": 2.0, "pct_of_total": 12},
                {"phase": "Development", "effort_hours": 500, "cost_usd": 37500,
                 "duration_weeks": 10.0, "pct_of_total": 59},
            ],
            "top_risks": [
                {"name": "Scope Creep", "severity": "High",
                 "description": "Requirements may expand."},
                {"name": "Tech Debt", "severity": "Medium",
                 "description": "Legacy integration challenges."},
            ],
            "model_loaded": True,
            "function_points": 280,
        },
    }


# ── Currency Formatting Tests ──────────────────────────────────

class TestFormatCurrency:
    """Tests for _format_currency() helper."""

    def test_usd_basic(self):
        result = _format_currency(1000, "USD", "$")
        assert result == "$1,000"

    def test_usd_large_amount(self):
        result = _format_currency(1234567, "USD", "$")
        assert result == "$1,234,567"

    def test_inr_lakhs(self):
        """INR amounts >= 1L should use lakh notation."""
        result = _format_currency(500000, "INR", "₹")
        assert "L" in result
        assert "₹" in result

    def test_inr_crores(self):
        """INR amounts >= 1Cr should use crore notation."""
        result = _format_currency(10000000, "INR", "₹")
        assert "Cr" in result
        assert "₹" in result

    def test_inr_below_lakh(self):
        """INR amounts below 1L should use standard formatting."""
        result = _format_currency(50000, "INR", "₹")
        assert "₹" in result
        assert "L" not in result
        assert "Cr" not in result

    def test_jpy_no_decimals(self):
        """JPY should not have decimal places."""
        result = _format_currency(1000.50, "JPY", "¥")
        assert "." not in result
        assert "¥" in result

    def test_eur_formatting(self):
        result = _format_currency(5000, "EUR", "€")
        assert "€" in result
        assert "5,000" in result

    def test_zero_amount(self):
        result = _format_currency(0, "USD", "$")
        assert "$" in result
        assert "0" in result


class TestCurrencySymbols:
    """Tests for CURRENCY_SYMBOLS dictionary."""

    def test_common_currencies_present(self):
        for code in ["USD", "EUR", "GBP", "INR", "JPY", "AED"]:
            assert code in CURRENCY_SYMBOLS

    def test_symbols_are_strings(self):
        for code, symbol in CURRENCY_SYMBOLS.items():
            assert isinstance(symbol, str)
            assert len(symbol) >= 1


# ── PDF Generation Tests ───────────────────────────────────────

class TestGeneratePDFReport:
    """Tests for generate_pdf_report()."""

    def test_returns_bytes(self):
        """PDF output must be bytes."""
        pdf = generate_pdf_report(_make_estimate())
        assert isinstance(pdf, bytes)

    def test_pdf_not_empty(self):
        """Generated PDF must have content."""
        pdf = generate_pdf_report(_make_estimate())
        assert len(pdf) > 100  # Real PDFs are thousands of bytes

    def test_pdf_header_magic(self):
        """PDF must start with %PDF magic bytes."""
        pdf = generate_pdf_report(_make_estimate())
        assert pdf[:5] == b"%PDF-"

    def test_pdf_with_inr(self):
        """PDF should generate successfully with INR currency."""
        pdf = generate_pdf_report(
            _make_estimate(), currency_code="INR", exchange_rate=83.5
        )
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100

    def test_pdf_with_eur(self):
        """PDF should generate successfully with EUR currency."""
        pdf = generate_pdf_report(
            _make_estimate(), currency_code="EUR", exchange_rate=0.92
        )
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100

    def test_pdf_with_empty_phases(self):
        """PDF should handle missing phase breakdown gracefully."""
        est = _make_estimate()
        est["outputs"]["phase_breakdown"] = []
        pdf = generate_pdf_report(est)
        assert isinstance(pdf, bytes)

    def test_pdf_with_empty_risks(self):
        """PDF should handle missing risks gracefully."""
        est = _make_estimate()
        est["outputs"]["top_risks"] = []
        pdf = generate_pdf_report(est)
        assert isinstance(pdf, bytes)

    def test_pdf_with_missing_inputs(self):
        """PDF should handle empty inputs dict."""
        est = _make_estimate()
        est["inputs"] = {}
        pdf = generate_pdf_report(est)
        assert isinstance(pdf, bytes)

    def test_pdf_with_benchmark(self):
        """PDF with benchmark comparison should work."""
        est = _make_estimate()
        est["outputs"]["benchmark_comparison"] = "Your project is 15% below industry average."
        est["outputs"]["model_explanation"] = "Key factors: team size, complexity."
        pdf = generate_pdf_report(est)
        assert isinstance(pdf, bytes)
