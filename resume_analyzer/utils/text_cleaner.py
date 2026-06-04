"""Text normalization and cleaning utilities."""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Normalize whitespace and remove control characters.

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned single-block friendly text.
    """
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name for comparison.

    Args:
        skill: Raw skill string.

    Returns:
        Lowercase trimmed skill with consistent spacing.
    """
    skill = skill.strip()
    skill = re.sub(r"\s+", " ", skill)
    return skill


def tokenize_lines(text: str) -> List[str]:
    """
    Split text into non-empty lines.

    Args:
        text: Input text.

    Returns:
        List of trimmed lines.
    """
    return [line.strip() for line in text.split("\n") if line.strip()]


def extract_words(text: str) -> List[str]:
    """
    Extract alphabetic tokens from text.

    Args:
        text: Input text.

    Returns:
        List of lowercase word tokens.
    """
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text.lower())
