"""Keyword-only baseline matcher for thesis evaluation comparison."""


class BaselineMatcher:
    """
    Baseline job match using exact skill overlap only (no semantic embeddings).

    Mirrors traditional ATS keyword-matching approaches cited in literature.
    """

    def skill_overlap_score(
        self,
        resume_skills: list[str],
        job_skills: list[str],
    ) -> float:
        """
        Compute match percentage from skill set intersection.

        Args:
            resume_skills: Skills detected in resume.
            job_skills: Skills required in job description.

        Returns:
            Score 0–100 based on fraction of job skills found in resume.
        """
        if not job_skills:
            return 0.0
        resume_set = {s.lower().strip() for s in resume_skills}
        job_set = {s.lower().strip() for s in job_skills}
        if not job_set:
            return 0.0
        matched = len(resume_set & job_set)
        return round((matched / len(job_set)) * 100, 1)

    def keyword_density_score(self, resume_text: str, job_text: str) -> float:
        """
        Simple keyword density baseline: share of job tokens found in resume.

        Args:
            resume_text: Full resume text.
            job_text: Full job description text.

        Returns:
            Score 0–100.
        """
        def tokens(text: str) -> set[str]:
            return {t.lower() for t in text.split() if len(t) > 2 and t.isalpha()}

        job_tokens = tokens(job_text)
        resume_tokens = tokens(resume_text)
        if not job_tokens:
            return 0.0
        overlap = len(job_tokens & resume_tokens) / len(job_tokens)
        return round(overlap * 100, 1)
