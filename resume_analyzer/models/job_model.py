"""Data models for job descriptions."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class JobDescription:
    """Structured job description for matching."""

    raw_text: str = ""
    title: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    job_id: Optional[str] = None

    @property
    def all_skills(self) -> List[str]:
        """Combine required and preferred skills uniquely."""
        seen: set[str] = set()
        combined: List[str] = []
        for skill in self.required_skills + self.preferred_skills:
            key = skill.lower()
            if key not in seen:
                seen.add(key)
                combined.append(skill)
        return combined
