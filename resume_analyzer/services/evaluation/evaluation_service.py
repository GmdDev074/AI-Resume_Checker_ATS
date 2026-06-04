"""Evaluation metrics for thesis: skill extraction and matching baselines."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from resume_analyzer.config.settings import Settings, get_settings
from resume_analyzer.models.job_model import JobDescription
from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.services.extraction.skill_extractor import SkillExtractor
from resume_analyzer.services.matching.baseline_matcher import BaselineMatcher
from resume_analyzer.services.matching.embedding_service import EmbeddingService
from resume_analyzer.services.matching.job_matching_service import JobMatchingService
from resume_analyzer.services.matching.similarity_service import SimilarityService
from resume_analyzer.utils.file_utils import read_json


@dataclass
class SkillExtractionMetrics:
    """Precision, recall, F1 for skill extraction benchmark."""

    precision: float
    recall: float
    f1_score: float
    samples_evaluated: int
    true_positives: int
    false_positives: int
    false_negatives: int


@dataclass
class MatchingComparison:
    """Semantic vs keyword baseline on one resume–job pair."""

    semantic_match_score: float
    keyword_baseline_score: float
    semantic_similarity_pct: float
    improvement_over_baseline: float


@dataclass
class EvaluationReport:
    """Full evaluation report for thesis documentation."""

    skill_metrics: SkillExtractionMetrics
    matching_comparisons: List[MatchingComparison] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class EvaluationService:
    """Run benchmarks documented in the project methodology."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize evaluation service.

        Args:
            settings: Application settings.
        """
        self._settings = settings or get_settings()
        self._extractor = SkillExtractor(self._settings)
        self._baseline = BaselineMatcher()
        self._matcher = JobMatchingService()

    def _default_labels_path(self) -> Path:
        """
        Prefer merged 50+ Kaggle-style set; fall back to smaller legacy file.

        Returns:
            Path to labeled resume JSON.
        """
        eval_dir = self._settings.data_dir / "evaluation"
        for name in (
            "all_labeled_resumes.json",
            "kaggle_labeled_resumes.json",
            "skill_extraction_labels.json",
        ):
            candidate = eval_dir / name
            if candidate.exists():
                return candidate
        return eval_dir / "skill_extraction_labels.json"

    def evaluate_skill_extraction(
        self,
        labels_path: Optional[Path] = None,
    ) -> SkillExtractionMetrics:
        """
        Measure skill extraction against labeled samples.

        Args:
            labels_path: Path to JSON label file.

        Returns:
            Aggregated precision, recall, and F1.
        """
        path = labels_path or self._default_labels_path()
        samples = read_json(path)
        tp = fp = fn = 0

        for sample in samples:
            expected = {s.lower() for s in sample["expected_skills"]}
            predicted = {s.lower() for s in self._extractor.extract(sample["text"])}
            tp += len(expected & predicted)
            fp += len(predicted - expected)
            fn += len(expected - predicted)

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall)
            else 0.0
        )

        return SkillExtractionMetrics(
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            samples_evaluated=len(samples),
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
        )

    def compare_matching_methods(
        self,
        resume: ResumeData,
        job: JobDescription,
    ) -> MatchingComparison:
        """
        Compare hybrid semantic match vs keyword-only baseline.

        Args:
            resume: Parsed resume.
            job: Job description.

        Returns:
            Side-by-side scores for thesis tables.
        """
        result = self._matcher.match(resume, job)
        improvement = result.match_score - result.keyword_baseline_score
        return MatchingComparison(
            semantic_match_score=result.match_score,
            keyword_baseline_score=result.keyword_baseline_score,
            semantic_similarity_pct=result.semantic_similarity,
            improvement_over_baseline=round(improvement, 1),
        )

    def run_full_report(
        self,
        resume_job_pairs: Optional[List[tuple[ResumeData, JobDescription]]] = None,
    ) -> EvaluationReport:
        """
        Generate complete evaluation report.

        Args:
            resume_job_pairs: Optional pairs for matching comparison.

        Returns:
            EvaluationReport dataclass.
        """
        skill_metrics = self.evaluate_skill_extraction()
        comparisons: List[MatchingComparison] = []
        if resume_job_pairs:
            for resume, job in resume_job_pairs:
                comparisons.append(self.compare_matching_methods(resume, job))

        label_path = self._default_labels_path()
        notes = [
            "Semantic matching uses Sentence Transformers (all-MiniLM-L6-v2) + scikit-learn cosine similarity.",
            "Keyword baseline uses exact skill overlap only (no embeddings).",
            f"Skill labels dataset: {label_path.name} ({skill_metrics.samples_evaluated} samples).",
            "Kaggle CSV import: scripts/import_kaggle_csv.py",
        ]

        return EvaluationReport(
            skill_metrics=skill_metrics,
            matching_comparisons=comparisons,
            notes=notes,
        )

    def save_report_json(
        self,
        report: EvaluationReport,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Save report as JSON for thesis appendix.

        Args:
            report: Evaluation report.
            output_path: Target file path.

        Returns:
            Path written.
        """
        out = output_path or (
            self._settings.project_root / "data" / "evaluation" / "latest_report.json"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        payload: Dict[str, Any] = {
            "skill_extraction": {
                "precision": report.skill_metrics.precision,
                "recall": report.skill_metrics.recall,
                "f1_score": report.skill_metrics.f1_score,
                "samples": report.skill_metrics.samples_evaluated,
                "tp": report.skill_metrics.true_positives,
                "fp": report.skill_metrics.false_positives,
                "fn": report.skill_metrics.false_negatives,
            },
            "matching_comparisons": [
                {
                    "semantic_match_score": c.semantic_match_score,
                    "keyword_baseline_score": c.keyword_baseline_score,
                    "semantic_similarity_pct": c.semantic_similarity_pct,
                    "improvement_over_baseline": c.improvement_over_baseline,
                }
                for c in report.matching_comparisons
            ],
            "notes": report.notes,
        }
        with out.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        return out
