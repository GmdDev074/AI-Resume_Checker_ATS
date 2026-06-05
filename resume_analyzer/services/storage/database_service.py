"""SQLite persistence for users, analysis history, and reports."""

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from resume_analyzer.config.settings import Settings, get_settings
from resume_analyzer.models.score_model import AnalysisResult
from resume_analyzer.utils.file_utils import ensure_dir
from resume_analyzer.utils.logger import get_logger

logger = get_logger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    resume_name TEXT NOT NULL,
    job_title TEXT,
    resume_text TEXT,
    job_description TEXT,
    ats_score REAL,
    match_score REAL,
    skills_json TEXT,
    missing_skills_json TEXT,
    analysis_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analysis_history(id)
);

CREATE TABLE IF NOT EXISTS usability_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    role TEXT,
    task_t1_success INTEGER NOT NULL DEFAULT 0,
    task_t2_success INTEGER NOT NULL DEFAULT 0,
    task_t3_success INTEGER NOT NULL DEFAULT 0,
    task_t4_success INTEGER NOT NULL DEFAULT 0,
    task_t5_success INTEGER NOT NULL DEFAULT 0,
    task_t1_time_sec INTEGER,
    task_t2_time_sec INTEGER,
    task_t3_time_sec INTEGER,
    task_t4_time_sec INTEGER,
    task_t5_time_sec INTEGER,
    likert_q1 INTEGER,
    likert_q2 INTEGER,
    likert_q3 INTEGER,
    likert_q4 INTEGER,
    likert_q5 INTEGER,
    likert_q6 INTEGER,
    sus_q1 INTEGER,
    sus_q2 INTEGER,
    sus_q3 INTEGER,
    sus_q4 INTEGER,
    sus_q5 INTEGER,
    sus_q6 INTEGER,
    sus_q7 INTEGER,
    sus_q8 INTEGER,
    sus_q9 INTEGER,
    sus_q10 INTEGER,
    sus_score REAL,
    comments TEXT,
    analysis_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analysis_history(id)
);
"""


class DatabaseService:
    """SQLite database operations."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize database service.

        Args:
            settings: Application settings.
        """
        self._settings = settings or get_settings()
        self._db_path = self._settings.db_path
        ensure_dir(self._db_path.parent)
        self.initialize()

    def initialize(self) -> None:
        """Create tables if they do not exist."""
        with self._connection() as conn:
            conn.executescript(SCHEMA_SQL)
            self._migrate_usability_columns(conn)
            conn.commit()
        logger.info("Database initialized at %s", self._db_path)

    @staticmethod
    def _migrate_usability_columns(conn: sqlite3.Connection) -> None:
        """Add newer usability columns to existing databases."""
        existing = {
            row[1]
            for row in conn.execute("PRAGMA table_info(usability_responses)").fetchall()
        }
        for column, sql_type in (
            ("full_name", "TEXT"),
            ("email", "TEXT"),
            ("phone", "TEXT"),
        ):
            if column not in existing:
                conn.execute(
                    f"ALTER TABLE usability_responses ADD COLUMN {column} {sql_type}"
                )

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Yield database connection with row factory."""
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_user(self, name: str, email: str) -> int:
        """
        Insert or fetch user by email.

        Args:
            name: User display name.
            email: User email.

        Returns:
            User id.
        """
        now = datetime.utcnow().isoformat()
        with self._connection() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if row:
                return int(row["id"])
            cursor = conn.execute(
                "INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)",
                (name, email, now),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def save_analysis(
        self,
        resume_name: str,
        job_title: str,
        resume_text: str,
        job_description: str,
        analysis: AnalysisResult,
        skills: List[str],
        user_id: Optional[int] = None,
    ) -> int:
        """
        Persist analysis result.

        Args:
            resume_name: Uploaded file name.
            job_title: Job title label.
            resume_text: Extracted resume text.
            job_description: Job description text.
            analysis: Full analysis result.
            skills: Resume skills list.
            user_id: Optional user foreign key.

        Returns:
            Analysis history id.
        """
        now = datetime.utcnow().isoformat()
        payload = {
            "ats": asdict(analysis.ats),
            "match": asdict(analysis.match),
            "recommendations": analysis.recommendations,
        }
        with self._connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO analysis_history (
                    user_id, resume_name, job_title, resume_text, job_description,
                    ats_score, match_score, skills_json, missing_skills_json,
                    analysis_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    resume_name,
                    job_title,
                    resume_text[:50000],
                    job_description[:50000],
                    analysis.ats.ats_score,
                    analysis.match.match_score,
                    json.dumps(skills),
                    json.dumps(analysis.match.missing_skills),
                    json.dumps(payload),
                    now,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def save_report(self, analysis_id: int, file_path: Path) -> int:
        """
        Record generated report path.

        Args:
            analysis_id: Linked analysis id.
            file_path: PDF file path.

        Returns:
            Report record id.
        """
        now = datetime.utcnow().isoformat()
        with self._connection() as conn:
            cursor = conn.execute(
                "INSERT INTO reports (analysis_id, file_path, created_at) VALUES (?, ?, ?)",
                (analysis_id, str(file_path), now),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_analysis_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch recent analysis records.

        Args:
            limit: Max records.

        Returns:
            List of analysis dicts.
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT id, resume_name, job_title, ats_score, match_score, created_at
                FROM analysis_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch single analysis record.

        Args:
            analysis_id: Record id.

        Returns:
            Analysis dict or None.
        """
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM analysis_history WHERE id = ?", (analysis_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch recent report records.

        Args:
            limit: Max records.

        Returns:
            List of report dicts.
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT r.id, r.analysis_id, r.file_path, r.created_at,
                       a.resume_name, a.ats_score, a.match_score
                FROM reports r
                JOIN analysis_history a ON a.id = r.analysis_id
                ORDER BY r.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_usability_response(self, payload: Dict[str, Any]) -> int:
        """
        Insert a usability study survey response.

        Args:
            payload: Field dictionary from UsabilityService / survey form.

        Returns:
            New record id.
        """
        now = datetime.utcnow().isoformat()
        columns = [
            "participant_id",
            "full_name",
            "email",
            "phone",
            "role",
            "task_t1_success",
            "task_t2_success",
            "task_t3_success",
            "task_t4_success",
            "task_t5_success",
            "task_t1_time_sec",
            "task_t2_time_sec",
            "task_t3_time_sec",
            "task_t4_time_sec",
            "task_t5_time_sec",
            "likert_q1",
            "likert_q2",
            "likert_q3",
            "likert_q4",
            "likert_q5",
            "likert_q6",
            "sus_q1",
            "sus_q2",
            "sus_q3",
            "sus_q4",
            "sus_q5",
            "sus_q6",
            "sus_q7",
            "sus_q8",
            "sus_q9",
            "sus_q10",
            "sus_score",
            "comments",
            "analysis_id",
            "created_at",
        ]
        values = [payload.get(col) for col in columns[:-1]] + [now]
        placeholders = ", ".join("?" for _ in columns)
        col_sql = ", ".join(columns)
        with self._connection() as conn:
            cursor = conn.execute(
                f"INSERT INTO usability_responses ({col_sql}) VALUES ({placeholders})",
                values,
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_usability_responses(self, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Fetch usability survey responses.

        Args:
            limit: Maximum rows.

        Returns:
            List of response dicts.
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM usability_responses
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def participant_id_exists(self, participant_id: str) -> bool:
        """Return True if participant_id was already used."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM usability_responses WHERE participant_id = ? LIMIT 1",
                (participant_id.strip(),),
            ).fetchone()
        return row is not None

    def usability_email_exists(self, email: str) -> bool:
        """Return True if this email already submitted a usability response."""
        normalized = (email or "").strip().lower()
        if not normalized:
            return False
        with self._connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM usability_responses WHERE LOWER(email) = ? LIMIT 1",
                (normalized,),
            ).fetchone()
        return row is not None

    def next_participant_code(self) -> str:
        """Generate the next study code (P01, P02, …)."""
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT participant_id FROM usability_responses"
            ).fetchall()
        numbers = []
        for row in rows:
            pid = str(row[0] or "")
            if pid.startswith("P") and pid[1:].isdigit():
                numbers.append(int(pid[1:]))
        return f"P{max(numbers, default=0) + 1:02d}"
