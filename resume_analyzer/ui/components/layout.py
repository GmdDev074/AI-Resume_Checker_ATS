"""Layout helpers: headers, sections, empty states, workflow."""

import streamlit as st

from resume_analyzer.ui.icons import svg_icon, symbol


def render_page_header(title: str, subtitle: str, icon_name: str = "article") -> None:
    """
    Render a professional page header with Material icon.

    Args:
        title: Page title.
        subtitle: Short description.
        icon_name: Material Symbols ligature name.
    """
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-icon-wrap">
                {symbol(icon_name, 26, "#1d4ed8")}
            </div>
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def vertical_spacer(pixels: int = 24) -> None:
    """
    Insert reliable vertical gap between Streamlit blocks.

    HTML wrappers do not wrap the next widget; use this between components.

    Args:
        pixels: Spacer height in pixels.
    """
    st.markdown(
        f'<div class="v-spacer" style="height:{pixels}px;min-height:{pixels}px;'
        f'display:block;width:100%;"></div>',
        unsafe_allow_html=True,
    )


def render_section(title: str, description: str = "") -> None:
    """
    Render a section heading.

    Args:
        title: Section title.
        description: Optional helper text.
    """
    st.markdown(f'<p class="section-label">{title}</p>', unsafe_allow_html=True)
    if description:
        st.caption(description)


def render_empty_state(message: str, action_hint: str = "") -> None:
    """
    Professional empty state banner.

    Args:
        message: Main message.
        action_hint: What the user should do next.
    """
    hint = (
        f'<div class="empty-hint" style="margin-top:0.35rem;font-size:0.85rem;">'
        f"<strong>Next step:</strong> {action_hint}</div>"
        if action_hint
        else ""
    )
    st.markdown(
        f"""
        <div class="info-banner" style="display:flex;align-items:flex-start;gap:0.5rem;">
            {svg_icon("info", 18, "#1d4ed8")}
            <div><span>{message}</span>{hint}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_sidebar() -> None:
    """Render numbered workflow steps in the sidebar."""
    steps = [
        "Upload resume (PDF)",
        "Enter job description",
        "Run analysis",
        "Export PDF report",
    ]
    html = "".join(
        f'<div class="workflow-step"><span class="workflow-num">{i}</span><span>{s}</span></div>'
        for i, s in enumerate(steps, 1)
    )
    st.sidebar.markdown('<p class="section-label">Workflow</p>', unsafe_allow_html=True)
    st.sidebar.markdown(html, unsafe_allow_html=True)


def render_status_pills(
    has_resume: bool,
    has_job: bool,
    has_analysis: bool,
    has_report: bool = False,
) -> None:
    """
    Show session progress in sidebar.

    Args:
        has_resume: Resume parsed.
        has_job: Job loaded.
        has_analysis: Analysis complete.
        has_report: PDF report generated (unlocks usability study).
    """
    def pill(ok: bool, label: str) -> str:
        cls = "status-pill done" if ok else "status-pill"
        if ok:
            ic = svg_icon("check", 14, "#166534")
        else:
            ic = svg_icon("circle", 14, "#94a3b8")
        return f'<span class="{cls}">{ic}<span>{label}</span></span>'

    st.sidebar.markdown('<p class="section-label">Session</p>', unsafe_allow_html=True)
    st.sidebar.markdown(
        pill(has_resume, "Resume")
        + pill(has_job, "Job")
        + pill(has_analysis, "Analysis")
        + pill(has_report, "Report"),
        unsafe_allow_html=True,
    )
