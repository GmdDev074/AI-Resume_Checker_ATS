"""Tests for job matching services."""

import numpy as np
import pytest

from resume_analyzer.models.job_model import JobDescription
from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.services.matching.similarity_service import SimilarityService
from resume_analyzer.services.matching.job_matching_service import JobMatchingService


class TestSimilarityService:
    """Cosine similarity tests."""

    def test_identical_vectors_score_one(self) -> None:
        """Identical vectors have similarity 1."""
        vec = np.array([1.0, 0.0, 0.0])
        score = SimilarityService().cosine_similarity(vec, vec)
        assert score == pytest.approx(1.0, abs=0.01)


class TestJobMatchingService:
    """Job matching tests."""

    def test_missing_skills_detected(self) -> None:
        """Skills in job but not resume should be missing."""
        resume = ResumeData(
            raw_text="Python developer",
            skills=["Python", "Git"],
        )
        job = JobDescription(
            raw_text="Need Python, Docker, Kubernetes",
            required_skills=["Python", "Docker", "Kubernetes"],
        )
        result = JobMatchingService().match(resume, job)
        assert "Python" in result.matched_skills or any(
            s.lower() == "python" for s in result.matched_skills
        )
        assert len(result.missing_skills) >= 1
