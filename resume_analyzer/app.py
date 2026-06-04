"""
AI-Powered Resume Analyzer and Job Matching System
Streamlit application entry point.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from resume_analyzer.config.settings import get_settings
from resume_analyzer.services.resume_pipeline import ResumePipeline
from resume_analyzer.services.storage.database_service import DatabaseService
from resume_analyzer.ui.components.layout import (
    render_status_pills,
    render_workflow_sidebar,
)
from resume_analyzer.ui.icons import material
from resume_analyzer.ui.pages.analysis_page import render_analysis_page
from resume_analyzer.ui.pages.dashboard import render_dashboard
from resume_analyzer.ui.pages.reports_page import render_reports_page
from resume_analyzer.ui.pages.resume_upload import render_resume_upload
from resume_analyzer.ui.theme import apply_theme
from resume_analyzer.utils.logger import configure_root_logger

NAV_OPTIONS = [
    (material("dashboard") + " Dashboard", "Dashboard"),
    (material("upload") + " Upload Resume", "Upload Resume"),
    (material("analysis") + " Analysis", "Analysis"),
    (material("reports") + " Reports", "Reports"),
]


def init_session_state() -> None:
    """Initialize Streamlit session state keys."""
    defaults = {
        "resumes": None,
        "job": None,
        "job_text": "",
        "last_analysis": None,
        "last_resume": None,
        "last_analysis_id": None,
        "last_report_path": None,
        "nav_page": "Dashboard",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_resource
def get_pipeline() -> ResumePipeline:
    """Cached resume pipeline singleton."""
    return ResumePipeline()


@st.cache_resource
def get_database() -> DatabaseService:
    """Cached database service singleton."""
    return DatabaseService()


def main() -> None:
    """Run Streamlit multi-page application."""
    configure_root_logger()
    settings = get_settings()
    settings.reports_dir.mkdir(parents=True, exist_ok=True)

    st.set_page_config(
        page_title="Resume Analyzer | AI Job Matching",
        page_icon=":material/work_history:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    apply_theme()

    labels = [label for label, _ in NAV_OPTIONS]
    key_to_page = {label: page for label, page in NAV_OPTIONS}

    default_idx = next(
        (i for i, (_, p) in enumerate(NAV_OPTIONS) if p == st.session_state["nav_page"]),
        0,
    )

    st.sidebar.markdown("---")
    selected_label = st.sidebar.radio(
        "Navigation",
        options=labels,
        index=default_idx,
        label_visibility="collapsed",
    )
    page = key_to_page[selected_label]
    st.session_state["nav_page"] = page

    render_status_pills(
        has_resume=bool(st.session_state.get("resumes")),
        has_job=bool(st.session_state.get("job")),
        has_analysis=bool(st.session_state.get("last_analysis")),
    )
    st.sidebar.markdown("---")
    render_workflow_sidebar()

    pipeline = get_pipeline()
    db = get_database()

    if page == "Dashboard":
        render_dashboard(db)
    elif page == "Upload Resume":
        render_resume_upload(pipeline, db)
    elif page == "Analysis":
        render_analysis_page(pipeline, db)
    elif page == "Reports":
        render_reports_page(pipeline, db)


if __name__ == "__main__":
    main()
