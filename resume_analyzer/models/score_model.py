"""Data models for scoring and analysis results."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ATSScoreResult:
    """ATS compatibility scoring breakdown."""

    ats_score: float
    grade: str
    breakdown: Dict[str, float] = field(default_factory=dict)
    details: List[str] = field(default_factory=list)


@dataclass
class JobMatchResult:
    """Job matching analysis output."""

    match_score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    semantic_similarity: float = 0.0
    skill_overlap_ratio: float = 0.0
    keyword_baseline_score: float = 0.0


@dataclass
class AnalysisResult:
    """Complete analysis bundle for UI and reports."""

    ats: ATSScoreResult
    match: JobMatchResult
    recommendations: List[str] = field(default_factory=list)
    resume_id: Optional[int] = None
    job_title: Optional[str] = None
