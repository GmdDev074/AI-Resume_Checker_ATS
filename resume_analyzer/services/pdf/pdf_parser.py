"""PDF parsing service using PyMuPDF."""

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Tuple, Union

import fitz

from resume_analyzer.utils.logger import get_logger
from resume_analyzer.utils.text_cleaner import clean_text

logger = get_logger(__name__)


class PDFParser:
    """Extract and validate text from resume PDF files."""

    def validate_pdf(self, source: Union[bytes, BinaryIO, Path]) -> Tuple[bool, str]:
        """
        Validate that the input is a readable PDF.

        Args:
            source: File bytes, stream, or path.

        Returns:
            Tuple of (is_valid, message).
        """
        try:
            doc = self._open_document(source)
            if doc.page_count == 0:
                doc.close()
                return False, "PDF has no pages."
            doc.close()
            return True, "Valid PDF."
        except Exception as exc:
            logger.warning("PDF validation failed: %s", exc)
            return False, f"Invalid or corrupted PDF: {exc}"

    def load_pdf(self, source: Union[bytes, BinaryIO, Path]) -> fitz.Document:
        """
        Load a PDF document.

        Args:
            source: File bytes, stream, or path.

        Returns:
            Open PyMuPDF document (caller should close).

        Raises:
            ValueError: If PDF cannot be opened.
        """
        try:
            return self._open_document(source)
        except Exception as exc:
            raise ValueError(f"Failed to load PDF: {exc}") from exc

    def extract_text(self, source: Union[bytes, BinaryIO, Path]) -> str:
        """
        Extract and clean all text from a PDF resume.

        Args:
            source: File bytes, stream, or path.

        Returns:
            Cleaned resume text.

        Raises:
            ValueError: If extraction fails.
        """
        doc = None
        try:
            doc = self.load_pdf(source)
            pages: list[str] = []
            for page in doc:
                pages.append(page.get_text("text"))
            raw = "\n".join(pages)
            return clean_text(raw)
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Failed to extract PDF text: {exc}") from exc
        finally:
            if doc is not None:
                doc.close()

    def _open_document(self, source: Union[bytes, BinaryIO, Path]) -> fitz.Document:
        """Open document from various input types."""
        if isinstance(source, Path):
            return fitz.open(str(source))
        if isinstance(source, bytes):
            return fitz.open(stream=source, filetype="pdf")
        if hasattr(source, "read"):
            data = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            return fitz.open(stream=data, filetype="pdf")
        raise TypeError("Unsupported PDF source type.")

    def extract_from_upload(self, uploaded_bytes: bytes) -> str:
        """
        Convenience method for Streamlit uploaded file bytes.

        Args:
            uploaded_bytes: Raw file content.

        Returns:
            Extracted text.
        """
        valid, message = self.validate_pdf(uploaded_bytes)
        if not valid:
            raise ValueError(message)
        return self.extract_text(BytesIO(uploaded_bytes))
