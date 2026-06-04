"""Contact information extraction from resume text."""

import re
from typing import List, Optional

from resume_analyzer.config.constants import (
    EMAIL_PATTERN,
    GITHUB_PATTERN,
    LINKEDIN_PATTERN,
    PHONE_PATTERN,
)
from resume_analyzer.models.resume_model import ContactInfo
from resume_analyzer.utils.text_cleaner import tokenize_lines


class ContactExtractor:
    """Extract name, email, phone, and social links using regex."""

    def extract(self, text: str) -> ContactInfo:
        """
        Extract contact fields from resume text.

        Args:
            text: Full resume text.

        Returns:
            Populated ContactInfo.
        """
        return ContactInfo(
            name=self._extract_name(text),
            email=self._extract_email(text),
            phone=self._extract_phone(text),
            linkedin=self._extract_linkedin(text),
            github=self._extract_github(text),
        )

    def _extract_email(self, text: str) -> Optional[str]:
        """Find first email address."""
        match = re.search(EMAIL_PATTERN, text, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Find first plausible phone number."""
        for match in re.finditer(PHONE_PATTERN, text):
            digits = re.sub(r"\D", "", match.group(0))
            if 10 <= len(digits) <= 15:
                return match.group(0).strip()
        return None

    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Find LinkedIn profile URL."""
        match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_github(self, text: str) -> Optional[str]:
        """Find GitHub profile URL."""
        match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_name(self, text: str) -> Optional[str]:
        """
        Heuristic: first non-empty line that is not contact metadata.

        Args:
            text: Resume text.

        Returns:
            Candidate name or None.
        """
        lines = tokenize_lines(text)
        skip_keywords = ("email", "phone", "linkedin", "github", "http", "@", "summary")
        for line in lines[:8]:
            lower = line.lower()
            if any(kw in lower for kw in skip_keywords):
                continue
            if len(line.split()) <= 6 and len(line) < 60:
                if not re.search(r"\d{4}", line):
                    return line.title() if line.isupper() else line
        return None
