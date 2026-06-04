"""Sidebar branding and global styles."""

import streamlit as st

from resume_analyzer.ui.icons import svg_icon
from resume_analyzer.ui.styles import inject_styles


def apply_theme() -> None:
    """Render sidebar branding and inject light-theme CSS."""
    st.sidebar.markdown(
        f"""
        <div class="brand-block" style="padding:0.35rem 0 1.1rem;">
            <div style="display:flex;align-items:center;gap:0.75rem;">
                <div style="width:42px;height:42px;border-radius:10px;background:#1d4ed8;
                     display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    {svg_icon("briefcase", 22, "#ffffff")}
                </div>
                <div style="min-width:0;">
                    <div class="brand-title" style="font-size:0.95rem;font-weight:600;
                         letter-spacing:-0.01em;line-height:1.3;">Resume Analyzer</div>
                    <div class="brand-subtitle" style="font-size:0.72rem;font-weight:500;
                         line-height:1.35;margin-top:0.15rem;">AI Job Matching System</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    inject_styles()
