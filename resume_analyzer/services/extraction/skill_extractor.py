"""Technical skill extraction using spaCy and skills database."""

import json
import re
from pathlib import Path
from typing import List, Optional, Set

from resume_analyzer.config.settings import Settings, get_settings
from resume_analyzer.utils.file_utils import read_json
from resume_analyzer.utils.logger import get_logger
from resume_analyzer.utils.text_cleaner import normalize_skill

logger = get_logger(__name__)


class SkillExtractor:
    """Detect skills from resume or job description text."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize extractor with skill database.

        Args:
            settings: Application settings.
        """
        self._settings = settings or get_settings()
        self._skills_db = self._load_skills_database()
        self._all_skills = self._flatten_skills()
        self._nlp = None

    def extract(self, text: str) -> List[str]:
        """
        Extract skills from text.

        Args:
            text: Resume or job description.

        Returns:
            Sorted list of unique detected skills.
        """
        found: Set[str] = set()
        lower_text = text.lower()

        for skill in self._all_skills:
            pattern = self._skill_pattern(skill)
            if re.search(pattern, lower_text, re.IGNORECASE):
                found.add(skill)

        comma_skills = self._extract_comma_separated(text)
        found.update(comma_skills)

        return sorted(found, key=str.lower)

    def extract_from_job(self, job_text: str) -> List[str]:
        """
        Extract skills specifically from a job description.

        Args:
            job_text: Job description text.

        Returns:
            List of skills.
        """
        return self.extract(job_text)

    def search_skills(self, query: str, limit: int = 20) -> List[str]:
        """
        Search skill database by substring.

        Args:
            query: Search term.
            limit: Max results.

        Returns:
            Matching skill names.
        """
        q = query.lower().strip()
        if not q:
            return self._all_skills[:limit]
        matches = [s for s in self._all_skills if q in s.lower()]
        return matches[:limit]

    def _load_skills_database(self) -> dict:
        """Load JSON skills database."""
        path = self._settings.skills_db_path
        if not path.exists():
            logger.warning("Skills database not found at %s", path)
            return {}
        return read_json(path)

    def _flatten_skills(self) -> List[str]:
        """Flatten categorized skills into one list."""
        skills: List[str] = []
        for category in self._skills_db.values():
            if isinstance(category, list):
                skills.extend(category)
        return sorted(set(skills), key=len, reverse=True)

    def _skill_pattern(self, skill: str) -> str:
        """Build word-boundary regex for a skill."""
        escaped = re.escape(skill.lower())
        escaped = escaped.replace(r"\ ", r"[\s\-]?")
        return rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"

    def _extract_comma_separated(self, text: str) -> Set[str]:
        """Match comma-separated tokens against known skills."""
        found: Set[str] = set()
        skill_lower = {s.lower(): s for s in self._all_skills}
        for line in text.split("\n"):
            if "," in line and len(line) < 200:
                for part in line.split(","):
                    token = normalize_skill(part)
                    if token.lower() in skill_lower:
                        found.add(skill_lower[token.lower()])
        return found

    def _get_nlp(self):
        """Lazy-load spaCy model when available."""
        if self._nlp is not None:
            return self._nlp
        try:
            import spacy

            self._nlp = spacy.load(self._settings.spacy_model)
        except Exception as exc:
            logger.info("spaCy model not loaded (%s); using regex matching only.", exc)
            self._nlp = False
        return self._nlp
