"""Education section extraction from resume text."""

import re
from typing import List, Optional

from resume_analyzer.config.constants import DEGREE_KEYWORDS, SECTION_KEYWORDS
from resume_analyzer.models.resume_model import EducationEntry
from resume_analyzer.utils.text_cleaner import tokenize_lines


class EducationExtractor:
    """Extract degree, university, and graduation year."""

    YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

    def extract(self, text: str) -> List[EducationEntry]:
        """
        Extract education entries from resume.

        Args:
            text: Full resume text.

        Returns:
            List of EducationEntry objects.
        """
        section = self._get_section(text, "education")
        lines = tokenize_lines(section or text)
        entries: List[EducationEntry] = []
        current = EducationEntry()

        for line in lines:
            lower = line.lower()
            if self._is_degree_line(lower):
                if current.degree and (current.university or current.graduation_year):
                    entries.append(current)
                    current = EducationEntry()
                current.degree = line.strip()
            elif self.YEAR_PATTERN.search(line):
                years = self.YEAR_PATTERN.findall(line)
                if years:
                    match = self.YEAR_PATTERN.search(line)
                    if match:
                        current.graduation_year = match.group(0)
                if not current.university and (
                    "university" in lower or "college" in lower
                ):
                    current.university = line.strip()
                elif not current.university:
                    current.university = re.sub(
                        r"\b(19|20)\d{2}\b", "", line
                    ).strip(" -–—|,.")

            elif any(kw in lower for kw in ("university", "college", "institute", "school")):
                current.university = line.strip()

        if current.degree or current.university:
            entries.append(current)

        if not entries:
            entries = [self._fallback_extract(text)]
        return [e for e in entries if e.degree or e.university]

    def _is_degree_line(self, lower: str) -> bool:
        """Check if line describes a degree."""
        return any(kw in lower for kw in DEGREE_KEYWORDS)

    def _get_section(self, text: str, section: str) -> Optional[str]:
        """Extract text under a section heading."""
        keywords = SECTION_KEYWORDS.get(section, [])
        lines = text.split("\n")
        capture = False
        collected: List[str] = []
        for line in lines:
            lower = line.lower().strip()
            if any(kw in lower for kw in keywords) and len(lower) < 40:
                capture = True
                continue
            if capture and any(
                kw in lower
                for kw in SECTION_KEYWORDS.get("experience", [])
                + SECTION_KEYWORDS.get("skills", [])
            ) and len(lower) < 40:
                break
            if capture:
                collected.append(line)
        return "\n".join(collected) if collected else None

    def _fallback_extract(self, text: str) -> EducationEntry:
        """Best-effort single education entry."""
        entry = EducationEntry()
        for line in tokenize_lines(text):
            lower = line.lower()
            if self._is_degree_line(lower) and not entry.degree:
                entry.degree = line.strip()
            if self.YEAR_PATTERN.search(line) and not entry.graduation_year:
                match = self.YEAR_PATTERN.search(line)
                if match:
                    entry.graduation_year = match.group(0)
            if "university" in lower or "college" in lower:
                entry.university = line.strip()
        return entry
