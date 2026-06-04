"""Analysis results page."""

import streamlit as st

from resume_analyzer.models.score_model import AnalysisResult
from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.services.resume_pipeline import ResumePipeline
from resume_analyzer.services.storage.database_service import DatabaseService
from resume_analyzer.ui.components.charts import (
    render_ats_breakdown_matplotlib,
    render_match_gauge,
    render_skill_distribution,
    render_skill_gap_chart,
)
from resume_analyzer.ui.components.data_table import render_data_table
from resume_analyzer.ui.components.layout import (
    render_empty_state,
    render_page_header,
    render_section,
    vertical_spacer,
)
from resume_analyzer.ui.components.metrics import render_resume_metrics
from resume_analyzer.ui.components.score_card import render_score_cards
from resume_analyzer.ui.components.skill_card import render_skill_lists
from resume_analyzer.ui.icons import material, svg_icon


def render_analysis_page(pipeline: ResumePipeline, db: DatabaseService) -> None:
    """
    Run and display full resume analysis.

    Args:
        pipeline: Resume pipeline.
        db: Database service.
    """
    render_page_header(
        "Analysis results",
        "ATS compatibility scoring, semantic job match, skill gap, and recommendations.",
        "analytics",
    )

    if not st.session_state.get("resumes") or not st.session_state.get("job"):
        render_empty_state(
            "Required inputs are missing.",
            "Complete document upload on the Upload page before running analysis.",
        )
        return

    resumes = st.session_state["resumes"]
    job = st.session_state["job"]

    st.markdown(
        f"""
        <div class="info-banner">
            <strong>Target role:</strong> {job.title or "Position"}
            &nbsp;&middot;&nbsp;
            <strong>Documents loaded:</strong> {len(resumes)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    run_col, _ = st.columns([1, 3])
    with run_col:
        if st.button(
            "Run analysis",
            type="primary",
            use_container_width=True,
            icon=material("play"),
        ):
            if len(resumes) > 1:
                ranked = pipeline.compare_resumes(resumes, job)
                st.session_state["ranked_results"] = ranked
                resume, analysis = ranked[0]
            else:
                resume = resumes[0]
                analysis = pipeline.analyze(resume, job)
            st.session_state["last_analysis"] = analysis
            st.session_state["last_resume"] = resume
            _persist(db, resume, job, analysis)

    if len(resumes) > 1 and st.session_state.get("ranked_results"):
        render_section("Candidate ranking", "Ordered by job match score")
        ranked = st.session_state["ranked_results"]
        render_data_table(
            [
                {
                    "Rank": i + 1,
                    "Resume": r.file_name,
                    "Match (%)": round(a.match.match_score, 1),
                    "ATS score": round(a.ats.ats_score, 1),
                    "Grade": a.ats.grade,
                }
                for i, (r, a) in enumerate(ranked)
            ],
        )
        choice = st.selectbox(
            "Select candidate for detail view",
            range(len(ranked)),
            format_func=lambda i: (
                f"{ranked[i][0].file_name} — {ranked[i][1].match.match_score}% match"
            ),
        )
        resume, analysis = ranked[choice]
    elif st.session_state.get("last_analysis"):
        analysis = st.session_state["last_analysis"]
        resume = st.session_state.get("last_resume", resumes[0])
    else:
        render_empty_state(
            "Analysis has not been run for the current session.",
            'Click "Run analysis" to generate results.',
        )
        return

    _render_results(resume, analysis)


def _render_results(resume: ResumeData, analysis: AnalysisResult) -> None:
    """Display analysis UI sections."""
    tab_scores, tab_skills, tab_tips = st.tabs(
        [
            "Scores & metrics",
            "Skill analysis",
            "Recommendations",
        ]
    )

    with tab_scores:
        render_score_cards(
            analysis.ats.ats_score,
            analysis.ats.grade,
            analysis.match.match_score,
        )
        vertical_spacer(12)
        render_section(
            "Method comparison",
            "Hybrid (embeddings + skills) vs keyword-only baseline from methodology",
        )
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Hybrid match", f"{analysis.match.match_score}%")
        with m2:
            st.metric("Keyword baseline", f"{analysis.match.keyword_baseline_score}%")
        with m3:
            delta = analysis.match.match_score - analysis.match.keyword_baseline_score
            st.metric("Gain vs baseline", f"{delta:+.1f} pts")
        vertical_spacer(28)
        render_resume_metrics(resume)
        vertical_spacer(24)
        c1, c2 = st.columns(2, gap="large")
        with c1:
            render_match_gauge(analysis.match.match_score, analysis.match.semantic_similarity)
        with c2:
            render_skill_gap_chart(
                analysis.match.matched_skills,
                analysis.match.missing_skills,
            )
        vertical_spacer(16)
        render_section("ATS score breakdown")
        render_ats_breakdown_matplotlib(analysis.ats.breakdown)

    with tab_skills:
        render_skill_lists(analysis.match.matched_skills, analysis.match.missing_skills)
        render_section("Complete skill inventory")
        render_skill_distribution(resume.skills)

    with tab_tips:
        render_section("ATS optimization notes")
        for detail in analysis.ats.details:
            st.markdown(f"- {detail}")
        render_section("Actionable recommendations")
        for rec in analysis.recommendations:
            st.markdown(
                f"""
                <div class="info-banner" style="margin:0.4rem 0;">
                    {svg_icon("info", 16, "#1d4ed8")}
                    <span style="margin-left:0.4rem;">{rec}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _persist(db: DatabaseService, resume: ResumeData, job, analysis: AnalysisResult) -> None:
    """Save analysis to database."""
    aid = db.save_analysis(
        resume_name=resume.file_name or "resume",
        job_title=job.title or "Job",
        resume_text=resume.raw_text,
        job_description=job.raw_text,
        analysis=analysis,
        skills=resume.skills,
    )
    st.session_state["last_analysis_id"] = aid
    st.toast(f"Analysis record saved (ID {aid})")
