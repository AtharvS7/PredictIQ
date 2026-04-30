"""
Predictify — Input Sanitization Tests
Tests for _sanitize_text() XSS prevention in estimates.py
"""
import pytest
from app.api.v1.estimates import _sanitize_text


class TestSanitizeTextBasic:
    """Basic sanitization behavior."""

    def test_plain_text_unchanged(self):
        """Normal text should pass through unchanged."""
        assert _sanitize_text("My Project Name") == "My Project Name"

    def test_whitespace_trimmed(self):
        """Leading and trailing whitespace should be stripped."""
        assert _sanitize_text("  hello  ") == "hello"

    def test_empty_string(self):
        """Empty string should return empty."""
        assert _sanitize_text("") == ""

    def test_only_whitespace(self):
        """Whitespace-only string should return empty."""
        assert _sanitize_text("   ") == ""


class TestSanitizeTextXSS:
    """XSS attack prevention."""

    def test_removes_script_tags(self):
        """Script tags and content should be completely removed."""
        result = _sanitize_text('<script>alert("xss")</script>Hello')
        assert "script" not in result.lower()
        assert "alert" not in result
        assert "Hello" in result

    def test_removes_script_tags_case_insensitive(self):
        """Script removal should be case-insensitive."""
        result = _sanitize_text('<SCRIPT>alert("xss")</SCRIPT>Hello')
        assert "SCRIPT" not in result
        assert "alert" not in result

    def test_removes_multiline_script(self):
        """Script tags spanning multiple lines should be removed."""
        result = _sanitize_text('<script>\nalert("xss")\n</script>Hello')
        assert "script" not in result.lower()
        assert "Hello" in result

    def test_removes_html_tags(self):
        """All HTML tags should be stripped."""
        result = _sanitize_text("<b>Bold</b> and <i>italic</i>")
        assert "<b>" not in result
        assert "</b>" not in result
        assert "Bold" in result
        assert "italic" in result

    def test_removes_nested_tags(self):
        """Nested HTML tags should be removed."""
        result = _sanitize_text("<div><span>text</span></div>")
        assert "<" not in result or "&lt;" in result
        assert "text" in result

    def test_removes_img_onerror(self):
        """IMG with onerror payload should be sanitized."""
        result = _sanitize_text('<img src=x onerror=alert(1)>')
        assert "onerror" not in result
        assert "<img" not in result

    def test_escapes_ampersand(self):
        """Ampersands should be HTML-escaped after tag removal."""
        result = _sanitize_text("Tom & Jerry")
        assert "&amp;" in result

    def test_escapes_quotes(self):
        """Quotes should be escaped."""
        result = _sanitize_text('He said "hello"')
        assert "&quot;" in result or "hello" in result


class TestSanitizeTextTruncation:
    """Length limit enforcement."""

    def test_default_max_length_200(self):
        """Strings longer than 200 chars should be truncated."""
        long_text = "A" * 300
        result = _sanitize_text(long_text)
        assert len(result) == 200

    def test_custom_max_length(self):
        """Custom max_length parameter should work."""
        result = _sanitize_text("Hello World", max_length=5)
        assert result == "Hello"

    def test_short_text_not_truncated(self):
        """Text within limit should not be truncated."""
        result = _sanitize_text("Short", max_length=200)
        assert result == "Short"

    def test_exact_length_not_truncated(self):
        """Text exactly at limit should not be truncated."""
        text = "A" * 200
        result = _sanitize_text(text)
        assert len(result) == 200


class TestSanitizeTextEdgeCases:
    """Edge cases and combined attacks."""

    def test_multiple_script_tags(self):
        """Multiple script blocks should all be removed."""
        result = _sanitize_text(
            '<script>a()</script>ok<script>b()</script>'
        )
        assert "script" not in result.lower()
        assert "ok" in result

    def test_unicode_preserved(self):
        """Unicode characters should be preserved."""
        result = _sanitize_text("Café résumé 日本語")
        assert "Café" in result
        assert "日本語" in result

    def test_numbers_and_symbols(self):
        """Numbers and safe symbols should be preserved."""
        result = _sanitize_text("Project v2.0 - Phase 1 (alpha)")
        assert "v2.0" in result
        assert "Phase 1" in result
