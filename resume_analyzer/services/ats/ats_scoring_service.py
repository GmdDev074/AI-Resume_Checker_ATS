"""ATS (Applicant Tracking System) compatibility scoring."""

from typing import List, Optional

from resume_analyzer.config.constants import ATS_WEIGHTS, GRADE_THRESHOLDS, SECTION_KEYWORDS
from resume_analyzer.models.job_model import JobDescription
from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.models.score_model import ATSScoreResult
from resume_analyzer.services.matching.job_matching_service import JobMatchingService


class ATSScoringService:
    """Calculate ATS score out of 100 with weighted factors."""

    def __init__(self, job_matcher: Optional[JobMatchingService] = None) -> None:
        """
        Initialize ATS scorer.

        Args:
            job_matcher: Optional shared job matching service.
        """
        self._matcher = job_matcher or JobMatchingService()

    def calculate(
        self,
        resume: ResumeData,
        job: JobDescription,
    ) -> ATSScoreResult:
        """
        Compute ATS score and grade.

        Args:
            resume: Parsed resume.
            job: Job description.

        Returns:
            ATSScoreResult with breakdown.
        """
        match = self._matcher.match(resume, job)
        skills_score = self._skills_score(match.skill_overlap_ratio) * ATS_WEIGHTS["skills_match"]
        exp_score = self._experience_score(resume.total_experience_years) * ATS_WEIGHTS["experience"]
        edu_score = self._education_score(resume) * ATS_WEIGHTS["education"]
        complete_score = self._completeness_score(resume) * ATS_WEIGHTS["completeness"]
        format_score = self._formatting_score(resume.raw_text) * ATS_WEIGHTS["formatting"]

        total = skills_score + exp_score + edu_score + complete_score + format_score
        total = min(100.0, round(total, 1))

        breakdown = {
            "skills_match": round(skills_score, 1),
            "experience": round(exp_score, 1),
            "education": round(edu_score, 1),
            "completeness": round(complete_score, 1),
            "formatting": round(format_score, 1),
        }
        details = self._build_details(resume, match.missing_skills)

        return ATSScoreResult(
            ats_score=total,
            grade=self._grade(total),
            breakdown=breakdown,
            details=details,
        )

    def _skills_score(self, overlap_ratio: float) -> float:
        """Normalize skill overlap to 0-1."""
        return min(1.0, max(0.0, overlap_ratio))

    def _experience_score(self, years: float) -> float:
        """Score experience; caps at 5+ years."""
        if years <= 0:
            return 0.3
        return min(1.0, years / 5.0)

    def _education_score(self, resume: ResumeData) -> float:
        """Score based on education entries."""
        if not resume.education:
            return 0.2
        score = 0.5
        for edu in resume.education:
            if edu.degree:
                score += 0.25
            if edu.university:
                score += 0.15
            if edu.graduation_year:
                score += 0.1
        return min(1.0, score)

    def _completeness_score(self, resume: ResumeData) -> float:
        """Check presence of key resume sections."""
        checks = [
            bool(resume.contact.email),
            bool(resume.contact.phone),
            bool(resume.skills),
            bool(resume.experience or resume.total_experience_years),
            bool(resume.education),
        ]
        return sum(checks) / len(checks)

    def _formatting_score(self, text: str) -> float:
        """Heuristic formatting quality score."""
        lower = text.lower()
        score = 0.5
        for section, keywords in SECTION_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                score += 0.08
        if len(text) > 300:
            score += 0.1
        if len(text) < 100:
            score -= 0.3
        return min(1.0, max(0.0, score))

    def _grade(self, score: float) -> str:
        """Map numeric score to letter grade."""
        for threshold, grade in GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"

    def _build_details(self, resume: ResumeData, missing: List[str]) -> List[str]:
        """Generate human-readable ATS feedback."""
        details: List[str] = []
        if missing:
            details.append(f"Add missing keywords: {', '.join(missing[:8])}.")
        if not resume.contact.email:
            details.append("Include a professional email address.")
        if not resume.skills:
            details.append("Add a dedicated Skills section.")
        if resume.total_experience_years == 0:
            details.append("Clarify years of experience in summary or experience section.")
        if not details:
            details.append("Resume is well-structured for ATS parsing.")
        return details
