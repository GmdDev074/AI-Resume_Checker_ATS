"""Dashboard overview page."""

import streamlit as st

from resume_analyzer.services.extraction.skill_extractor import SkillExtractor
from resume_analyzer.services.storage.database_service import DatabaseService
from resume_analyzer.ui.components.charts import render_skill_gap_chart
from resume_analyzer.ui.components.data_table import render_data_table
from resume_analyzer.ui.components.layout import (
    render_empty_state,
    render_page_header,
    render_section,
    vertical_spacer,
)


def render_dashboard(db: DatabaseService) -> None:
    """
    Render main dashboard with history and stats.

    Args:
        db: Database service instance.
    """
    render_page_header(
        "Dashboard",
        "Overview of analyses, aggregate scores, and skill database search.",
        "space_dashboard",
    )
    vertical_spacer(16)

    history = db.get_analysis_history(limit=15)

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1:
        st.metric("Total analyses", len(history))
    with m2:
        avg_ats = sum(h["ats_score"] or 0 for h in history) / len(history) if history else 0
        st.metric("Average ATS", f"{avg_ats:.1f}")
    with m3:
        avg_match = sum(h["match_score"] or 0 for h in history) / len(history) if history else 0
        st.metric("Average match", f"{avg_match:.1f}%")
    with m4:
        ready = "Ready" if st.session_state.get("last_analysis") else "Pending"
        st.metric("Report status", ready)

    vertical_spacer(28)
    render_section("Recent analysis history")
    if history:
        render_data_table(
            [
                {
                    "Resume": h["resume_name"],
                    "Position": h["job_title"] or "—",
                    "ATS": round(h["ats_score"] or 0, 1),
                    "Match (%)": round(h["match_score"] or 0, 1),
                    "Date": (h["created_at"] or "—")[:19].replace("T", " "),
                }
                for h in history
            ],
            height=min(42 + len(history) * 36, 320),
        )
    else:
        render_empty_state(
            "No analysis records found. Results are saved automatically after each run.",
            "Upload a resume and run analysis from the Upload and Analysis pages.",
        )

    vertical_spacer(32)
    left, right = st.columns([1, 1], gap="large")

    with left:
        render_section("Skill database", "Search technical skills used for matching")
        skill_search = st.text_input(
            "Search skills",
            placeholder="e.g. Python, Docker, React",
            label_visibility="collapsed",
        )
        extractor = SkillExtractor()
        results = extractor.search_skills(skill_search or "", limit=18)
        if results:
            chips = "".join(
                f'<span class="skill-chip skill-chip-match">{s}</span>' for s in results
            )
            st.markdown(
                f'<div class="skill-tags-wrap">{chips}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("Enter a keyword to browse the skills catalog.")

    with right:
        if st.session_state.get("last_analysis"):
            render_section("Latest skill gap")
            analysis = st.session_state["last_analysis"]
            render_skill_gap_chart(
                analysis.match.matched_skills,
                analysis.match.missing_skills,
            )
        else:
            render_section("Latest skill gap")
            st.caption("Run an analysis to view the skill gap chart here.")
