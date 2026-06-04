"""Tests for evaluation and baseline matching."""

from resume_analyzer.services.evaluation.evaluation_service import EvaluationService
from resume_analyzer.services.matching.baseline_matcher import BaselineMatcher


class TestBaselineMatcher:
    """Keyword baseline tests."""

    def test_full_overlap(self) -> None:
        """All job skills present gives 100%."""
        score = BaselineMatcher().skill_overlap_score(
            ["Python", "Git"], ["Python", "Git"]
        )
        assert score == 100.0

    def test_partial_overlap(self) -> None:
        """Half of job skills gives 50%."""
        score = BaselineMatcher().skill_overlap_score(
            ["Python"], ["Python", "Docker"]
        )
        assert score == 50.0


class TestEvaluationService:
    """Skill extraction benchmark tests."""

    def test_skill_metrics_on_labels(self) -> None:
        """F1 should be high on curated label set."""
        metrics = EvaluationService().evaluate_skill_extraction()
        assert metrics.samples_evaluated >= 45
        assert metrics.f1_score >= 0.5
