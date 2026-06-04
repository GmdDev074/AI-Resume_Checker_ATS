"""Data models for PDF report generation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from resume_analyzer.models.resume_model import ContactInfo, ResumeData
from resume_analyzer.models.score_model import AnalysisResult


@dataclass
class ReportPayload:
    """All data required to generate a PDF report."""

    candidate: ContactInfo
    resume: ResumeData
    analysis: AnalysisResult
    job_description_snippet: str = ""
    generated_at: datetime = field(default_factory=datetime.now)
    report_title: str = "Resume Analysis Report"

    @property
    def candidate_name(self) -> str:
        """Return display name for candidate."""
        return self.candidate.name or "Candidate"
