"""Work experience extraction from resume text."""

import re
from typing import List, Optional

from resume_analyzer.config.constants import EXPERIENCE_YEAR_PATTERN, SECTION_KEYWORDS
from resume_analyzer.models.resume_model import ExperienceEntry
from resume_analyzer.utils.text_cleaner import tokenize_lines


class ExperienceExtractor:
    """Extract companies, titles, and years of experience."""

    DATE_RANGE = re.compile(
        r"(?:(\d{4})\s*[-–—]\s*(?:Present|(\d{4})))|"
        r"((\d+(?:\.\d+)?)\s*(?:\+)?\s*years?)",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> tuple[List[ExperienceEntry], float]:
        """
        Extract experience entries and total years.

        Args:
            text: Resume text.

        Returns:
            Tuple of (entries, total_experience_years).
        """
        section = self._get_experience_section(text)
        lines = tokenize_lines(section or text)
        entries: List[ExperienceEntry] = []
        explicit_years = self._find_explicit_years(text)

        for i, line in enumerate(lines):
            if "—" in line or " - " in line or self.DATE_RANGE.search(line):
                entry = self._parse_experience_line(line)
                if entry.company or entry.job_title:
                    entries.append(entry)

        total = explicit_years if explicit_years else self._calculate_from_ranges(text)
        if not total and entries:
            total = sum(e.duration_years or 0 for e in entries)

        return entries, round(total, 1)

    def _parse_experience_line(self, line: str) -> ExperienceEntry:
        """Parse a single experience line."""
        entry = ExperienceEntry()
        parts = re.split(r"\s*[—\-–]\s*", line, maxsplit=2)
        if len(parts) >= 2:
            entry.job_title = parts[0].strip()
            entry.company = parts[1].strip()
        else:
            entry.job_title = line.strip()

        years_match = re.search(EXPERIENCE_YEAR_PATTERN, line, re.IGNORECASE)
        if years_match:
            entry.duration_years = float(years_match.group(1))

        range_match = re.search(r"(\d{4})\s*[-–—]\s*(?:Present|(\d{4}))", line, re.I)
        if range_match:
            start = int(range_match.group(1))
            end_year = range_match.group(2)
            end = int(end_year) if end_year else 2026
            entry.duration_years = max(end - start, 0)

        return entry

    def _find_explicit_years(self, text: str) -> float:
        """Find phrases like '3 years of experience'."""
        patterns = [
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
            r"experience[:\s]+(\d+(?:\.\d+)?)\s*years?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return 0.0

    def _calculate_from_ranges(self, text: str) -> float:
        """Sum years from date ranges in experience section."""
        total = 0.0
        for match in re.finditer(
            r"(\d{4})\s*[-–—]\s*(?:Present|(\d{4}))", text, re.IGNORECASE
        ):
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else 2026
            total += max(end - start, 0)
        return total

    def _get_experience_section(self, text: str) -> Optional[str]:
        """Isolate experience section."""
        keywords = SECTION_KEYWORDS.get("experience", [])
        lines = text.split("\n")
        capture = False
        collected: List[str] = []
        for line in lines:
            lower = line.lower().strip()
            if any(kw in lower for kw in keywords) and len(lower) < 40:
                capture = True
                continue
            if capture and "education" in lower and len(lower) < 30:
                break
            if capture:
                collected.append(line)
        return "\n".join(collected) if collected else None
