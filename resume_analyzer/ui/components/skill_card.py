"""Skill display components."""

from typing import List

import streamlit as st

from resume_analyzer.ui.icons import svg_icon


def _chips_html(skills: List[str], css_class: str) -> str:
    """Build HTML for skill chip row."""
    if not skills:
        return '<span class="empty-hint">None detected</span>'
    return "".join(f'<span class="skill-chip {css_class}">{s}</span>' for s in skills)


def render_skill_lists(matched: List[str], missing: List[str]) -> None:
    """
    Show matched and missing skills as professional chips.

    Args:
        matched: Skills found in resume.
        missing: Skills required but not found.
    """
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="skill-list-heading">'
            f'{svg_icon("check", 16, "#166534")} '
            f'<span style="margin-left:0.35rem;">Matched skills</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="skill-tags-wrap">{_chips_html(matched, "skill-chip-match")}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"{len(matched)} skills aligned with job requirements")
    with col2:
        st.markdown(
            f'<div class="skill-list-heading">'
            f'{svg_icon("warn", 16, "#b91c1c")} '
            f'<span style="margin-left:0.35rem;">Skills to develop</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="skill-tags-wrap">{_chips_html(missing, "skill-chip-miss")}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"{len(missing)} gaps identified from job description")
