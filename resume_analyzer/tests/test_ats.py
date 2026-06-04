"""Tests for ATS scoring service."""

from resume_analyzer.models.job_model import JobDescription
from resume_analyzer.models.resume_model import ContactInfo, ResumeData
from resume_analyzer.services.ats.ats_scoring_service import ATSScoringService


class TestATSScoringService:
    """ATS scoring tests."""

    def test_score_within_range(self) -> None:
        """ATS score should be between 0 and 100."""
        resume = ResumeData(
            raw_text="Skills: Python, Flask\nExperience: 3 years\nEducation: BSc CS 2024",
            contact=ContactInfo(email="a@b.com", phone="+1234567890"),
            skills=["Python", "Flask", "Git", "SQL"],
            total_experience_years=3.0,
        )
        job = JobDescription(
            raw_text="Python Flask Git SQL REST",
            required_skills=["Python", "Flask", "Docker"],
        )
        result = ATSScoringService().calculate(resume, job)
        assert 0 <= result.ats_score <= 100
        assert result.grade in {"A+", "A", "B", "C", "D", "F"}
        assert "skills_match" in result.breakdown
