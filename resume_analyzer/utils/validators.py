"""Input validation utilities."""

import re
from typing import Optional, Tuple

from resume_analyzer.config.constants import EMAIL_PATTERN


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address string.

    Returns:
        True if valid format.
    """
    return bool(re.fullmatch(EMAIL_PATTERN, email.strip(), re.IGNORECASE))


def validate_job_description(text: str, min_length: int = 50) -> Tuple[bool, Optional[str]]:
    """
    Validate job description content.

    Args:
        text: Job description text.
        min_length: Minimum required characters.

    Returns:
        Tuple of (is_valid, error_message).
    """
    cleaned = text.strip()
    if not cleaned:
        return False, "Job description cannot be empty."
    if len(cleaned) < min_length:
        return False, f"Job description must be at least {min_length} characters."
    return True, None


def validate_pdf_size(size_bytes: int, max_mb: int) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded PDF size.

    Args:
        size_bytes: File size in bytes.
        max_mb: Maximum allowed megabytes.

    Returns:
        Tuple of (is_valid, error_message).
    """
    max_bytes = max_mb * 1024 * 1024
    if size_bytes > max_bytes:
        return False, f"File exceeds maximum size of {max_mb} MB."
    return True, None
