"""
Predictify — Document Parser Tests
Tests for PDF, DOCX, and TXT text extraction.
"""
import io
import pytest
from app.services.document_parser import DocumentParser


class TestTxtParsing:
    """Tests for plain text document parsing."""

    def test_parse_txt_returns_dict(self):
        """Parsing UTF-8 text should return a dictionary."""
        content = b"This is a sample project specification document with enough text to parse properly."
        result = DocumentParser.parse(content, "text/plain")
        assert isinstance(result, dict)

    def test_parse_txt_has_raw_text(self):
        """Result must contain a raw_text key."""
        content = b"Project specification for a CRM system. Features include contact management and reporting dashboards."
        result = DocumentParser.parse(content, "text/plain")
        assert "raw_text" in result
        assert len(result["raw_text"]) > 0

    def test_parse_txt_word_count(self):
        """Word count should be populated for text documents."""
        content = b"One two three four five six seven eight nine ten eleven twelve."
        result = DocumentParser.parse(content, "text/plain")
        assert "word_count" in result
        assert result["word_count"] >= 1

    def test_parse_txt_preview(self):
        """text_preview should contain a truncated version of the text."""
        long_text = b"This is a long document about software requirements. " * 100
        result = DocumentParser.parse(long_text, "text/plain")
        assert "text_preview" in result


class TestUnsupportedFormats:
    """Tests for unsupported file types."""

    def test_unsupported_mime_raises(self):
        """Unsupported MIME types should raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported"):
            DocumentParser.parse(b"data", "application/vnd.ms-excel")

    def test_image_mime_raises(self):
        """Image MIME type should raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported"):
            DocumentParser.parse(b"data", "image/png")


class TestPdfParsing:
    """Tests for PDF parsing using a programmatically-generated PDF."""

    def _make_minimal_pdf(self, text: str = "Sample project specification") -> bytes:
        """Create a PDF in memory using ReportLab with enough content to pass validation."""
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf)
            styles = getSampleStyleSheet()
            story = []
            # Add enough text to pass the 50-char minimum
            for _ in range(10):
                story.append(Paragraph(text + " " + text, styles["Normal"]))
                story.append(Spacer(1, 0.2 * inch))
            doc.build(story)
            return buf.getvalue()
        except ImportError:
            pytest.skip("ReportLab not installed — skipping PDF test")

    def test_parse_pdf_returns_dict(self):
        """Parsing a valid PDF with sufficient text should return a dictionary."""
        pdf_bytes = self._make_minimal_pdf(
            "This is a comprehensive test project document for Predictify software cost estimation."
        )
        result = DocumentParser.parse(pdf_bytes, "application/pdf")
        assert isinstance(result, dict)
        assert "raw_text" in result


class TestDocxParsing:
    """Tests for DOCX parsing."""

    def _make_minimal_docx(self, text: str = "Sample project specification") -> bytes:
        """Create a DOCX in memory using python-docx with enough content."""
        try:
            from docx import Document
            doc = Document()
            # Add enough text to pass validation
            for _ in range(10):
                doc.add_paragraph(text + " " + text)
            buf = io.BytesIO()
            doc.save(buf)
            return buf.getvalue()
        except ImportError:
            pytest.skip("python-docx not installed — skipping DOCX test")

    def test_parse_docx_returns_dict(self):
        """Parsing a valid DOCX with sufficient text should return a dictionary."""
        docx_bytes = self._make_minimal_docx(
            "This is a comprehensive test project specification for CRM software."
        )
        result = DocumentParser.parse(
            docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert isinstance(result, dict)
        assert "raw_text" in result
