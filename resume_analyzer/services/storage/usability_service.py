"""Usability study persistence, eligibility, and SUS scoring."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from resume_analyzer.services.storage.database_service import DatabaseService

# Standard System Usability Scale (SUS) — 1 = Strongly disagree, 5 = Strongly agree
SUS_QUESTIONS: List[str] = [
    "I would like to use this system frequently.",
    "I found the system unnecessarily complex.",
    "I thought the system was easy to use.",
    "I think I would need technical support to use this system.",
    "I found the various functions of this system were well integrated.",
    "I thought there was too much inconsistency in this system.",
    "I would imagine that most people would learn to use this system quickly.",
    "I found the system very cumbersome to use.",
    "I felt very confident using the system.",
    "I needed to learn a lot before I could get going with this system.",
]

# Reverse-scored SUS items (even-numbered questions, 1-based index)
SUS_REVERSE_ITEMS = {2, 4, 6, 8, 10}

TASK_LABELS: List[str] = [
    "Upload resume (PDF or sample)",
    "Enter or select a job description",
    "Run analysis and view scores",
    "Review skill gaps and recommendations",
    "Generate and export a PDF report",
]

LIKERT_QUESTIONS: List[str] = [
    "The layout is clear and professional.",
    "I understood the ATS score and breakdown.",
    "Skill gap information was useful.",
    "Recommendations were actionable.",
    "The app responded in acceptable time.",
    "I would recommend this tool to a job seeker.",
]


@dataclass(frozen=True)
class UsabilitySummary:
    """Aggregated usability metrics for thesis reporting."""

    response_count: int
    task_success_rates: Dict[str, float]
    mean_likert: Dict[str, float]
    mean_sus: float
    mean_task_times_sec: Dict[str, Optional[float]]


def compute_sus_score(ratings: List[int]) -> float:
    """
    Compute SUS score (0–100) from ten 1–5 Likert responses.

    Args:
        ratings: Exactly ten integers from 1 to 5.

    Returns:
        SUS score between 0 and 100.
    """
    if len(ratings) != 10:
        raise ValueError("SUS requires exactly 10 ratings")
    total = 0.0
    for idx, rating in enumerate(ratings, start=1):
        if not 1 <= rating <= 5:
            raise ValueError(f"SUS rating must be 1–5, got {rating}")
        if idx in SUS_REVERSE_ITEMS:
            total += 5 - rating
        else:
            total += rating - 1
    return round(total * 2.5, 2)


def sync_report_unlock_from_session() -> None:
    """
    Mark workflow complete when Reports page generated a PDF in this session.

    Requires last_report_path (set only on Generate PDF) plus prior steps.
    """
    if st.session_state.get("report_generated"):
        return
    report_path = st.session_state.get("last_report_path")
    if not report_path or not Path(str(report_path)).is_file():
        return
    if not (
        st.session_state.get("resumes")
        and st.session_state.get("job")
        and st.session_state.get("last_analysis")
    ):
        return
    st.session_state["report_generated"] = True


def is_usability_study_unlocked() -> bool:
    """
    Return True only after the user generated a PDF report on the Reports page.
    """
    sync_report_unlock_from_session()
    return bool(st.session_state.get("report_generated"))


def mark_report_generated() -> None:
    """Record that the PDF report step was completed (call after successful export)."""
    st.session_state["report_generated"] = True


def docx_available() -> bool:
    """Return True if python-docx is installed (required for Word export)."""
    if importlib.util.find_spec("docx") is not None:
        return True
    try:
        import docx  # noqa: F401

        return True
    except ImportError:
        return False


def docx_install_hint() -> str:
    """Return a pip command for the Python interpreter running the app."""
    return f'"{sys.executable}" -m pip install python-docx'


class UsabilityService:
    """Save and summarize usability study responses."""

    def __init__(self, db: Optional[DatabaseService] = None) -> None:
        self._db = db or DatabaseService()

    def save_response(self, payload: Dict[str, Any]) -> int:
        """Persist one usability survey submission."""
        return self._db.save_usability_response(payload)

    def list_responses(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Fetch stored responses newest first."""
        return self._db.get_usability_responses(limit=limit)

    def summarize(self) -> UsabilitySummary:
        """Build aggregate metrics for thesis tables."""
        rows = self.list_responses()
        if not rows:
            return UsabilitySummary(
                response_count=0,
                task_success_rates={},
                mean_likert={},
                mean_sus=0.0,
                mean_task_times_sec={},
            )

        task_keys = [f"task_t{i}_success" for i in range(1, 6)]
        time_keys = [f"task_t{i}_time_sec" for i in range(1, 6)]
        likert_keys = [f"likert_q{i}" for i in range(1, 7)]

        task_success_rates: Dict[str, float] = {}
        for i, key in enumerate(task_keys, start=1):
            successes = sum(1 for r in rows if r.get(key))
            task_success_rates[f"T{i}"] = round(100.0 * successes / len(rows), 1)

        mean_likert: Dict[str, float] = {}
        for i, key in enumerate(likert_keys, start=1):
            values = [r[key] for r in rows if r.get(key) is not None]
            if values:
                mean_likert[f"Q{i}"] = round(sum(values) / len(values), 2)

        sus_values = [r["sus_score"] for r in rows if r.get("sus_score") is not None]
        mean_sus = round(sum(sus_values) / len(sus_values), 2) if sus_values else 0.0

        mean_task_times: Dict[str, Optional[float]] = {}
        for i, key in enumerate(time_keys, start=1):
            times = [r[key] for r in rows if r.get(key) is not None and r[key] > 0]
            mean_task_times[f"T{i}"] = round(sum(times) / len(times), 1) if times else None

        return UsabilitySummary(
            response_count=len(rows),
            task_success_rates=task_success_rates,
            mean_likert=mean_likert,
            mean_sus=mean_sus,
            mean_task_times_sec=mean_task_times,
        )

    def build_export_payload(self) -> Dict[str, Any]:
        """JSON-serializable summary plus raw rows for thesis export."""
        summary = self.summarize()
        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "response_count": summary.response_count,
            "mean_sus": summary.mean_sus,
            "task_success_rates_pct": summary.task_success_rates,
            "mean_likert": summary.mean_likert,
            "mean_task_times_sec": summary.mean_task_times_sec,
            "responses": self.list_responses(),
        }

    def export_json_text(self) -> str:
        """Full export payload as formatted JSON string for download."""
        return json.dumps(self.build_export_payload(), indent=2, ensure_ascii=False)

    @staticmethod
    def _add_table(doc: Any, headers: List[str], rows: List[List[Any]]) -> None:
        """Append a formatted table to a Word document."""
        table = doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.style = "Table Grid"
        for col, header in enumerate(headers):
            table.rows[0].cells[col].text = str(header)
        for r_idx, row_data in enumerate(rows, start=1):
            for c_idx, value in enumerate(row_data):
                table.rows[r_idx].cells[c_idx].text = "" if value is None else str(value)
        doc.add_paragraph("")

    def export_docx_bytes(self) -> bytes:
        """
        Build Microsoft Word (.docx) report for thesis evaluation chapter.

        Raises:
            ImportError: If python-docx is not installed.
        """
        if not docx_available():
            raise ImportError(
                "python-docx is required for Word export. "
                "Run: pip install python-docx"
            )
        from docx import Document

        rows = self.list_responses()
        summary = self.summarize()
        exported_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        doc = Document()
        doc.add_heading("Usability Study Results", level=0)
        doc.add_paragraph(
            "AI-Powered Resume Analyzer and Job Matching System — "
            "evaluation export for academic reporting."
        )
        doc.add_paragraph(f"Exported: {exported_at}")

        doc.add_heading("Summary", level=1)
        self._add_table(
            doc,
            ["Metric", "Value"],
            [
                ["Total responses", summary.response_count],
                ["Mean SUS (0–100)", summary.mean_sus],
            ],
        )

        doc.add_heading("Participants (overview)", level=1)
        participant_rows = [
            [
                r.get("participant_id"),
                r.get("full_name") or "—",
                r.get("email") or "—",
                r.get("phone") or "—",
                r.get("role"),
                f"{sum(1 for i in range(1, 6) if r.get(f'task_t{i}_success'))}/5",
                r.get("sus_score"),
                (r.get("created_at") or "")[:19].replace("T", " "),
            ]
            for r in rows
        ]
        self._add_table(
            doc,
            ["Code", "Name", "Email", "Phone", "Role", "Tasks OK", "SUS", "Submitted (UTC)"],
            participant_rows or [["—"] * 8],
        )

        doc.add_heading("Task checklist — responses by participant", level=1)
        doc.add_paragraph(
            "Each row shows whether the participant completed a workflow task and "
            "how long it took (minutes)."
        )
        task_detail_rows: List[List[Any]] = []
        for r in rows:
            pid = r.get("full_name") or r.get("participant_id")
            for i in range(1, 6):
                time_sec = r.get(f"task_t{i}_time_sec")
                time_label = "—"
                if time_sec is not None and time_sec != "":
                    time_label = f"{round(int(time_sec) / 60, 1)} min"
                task_detail_rows.append(
                    [
                        pid,
                        f"T{i}",
                        TASK_LABELS[i - 1],
                        "Yes" if r.get(f"task_t{i}_success") else "No",
                        time_label,
                    ]
                )
        self._add_table(
            doc,
            ["Participant", "Task", "Question", "Completed", "Time"],
            task_detail_rows or [["—", "—", "—", "—", "—"]],
        )

        doc.add_heading("Experience survey — responses by participant", level=1)
        doc.add_paragraph("Scale: 1 = Strongly disagree, 5 = Strongly agree.")
        likert_detail_rows: List[List[Any]] = []
        for r in rows:
            pid = r.get("full_name") or r.get("participant_id")
            for i in range(1, len(LIKERT_QUESTIONS) + 1):
                likert_detail_rows.append(
                    [
                        pid,
                        f"Q{i}",
                        LIKERT_QUESTIONS[i - 1],
                        r.get(f"likert_q{i}", "—"),
                    ]
                )
        self._add_table(
            doc,
            ["Participant", "Item", "Question", "Rating (1–5)"],
            likert_detail_rows or [["—", "—", "—", "—"]],
        )

        doc.add_heading("SUS — responses by participant", level=1)
        doc.add_paragraph("Scale: 1 = Strongly disagree, 5 = Strongly agree.")
        sus_detail_rows: List[List[Any]] = []
        for r in rows:
            pid = r.get("full_name") or r.get("participant_id")
            for i in range(1, len(SUS_QUESTIONS) + 1):
                sus_detail_rows.append(
                    [
                        pid,
                        f"S{i}",
                        SUS_QUESTIONS[i - 1],
                        r.get(f"sus_q{i}", "—"),
                    ]
                )
        self._add_table(
            doc,
            ["Participant", "Item", "Question", "Rating (1–5)"],
            sus_detail_rows or [["—", "—", "—", "—"]],
        )

        doc.add_heading("Task success rates (aggregate)", level=1)
        doc.add_paragraph("Scale: 0% (none completed) to 100% (all participants).")
        task_rows = [
            [tid, TASK_LABELS[int(tid.replace("T", "")) - 1], f"{rate}%"]
            for tid, rate in sorted(summary.task_success_rates.items())
        ]
        self._add_table(
            doc,
            ["Task", "Question", "Success rate"],
            task_rows or [["—", "—", "—"]],
        )

        doc.add_heading("Experience survey — mean scores (aggregate)", level=1)
        doc.add_paragraph("Scale: Min 1 (Strongly disagree) — Max 5 (Strongly agree).")
        likert_rows = []
        for q_id in sorted(summary.mean_likert.keys()):
            q_num = int(q_id.replace("Q", "")) - 1
            label = LIKERT_QUESTIONS[q_num] if q_num < len(LIKERT_QUESTIONS) else q_id
            likert_rows.append([q_id, label, summary.mean_likert[q_id]])
        self._add_table(doc, ["Item", "Question", "Mean (1–5)"], likert_rows or [["—", "—", "—"]])

        doc.add_heading("SUS scores by participant (aggregate)", level=1)
        doc.add_paragraph("System Usability Scale: 0–100 (higher is better).")
        sus_rows = [
            [r.get("full_name") or r.get("participant_id"), r.get("sus_score")]
            for r in rows
        ]
        self._add_table(doc, ["Participant", "SUS score"], sus_rows or [["—", "—"]])

        doc.add_heading("Optional comments", level=1)
        if rows:
            for r in rows:
                comment = (r.get("comments") or "").strip()
                if comment:
                    label = r.get("full_name") or r.get("participant_id")
                    doc.add_paragraph(f"{label}: {comment}")
        else:
            doc.add_paragraph("No comments recorded.")

        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    def thesis_summary_rows(self) -> List[Dict[str, Any]]:
        """Compact per-participant rows for display in the app."""
        rows = self.list_responses()
        result = []
        for row in rows:
            tasks_ok = sum(1 for i in range(1, 6) if row.get(f"task_t{i}_success"))
            result.append(
                {
                    "Code": row.get("participant_id"),
                    "Name": row.get("full_name") or "—",
                    "Email": row.get("email") or "—",
                    "Phone": row.get("phone") or "—",
                    "Role": row.get("role"),
                    "Tasks OK": f"{tasks_ok}/5",
                    "SUS": row.get("sus_score"),
                    "Submitted": (row.get("created_at") or "")[:19].replace("T", " "),
                }
            )
        return result
