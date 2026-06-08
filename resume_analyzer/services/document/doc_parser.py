"""Microsoft Word legacy (.doc) parsing service."""

import tempfile
from pathlib import Path
from typing import Tuple

from miette import DocReader
from miette.exceptions import MietteFormatError

from resume_analyzer.utils.logger import get_logger
from resume_analyzer.utils.text_cleaner import clean_text

logger = get_logger(__name__)


class DocParser:
    """Extract and validate text from legacy Word (.doc) files."""

    def validate_doc(self, source: bytes) -> Tuple[bool, str]:
        """
        Validate that the input is a readable .doc file.

        Args:
            source: Raw file content.

        Returns:
            Tuple of (is_valid, message).
        """
        try:
            raw = self._extract_raw_text(source)
            if not raw.strip():
                return False, "Word document appears to be empty."
            return True, "Valid Word document."
        except MietteFormatError as exc:
            logger.warning("DOC validation failed: %s", exc)
            return False, f"Invalid or corrupted Word document: {exc}"
        except Exception as exc:
            logger.warning("DOC validation failed: %s", exc)
            return False, f"Invalid or corrupted Word document: {exc}"

    def extract_text(self, source: bytes) -> str:
        """
        Extract and clean all text from a legacy Word resume.

        Args:
            source: Raw file content.

        Returns:
            Cleaned resume text.

        Raises:
            ValueError: If extraction fails.
        """
        try:
            raw = self._extract_raw_text(source)
            if not raw.strip():
                raise ValueError("Word document contains no extractable text.")
            return clean_text(raw)
        except ValueError:
            raise
        except MietteFormatError as exc:
            raise ValueError(f"Invalid or corrupted Word document: {exc}") from exc
        except Exception as exc:
            raise ValueError(f"Failed to extract Word document text: {exc}") from exc

    def extract_from_upload(self, uploaded_bytes: bytes) -> str:
        """
        Convenience method for Streamlit uploaded file bytes.

        Args:
            uploaded_bytes: Raw file content.

        Returns:
            Extracted text.
        """
        valid, message = self.validate_doc(uploaded_bytes)
        if not valid:
            raise ValueError(message)
        return self.extract_text(uploaded_bytes)

    def _extract_raw_text(self, source: bytes) -> str:
        """Write bytes to a temp file and read text with miette."""
        path = self._write_temp_file(source)
        try:
            with DocReader(path) as doc:
                return doc.read().decode("utf-8")
        finally:
            path.unlink(missing_ok=True)

    def _write_temp_file(self, source: bytes) -> Path:
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as tmp:
            tmp.write(source)
            return Path(tmp.name)
