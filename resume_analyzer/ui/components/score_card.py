"""Score card UI components."""

import streamlit as st

from resume_analyzer.ui.components.layout import vertical_spacer


def render_score_cards(ats_score: float, ats_grade: str, match_score: float) -> None:
    """
    Display ATS and match scores as professional stat cards.

    Args:
        ats_score: ATS numeric score.
        ats_grade: Letter grade.
        match_score: Job match percentage.
    """
    match_status = (
        "Strong alignment"
        if match_score >= 80
        else "Moderate fit"
        if match_score >= 60
        else "Improvement recommended"
    )
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(
            f"""
            <div class="score-card-pro">
                <div class="sc-label">ATS Compatibility</div>
                <div class="sc-value">{ats_score:.0f}<span class="sc-suffix">/ 100</span></div>
                <div class="sc-meta">Grade <strong>{ats_grade}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="score-card-pro match">
                <div class="sc-label">Job Match Score</div>
                <div class="sc-value">{match_score:.0f}<span class="sc-suffix">%</span></div>
                <div class="sc-meta">{match_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    vertical_spacer(32)
