"""Application settings and environment configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Central configuration for the resume analyzer application."""

    project_root: Path
    data_dir: Path
    skills_db_path: Path
    sample_resumes_dir: Path
    sample_jobs_path: Path
    db_path: Path
    reports_dir: Path
    embedding_model: str
    spacy_model: str
    max_upload_mb: int

    @classmethod
    def from_project_root(cls, root: Path | None = None) -> "Settings":
        """
        Build settings from the project root directory.

        Args:
            root: Optional override for project root. Defaults to resume_analyzer parent.

        Returns:
            Populated Settings instance.
        """
        if root is None:
            root = Path(__file__).resolve().parent.parent
        data = root / "data"
        return cls(
            project_root=root,
            data_dir=data,
            skills_db_path=data / "skills_database.json",
            sample_resumes_dir=data / "sample_resumes",
            sample_jobs_path=data / "sample_job_descriptions.json",
            db_path=root / "resume_analyzer.db",
            reports_dir=root / "generated_reports",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            spacy_model="en_core_web_sm",
            max_upload_mb=10,
        )


def get_settings() -> Settings:
    """Return singleton-style settings for the application."""
    return Settings.from_project_root()
