"""Orchestrates resume parsing, extraction, and analysis workflow."""

from typing import List, Optional, Union

from resume_analyzer.models.job_model import JobDescription
from resume_analyzer.models.report_model import ReportPayload
from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.models.score_model import AnalysisResult
from resume_analyzer.services.ats.ats_scoring_service import ATSScoringService
from resume_analyzer.services.extraction.contact_extractor import ContactExtractor
from resume_analyzer.services.extraction.education_extractor import EducationExtractor
from resume_analyzer.services.extraction.experience_extractor import ExperienceExtractor
from resume_analyzer.services.extraction.skill_extractor import SkillExtractor
from resume_analyzer.services.matching.job_matching_service import JobMatchingService
from resume_analyzer.services.pdf.pdf_parser import PDFParser
from resume_analyzer.services.recommendation.recommendation_service import RecommendationService
from resume_analyzer.services.report.pdf_report_generator import PDFReportGenerator


class ResumePipeline:
    """End-to-end resume processing and analysis."""

    def __init__(self) -> None:
        """Wire all services for the analysis workflow."""
        self.pdf_parser = PDFParser()
        self.contact_extractor = ContactExtractor()
        self.skill_extractor = SkillExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.job_matcher = JobMatchingService()
        self.ats_scorer = ATSScoringService(self.job_matcher)
        self.recommender = RecommendationService()
        self.report_generator = PDFReportGenerator()

    def parse_resume(
        self,
        source: Union[bytes, str],
        file_name: Optional[str] = None,
        is_text: bool = False,
    ) -> ResumeData:
        """
        Parse resume from PDF bytes or plain text.

        Args:
            source: PDF bytes or text string.
            file_name: Original filename.
            is_text: True if source is already text.

        Returns:
            Structured ResumeData.
        """
        if is_text:
            text = str(source)
        else:
            text = self.pdf_parser.extract_from_upload(bytes(source))

        contact = self.contact_extractor.extract(text)
        skills = self.skill_extractor.extract(text)
        education = self.education_extractor.extract(text)
        experience, total_years = self.experience_extractor.extract(text)

        return ResumeData(
            raw_text=text,
            contact=contact,
            skills=skills,
            education=education,
            experience=experience,
            total_experience_years=total_years,
            file_name=file_name,
        )

    def build_job(self, job_text: str, title: Optional[str] = None) -> JobDescription:
        """
        Build job description model from pasted text.

        Args:
            job_text: Raw job description.
            title: Optional job title.

        Returns:
            JobDescription with extracted skills.
        """
        skills = self.skill_extractor.extract_from_job(job_text)
        return JobDescription(
            raw_text=job_text,
            title=title or "Target Position",
            required_skills=skills,
        )

    def analyze(self, resume: ResumeData, job: JobDescription) -> AnalysisResult:
        """
        Run full ATS and job match analysis.

        Args:
            resume: Parsed resume.
            job: Job description.

        Returns:
            Complete AnalysisResult.
        """
        match = self.job_matcher.match(resume, job)
        ats = self.ats_scorer.calculate(resume, job)
        result = AnalysisResult(
            ats=ats,
            match=match,
            resume_id=resume.resume_id,
            job_title=job.title,
        )
        self.recommender.enrich_analysis(resume, job, result)
        return result

    def generate_report(
        self,
        resume: ResumeData,
        job: JobDescription,
        analysis: AnalysisResult,
    ):
        """
        Generate PDF report file.

        Args:
            resume: Parsed resume.
            job: Job description.
            analysis: Analysis results.

        Returns:
            Path to PDF report.
        """
        payload = ReportPayload(
            candidate=resume.contact,
            resume=resume,
            analysis=analysis,
            job_description_snippet=job.raw_text[:500],
        )
        return self.report_generator.generate(payload)

    def compare_resumes(
        self,
        resumes: List[ResumeData],
        job: JobDescription,
    ) -> List[tuple[ResumeData, AnalysisResult]]:
        """
        Analyze and rank multiple resumes.

        Args:
            resumes: List of resumes.
            job: Target job.

        Returns:
            Sorted list by match score.
        """
        results = [(r, self.analyze(r, job)) for r in resumes]
        results.sort(key=lambda x: x[1].match.match_score, reverse=True)
        return results
