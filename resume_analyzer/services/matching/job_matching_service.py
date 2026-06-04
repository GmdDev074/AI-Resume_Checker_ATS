"""Job matching orchestration service."""

from typing import List, Optional, Set

from resume_analyzer.models.job_model import JobDescription
from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.models.score_model import JobMatchResult
from resume_analyzer.services.extraction.skill_extractor import SkillExtractor
from resume_analyzer.services.matching.baseline_matcher import BaselineMatcher
from resume_analyzer.services.matching.embedding_service import EmbeddingService
from resume_analyzer.services.matching.similarity_service import SimilarityService


class JobMatchingService:
    """Compare resume against job description and produce match metrics."""

    def __init__(
        self,
        skill_extractor: Optional[SkillExtractor] = None,
        embedding_service: Optional[EmbeddingService] = None,
        similarity_service: Optional[SimilarityService] = None,
    ) -> None:
        """
        Initialize job matcher with dependencies.

        Args:
            skill_extractor: Skill detection service.
            embedding_service: Embedding generator.
            similarity_service: Similarity calculator.
        """
        self._skills = skill_extractor or SkillExtractor()
        self._embeddings = embedding_service or EmbeddingService()
        self._similarity = similarity_service or SimilarityService()
        self._baseline = BaselineMatcher()

    def match(self, resume: ResumeData, job: JobDescription) -> JobMatchResult:
        """
        Full job match analysis.

        Args:
            resume: Parsed resume.
            job: Job description.

        Returns:
            JobMatchResult with scores and skill lists.
        """
        if not job.required_skills:
            job.required_skills = self._skills.extract_from_job(job.raw_text)
        resume_skills = {s.lower(): s for s in resume.skills}
        job_skills = {s.lower(): s for s in job.required_skills}

        matched, missing = self._compare_skills(resume_skills, job_skills)
        overlap_ratio = len(matched) / len(job_skills) if job_skills else 0.0

        resume_vec = self._embeddings.encode(resume.raw_text[:8000])
        job_vec = self._embeddings.encode(job.raw_text[:8000])
        semantic = self._similarity.cosine_similarity(resume_vec, job_vec)

        skill_score = overlap_ratio * 100
        combined = 0.6 * skill_score + 0.4 * (semantic * 100)
        match_score = round(min(100.0, combined), 1)

        baseline_score = self._baseline.skill_overlap_score(
            resume.skills, job.required_skills
        )

        return JobMatchResult(
            match_score=match_score,
            matched_skills=sorted(matched, key=str.lower),
            missing_skills=sorted(missing, key=str.lower),
            semantic_similarity=round(semantic * 100, 1),
            skill_overlap_ratio=round(overlap_ratio, 3),
            keyword_baseline_score=baseline_score,
        )

    def _compare_skills(
        self,
        resume_skills: dict[str, str],
        job_skills: dict[str, str],
    ) -> tuple[List[str], List[str]]:
        """Find matched and missing skills."""
        matched: List[str] = []
        missing: List[str] = []
        for key, job_skill in job_skills.items():
            if key in resume_skills:
                matched.append(resume_skills[key])
            else:
                missing.append(job_skill)
        return matched, missing

    def rank_candidates(
        self,
        resumes: List[ResumeData],
        job: JobDescription,
    ) -> List[tuple[ResumeData, JobMatchResult]]:
        """
        Rank multiple resumes for a job.

        Args:
            resumes: List of resumes.
            job: Target job.

        Returns:
            Sorted list of (resume, match_result) descending by score.
        """
        results = [(r, self.match(r, job)) for r in resumes]
        results.sort(key=lambda x: x[1].match_score, reverse=True)
        return results
