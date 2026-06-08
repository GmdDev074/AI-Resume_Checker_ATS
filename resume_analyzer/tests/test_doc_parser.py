"""Tests for legacy Word (.doc) parser module."""

from pathlib import Path

import pytest

from resume_analyzer.services.document.doc_parser import DocParser
from resume_analyzer.utils.file_utils import is_resume_upload, resume_file_kind

_FIXTURE_DOC = Path(__file__).resolve().parent / "fixtures" / "simple.doc"


@pytest.fixture
def sample_doc_bytes() -> bytes:
    """Load a minimal legacy Word document used by the miette test suite."""
    if not _FIXTURE_DOC.exists():
        pytest.skip("simple.doc fixture missing")
    return _FIXTURE_DOC.read_bytes()


class TestDocParser:
    """Legacy Word parser unit tests."""

    def test_validate_invalid_bytes(self) -> None:
        """Corrupted bytes should fail validation."""
        parser = DocParser()
        valid, _ = parser.validate_doc(b"not a doc")
        assert valid is False

    def test_extract_text_from_doc(self, sample_doc_bytes: bytes) -> None:
        """Parser extracts text from a valid legacy .doc file."""
        parser = DocParser()
        text = parser.extract_from_upload(sample_doc_bytes)
        assert "One two three four five" in text


class TestResumeFileHelpers:
    """Resume upload extension helpers for legacy Word."""

    def test_is_resume_upload_includes_doc(self) -> None:
        """Legacy .doc extension is supported."""
        assert is_resume_upload("resume.doc")
        assert is_resume_upload("resume.DOC")

    def test_resume_file_kind_doc(self) -> None:
        """File kind distinguishes .doc from .docx."""
        assert resume_file_kind("cv.docx") == "docx"
        assert resume_file_kind("cv.doc") == "doc"
