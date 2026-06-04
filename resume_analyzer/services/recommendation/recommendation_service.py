"""Recommendation engine for resume improvements."""

from typing import List, Optional

from resume_analyzer.models.job_model import JobDescription
from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.models.score_model import AnalysisResult, JobMatchResult


class RecommendationService:
    """Generate actionable resume and learning suggestions."""

    SKILL_LEARNING_MAP = {
        "docker": "Learn Docker Fundamentals — containerize a sample Python app.",
        "kubernetes": "Study Kubernetes basics — deploy a pod and service locally.",
        "aws": "Complete AWS Cloud Practitioner modules and build an S3 + Lambda demo.",
        "react": "Build a small React portfolio project with hooks and routing.",
        "kotlin": "Practice Kotlin Android apps with MVVM architecture.",
        "tensorflow": "Follow a TensorFlow beginner course and train a simple classifier.",
        "machine learning": "Take an ML course and implement regression/classification projects.",
        "ci/cd": "Set up a GitHub Actions pipeline for automated tests and deployment.",
        "postgresql": "Practice SQL queries and schema design with PostgreSQL exercises.",
    }

    def generate(
        self,
        resume: ResumeData,
        job: JobDescription,
        match: JobMatchResult,
    ) -> List[str]:
        """
        Generate improvement recommendations.

        Args:
            resume: Parsed resume.
            job: Job description.
            match: Job match results.

        Returns:
            List of suggestion strings.
        """
        suggestions: List[str] = []

        for skill in match.missing_skills[:10]:
            key = skill.lower()
            tip = self.SKILL_LEARNING_MAP.get(key)
            if tip:
                suggestions.append(tip)
            else:
                suggestions.append(
                    f"Add or develop skill: {skill}. Include projects that demonstrate it."
                )

        if not resume.contact.linkedin:
            suggestions.append("Add your LinkedIn profile URL in the header section.")
        if not resume.contact.github and any(
            s.lower() in {"python", "java", "javascript", "react"} for s in resume.skills
        ):
            suggestions.append("Link a GitHub profile showcasing code samples.")
        if len(resume.skills) < 8:
            suggestions.append(
                "Expand your Skills section with tools and frameworks from the job description."
            )
        if match.match_score < 70:
            suggestions.append(
                "Tailor your summary to mirror keywords from the job description."
            )
        if resume.total_experience_years < 1:
            suggestions.append(
                "Highlight internships, academic projects, and measurable achievements."
            )
        if not suggestions:
            suggestions.append(
                "Strong alignment. Fine-tune bullet points with quantified results (%, time saved)."
            )
        return suggestions

    def enrich_analysis(
        self,
        resume: ResumeData,
        job: JobDescription,
        analysis: AnalysisResult,
    ) -> AnalysisResult:
        """
        Attach recommendations to an existing analysis result.

        Args:
            resume: Parsed resume.
            job: Job description.
            analysis: Existing analysis.

        Returns:
            Analysis with recommendations populated.
        """
        analysis.recommendations = self.generate(resume, job, analysis.match)
        return analysis
