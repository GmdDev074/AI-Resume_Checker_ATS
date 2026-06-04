"""Resume metrics display components."""

import streamlit as st

from resume_analyzer.models.resume_model import ResumeData
from resume_analyzer.ui.icons import svg_icon
from resume_analyzer.ui.components.layout import vertical_spacer


def render_resume_metrics(resume: ResumeData) -> None:
    """
    Display candidate profile and key metrics.

    Args:
        resume: Parsed resume data.
    """
    name = resume.contact.name or "Candidate"
    email = resume.contact.email or "Not provided"
    vertical_spacer(8)
    st.markdown(
        f"""
        <div class="profile-card">
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="width:44px;height:44px;border-radius:8px;background:#eff6ff;
                     border:1px solid #bfdbfe;display:flex;align-items:center;justify-content:center;">
                    {svg_icon("person", 24, "#1d4ed8")}
                </div>
                <div>
                    <div class="profile-name">{name}</div>
                    <div class="profile-email">{email}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    vertical_spacer(20)

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        st.metric("Experience", f"{resume.total_experience_years} yrs")
    with col2:
        st.metric("Education", len(resume.education))
    with col3:
        st.metric("Skills", resume.skills_count)
    with col4:
        st.metric("Roles listed", len(resume.experience))

    if resume.education:
        edu = resume.education[0]
        parts = [p for p in [edu.degree, edu.university, edu.graduation_year] if p]
        if parts:
            st.caption("Education: " + " · ".join(parts))
