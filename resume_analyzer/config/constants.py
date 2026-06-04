"""Application-wide constants."""

from typing import Final

ATS_WEIGHTS: Final[dict[str, int]] = {
    "skills_match": 40,
    "experience": 25,
    "education": 15,
    "completeness": 10,
    "formatting": 10,
}

GRADE_THRESHOLDS: Final[list[tuple[int, str]]] = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0, "F"),
]

SECTION_KEYWORDS: Final[dict[str, list[str]]] = {
    "experience": ["experience", "employment", "work history", "professional"],
    "education": ["education", "academic", "qualification", "degree"],
    "skills": ["skills", "technical skills", "competencies", "technologies"],
    "projects": ["projects", "portfolio"],
    "certifications": ["certifications", "certificates", "licenses"],
}

EMAIL_PATTERN: Final[str] = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN: Final[str] = r"\+?[\d\s\-().]{10,18}"
LINKEDIN_PATTERN: Final[str] = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?"
GITHUB_PATTERN: Final[str] = r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?"

DEGREE_KEYWORDS: Final[list[str]] = [
    "bachelor",
    "master",
    "phd",
    "b.sc",
    "b.s",
    "m.sc",
    "mba",
    "b.tech",
    "m.tech",
    "associate",
    "diploma",
    "computer science",
    "software engineering",
    "information technology",
]

EXPERIENCE_YEAR_PATTERN: Final[str] = r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?"
