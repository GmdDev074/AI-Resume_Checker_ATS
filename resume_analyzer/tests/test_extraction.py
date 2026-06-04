"""Tests for extraction services."""

from resume_analyzer.services.extraction.contact_extractor import ContactExtractor
from resume_analyzer.services.extraction.skill_extractor import SkillExtractor
from resume_analyzer.services.extraction.education_extractor import EducationExtractor
from resume_analyzer.services.extraction.experience_extractor import ExperienceExtractor

SAMPLE_RESUME = """
JOHN DOE
Email: john@example.com | Phone: +92 300 1112233
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

SKILLS
Kotlin, Android, Firebase, MVVM, Python, Git

EXPERIENCE
Android Developer — Mobile Co (2022 – Present)
3 years of experience in mobile apps

EDUCATION
Bachelor of Computer Science
University of Lahore — 2025
"""


class TestContactExtractor:
    """Contact extraction tests."""

    def test_extract_email_and_github(self) -> None:
        """Should find email and social links."""
        contact = ContactExtractor().extract(SAMPLE_RESUME)
        assert contact.email == "john@example.com"
        assert contact.github is not None


class TestSkillExtractor:
    """Skill extraction tests."""

    def test_extract_kotlin_stack(self) -> None:
        """Should detect Kotlin-related skills."""
        skills = SkillExtractor().extract("Kotlin, Android, Firebase, MVVM")
        lowered = [s.lower() for s in skills]
        assert "kotlin" in lowered
        assert "android" in lowered or "firebase" in lowered


class TestEducationExtractor:
    """Education extraction tests."""

    def test_extract_degree_and_year(self) -> None:
        """Should find degree and graduation year."""
        entries = EducationExtractor().extract(SAMPLE_RESUME)
        assert len(entries) >= 1
        assert entries[0].graduation_year == "2025" or any(
            e.graduation_year == "2025" for e in entries
        )


class TestExperienceExtractor:
    """Experience extraction tests."""

    def test_extract_total_years(self) -> None:
        """Should compute experience years."""
        _, total = ExperienceExtractor().extract(SAMPLE_RESUME)
        assert total >= 1.0
