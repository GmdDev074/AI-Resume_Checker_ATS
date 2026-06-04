"""
Run thesis evaluation benchmarks and print report.

Usage (from project root):
    python resume_analyzer/scripts/run_evaluation.py
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from resume_analyzer.config.settings import get_settings
from resume_analyzer.services.evaluation.evaluation_service import EvaluationService
from resume_analyzer.services.resume_pipeline import ResumePipeline
from resume_analyzer.utils.file_utils import read_json


def main() -> None:
    """Execute skill extraction benchmark and optional matching comparison."""
    settings = get_settings()
    evaluator = EvaluationService(settings)
    pipeline = ResumePipeline()

    print("=" * 60)
    print("Resume Analyzer — Evaluation Report")
    print("=" * 60)

    skill = evaluator.evaluate_skill_extraction()
    print("\n## Skill Extraction (labeled benchmark)")
    print(f"  Samples:   {skill.samples_evaluated}")
    print(f"  Precision: {skill.precision:.2%}")
    print(f"  Recall:    {skill.recall:.2%}")
    print(f"  F1 Score:  {skill.f1_score:.2%}")
    print(f"  TP/FP/FN:  {skill.true_positives}/{skill.false_positives}/{skill.false_negatives}")

    pairs = []
    resume_path = settings.sample_resumes_dir / "sample_resume_01.txt"
    if resume_path.exists() and settings.sample_jobs_path.exists():
        resume = pipeline.parse_resume(
            resume_path.read_text(encoding="utf-8"),
            file_name="sample_resume_01.txt",
            is_text=True,
        )
        jobs = read_json(settings.sample_jobs_path)
        if jobs:
            job = pipeline.build_job(jobs[0]["description"], title=jobs[0]["title"])
            pairs.append((resume, job))

    report = evaluator.run_full_report(pairs)
    if report.matching_comparisons:
        print("\n## Matching: Semantic (MiniLM) vs Keyword Baseline")
        for i, c in enumerate(report.matching_comparisons, 1):
            print(f"  Pair {i}:")
            print(f"    Hybrid match score:      {c.semantic_match_score}%")
            print(f"    Keyword baseline:        {c.keyword_baseline_score}%")
            print(f"    Semantic similarity:     {c.semantic_similarity_pct}%")
            print(f"    Improvement vs baseline: {c.improvement_over_baseline:+.1f} pts")

    out_path = evaluator.save_report_json(report)
    print(f"\nReport saved to: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
