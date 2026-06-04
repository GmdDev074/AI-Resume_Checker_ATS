"""Tests for PDF parser module."""

import pytest

from resume_analyzer.services.pdf.pdf_parser import PDFParser
from resume_analyzer.utils.text_cleaner import clean_text


class TestPDFParser:
    """PDF parser unit tests."""

    def test_validate_invalid_bytes(self) -> None:
        """Corrupted bytes should fail validation."""
        parser = PDFParser()
        valid, _ = parser.validate_pdf(b"not a pdf")
        assert valid is False

    def test_clean_text_removes_extra_whitespace(self) -> None:
        """Text cleaner normalizes whitespace."""
        raw = "Hello   World\n\n\nTest"
        cleaned = clean_text(raw)
        assert "  " not in cleaned.replace("\n", "")
        assert "Hello World" in cleaned
