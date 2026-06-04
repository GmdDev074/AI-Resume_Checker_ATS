"""Chart components for analytics visualization."""

from typing import List

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from resume_analyzer.ui.components.layout import vertical_spacer

CHART_COLORS = ["#1d4ed8", "#0369a1", "#0ea5e9", "#334155", "#64748b", "#94a3b8"]


def _chart_layout() -> dict:
    """Plotly layout defaults."""
    return dict(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, system-ui, sans-serif", color="#475569"),
        margin=dict(l=24, r=24, t=48, b=24),
    )


def render_skill_distribution(skills: List[str]) -> None:
    """
    Plot skill distribution bar chart.

    Args:
        skills: List of skill names.
    """
    if not skills:
        st.caption("No skills to visualize.")
        return
    fig = px.bar(
        x=skills,
        y=[1] * len(skills),
        labels={"x": "Skill", "y": ""},
        color=skills,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(
        **_chart_layout(),
        showlegend=False,
        height=320,
        title=dict(text="Detected Skills", font=dict(size=14)),
    )
    fig.update_yaxes(visible=False)
    st.plotly_chart(fig, use_container_width=True)


def render_match_gauge(match_score: float, semantic_score: float) -> None:
    """
    Display job match gauge with scores shown outside the chart (no overlap).

    Args:
        match_score: Combined match score.
        semantic_score: Semantic similarity percentage.
    """
    st.markdown('<p class="section-label">Job match</p>', unsafe_allow_html=True)

    m1, m2 = st.columns(2)
    with m1:
        st.metric("Match score", f"{match_score:.1f}%")
    with m2:
        st.metric("Semantic similarity", f"{semantic_score:.1f}%")

    vertical_spacer(8)

    fig = go.Figure(
        go.Indicator(
            mode="gauge",
            value=match_score,
            title=dict(text="", font=dict(size=1)),
            domain={"x": [0.1, 0.9], "y": [0.08, 0.95]},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#94a3b8",
                    "tickwidth": 1,
                    "tickmode": "linear",
                    "tick0": 0,
                    "dtick": 20,
                },
                "bar": {"color": "#1d4ed8", "thickness": 0.7},
                "bgcolor": "#f1f5f9",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "#fecaca"},
                    {"range": [50, 75], "color": "#fde68a"},
                    {"range": [75, 100], "color": "#bbf7d0"},
                ],
            },
        )
    )
    layout = _chart_layout()
    layout["margin"] = dict(l=32, r=32, t=16, b=32)
    fig.update_layout(**layout, height=220)
    st.plotly_chart(fig, use_container_width=True)


def render_skill_gap_chart(matched: List[str], missing: List[str]) -> None:
    """
    Visualize skill gap between matched and missing.

    Args:
        matched: Matched skills.
        missing: Missing skills.
    """
    st.markdown('<p class="section-label">Skill gap</p>', unsafe_allow_html=True)
    labels = ["Matched", "Missing"]
    values = [len(matched), len(missing)]
    fig = px.pie(
        names=labels,
        values=values,
        hole=0.45,
        color=labels,
        color_discrete_map={
            "Matched": "#1d4ed8",
            "Missing": "#64748b",
        },
    )
    fig.update_layout(
        **_chart_layout(),
        height=280,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_ats_breakdown_matplotlib(breakdown: dict) -> None:
    """
    Render ATS factor breakdown using Matplotlib.

    Args:
        breakdown: ATS score breakdown dictionary.
    """
    import matplotlib.pyplot as plt

    labels = [k.replace("_", " ").title() for k in breakdown.keys()]
    values = list(breakdown.values())
    fig, ax = plt.subplots(figsize=(7, 3.2))
    bars = ax.barh(labels, values, color="#1d4ed8", edgecolor="none", height=0.55)
    text_color = "#334155"
    for bar, val in zip(bars, values):
        ax.text(
            val + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}",
            va="center",
            fontsize=9,
            color=text_color,
        )
    ax.set_xlabel("Points earned", fontsize=9, color=text_color)
    ax.tick_params(colors=text_color)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("#fafafa")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
