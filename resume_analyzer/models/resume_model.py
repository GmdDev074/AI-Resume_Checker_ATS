"""Data models for parsed resume content."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ContactInfo:
    """Contact details extracted from a resume."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


@dataclass
class EducationEntry:
    """Single education record."""

    degree: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[str] = None


@dataclass
class ExperienceEntry:
    """Single work experience record."""

    company: Optional[str] = None
    job_title: Optional[str] = None
    duration_years: Optional[float] = None


@dataclass
class ResumeData:
    """Structured resume representation after extraction."""

    raw_text: str = ""
    contact: ContactInfo = field(default_factory=ContactInfo)
    skills: List[str] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    experience: List[ExperienceEntry] = field(default_factory=list)
    total_experience_years: float = 0.0
    file_name: Optional[str] = None
    resume_id: Optional[int] = None

    @property
    def skills_count(self) -> int:
        """Return number of detected skills."""
        return len(self.skills)
