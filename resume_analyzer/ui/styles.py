"""Global CSS — professional enterprise theme."""


def inject_styles() -> None:
    """Inject fonts and light-theme CSS into the app."""
    import streamlit as st

    st.markdown(
        f"<style>{_font_imports()}{_light_rules()}{_component_rules()}</style>",
        unsafe_allow_html=True,
    )


def _font_imports() -> str:
    """Font imports and icon class."""
    return """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined', sans-serif;
        font-weight: normal;
        font-style: normal;
        line-height: 1;
        display: inline-block;
        vertical-align: middle;
    }
    """


def _component_rules() -> str:
    """Shared UI component rules for tables, tabs, columns, inputs."""
    bg_surface = "#ffffff"
    border = "#e2e8f0"
    text = "#0f172a"
    text_muted = "#64748b"
    header_bg = "#f8fafc"
    hover = "#f1f5f9"
    input_bg = "#ffffff"

    return f"""
    .main .block-container {{
        padding: 1.75rem 2rem 2.5rem !important;
        max-width: 1280px !important;
    }}

    [data-testid="column"] {{
        padding: 0 0.65rem !important;
    }}
    [data-testid="column"]:first-child {{ padding-left: 0 !important; }}
    [data-testid="column"]:last-child {{ padding-right: 0 !important; }}

    .table-panel {{
        margin: 0.5rem 0 1.25rem 0;
        width: 100%;
    }}

    div[data-testid="stDataFrame"] {{
        width: 100% !important;
        border: 1px solid {border};
        border-radius: 10px;
        overflow: hidden;
        background: {bg_surface};
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    div[data-testid="stDataFrame"] > div {{
        width: 100% !important;
    }}
    div[data-testid="stDataFrame"] [data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
    }}
    div[data-testid="stDataFrame"] canvas {{
        max-width: 100% !important;
    }}

    .app-table-scroll {{
        border-radius: 10px;
        border: 1px solid {border};
        background: {bg_surface};
    }}
    table.app-data-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        background: {bg_surface};
        color: {text};
    }}
    table.app-data-table thead th {{
        background: {header_bg};
        color: {text_muted};
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.68rem;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem;
        text-align: left;
        border-bottom: 1px solid {border};
        position: sticky;
        top: 0;
        z-index: 1;
    }}
    table.app-data-table tbody td {{
        padding: 0.7rem 1rem;
        border-bottom: 1px solid {border};
        color: {text};
        vertical-align: middle;
    }}
    table.app-data-table tbody tr:hover td {{
        background: {hover};
    }}
    table.app-data-table tbody tr:last-child td {{
        border-bottom: none;
    }}

    .skill-tags-wrap {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem 0.45rem;
        align-items: center;
        margin-top: 0.65rem;
        padding: 0.85rem;
        border-radius: 10px;
        border: 1px solid {border};
        background: {bg_surface};
        max-height: 300px;
        overflow-y: auto;
    }}
    .skill-tags-wrap .skill-chip {{
        margin: 0 !important;
        flex-shrink: 0;
    }}
    .skill-chip,
    [data-testid="stMarkdownContainer"] .skill-chip,
    [data-testid="stMarkdownContainer"] .skill-tags-wrap .skill-chip {{
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 6px !important;
        -webkit-border-radius: 6px !important;
        font-size: 0.78rem;
        font-weight: 500;
        line-height: 1.35;
        box-sizing: border-box;
        overflow: hidden;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid {border};
        padding-bottom: 0;
    }}
    .stTabs [data-baseweb="tab"] {{
        padding: 0.65rem 1.1rem !important;
        font-weight: 500;
        color: {text_muted} !important;
        border-radius: 8px 8px 0 0;
    }}
    .stTabs [aria-selected="true"] {{
        color: {text} !important;
        background: {bg_surface};
        border: 1px solid {border};
        border-bottom-color: {bg_surface} !important;
    }}

    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border-radius: 8px !important;
        border-color: {border} !important;
    }}
    [data-testid="stExpander"] {{
        border: 1px solid {border} !important;
        border-radius: 10px !important;
        background: {bg_surface} !important;
        margin-bottom: 0.75rem;
    }}
    [data-testid="stExpander"] summary {{
        padding: 0.75rem 1rem !important;
        color: {text} !important;
    }}

    div[data-testid="stAlert"] {{
        border-radius: 8px;
        margin: 0.5rem 0;
    }}

    .section-block {{
        margin-bottom: 1.75rem;
        padding-bottom: 0.25rem;
    }}

    .empty-hint {{
        color: {text_muted};
    }}

    h1, h2, h3, p, span, label {{
        overflow-wrap: break-word;
    }}
    """


def _light_rules() -> str:
    """Light theme surface colors."""
    return """
    html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
    .stApp { background-color: #f1f5f9; }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] > div:first-child { background-color: #ffffff; }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p,
    [data-testid="stSidebar"] label { color: #334155 !important; }
    [data-testid="stSidebar"] .brand-title { color: #0f172a !important; }
    [data-testid="stSidebar"] .brand-subtitle { color: #64748b !important; }
    [data-testid="stSidebar"] hr { border-color: #e2e8f0; margin: 0.85rem 0; }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.1rem 1.15rem 1.15rem;
        min-height: 92px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        overflow: visible !important;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.68rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b !important;
        padding-top: 0.1rem !important;
        margin-bottom: 0.3rem !important;
        line-height: 1.3 !important;
        white-space: normal !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.45rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #1d4ed8 !important;
        border: 1px solid #1e40af !important;
        border-radius: 8px;
        font-weight: 600;
    }

    .page-header {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .page-header-icon-wrap {
        width: 48px; height: 48px; border-radius: 10px;
        background: #eff6ff; border: 1px solid #bfdbfe;
        display: flex; align-items: center; justify-content: center;
    }
    .page-header h1 { margin: 0; font-size: 1.45rem; font-weight: 600; color: #0f172a; }
    .page-header p { margin: 0.35rem 0 0; font-size: 0.9rem; color: #64748b; line-height: 1.5; }

    [data-testid="column"] .score-card-pro {
        margin-bottom: 0.5rem;
    }
    .score-card-pro {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
        padding: 1.5rem 1.6rem 1.65rem; border-left: 4px solid #1d4ed8;
        margin-bottom: 0.5rem;
        min-height: 132px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .score-card-pro.match { border-left-color: #0369a1; }
    .score-card-pro .sc-label {
        font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.06em; color: #64748b;
        margin-bottom: 0.5rem;
    }
    .score-card-pro .sc-value {
        font-size: 2rem; font-weight: 700; color: #0f172a;
        line-height: 1.35;
        margin: 0.5rem 0 0.75rem;
        padding-bottom: 0.15rem;
    }
    .score-card-pro .sc-suffix {
        font-size: 1rem; font-weight: 500; color: #64748b;
        margin-left: 0.35rem;
    }
    .score-card-pro .sc-meta {
        font-size: 0.82rem; color: #475569;
        margin-top: auto;
        padding-top: 0.85rem;
        border-top: 1px solid #e2e8f0;
        line-height: 1.45;
    }
    .profile-card {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    .profile-name { color: #0f172a; font-weight: 600; font-size: 1rem; }
    .profile-email { color: #64748b; font-size: 0.82rem; }
    .v-spacer {
        display: block !important;
        width: 100% !important;
        flex-shrink: 0;
        border: none;
        background: transparent;
    }
    div[data-testid="stVerticalBlock"] > div:has(.score-card-pro) {
        gap: 0.5rem;
    }
    div[data-testid="stPlotlyChart"] {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .skill-chip-match { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    .skill-chip-miss { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

    .info-banner {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-left: 3px solid #1d4ed8; border-radius: 8px;
        padding: 1rem 1.15rem; margin: 0.85rem 0; color: #334155;
    }

    .survey-panel-meta {
        margin-bottom: 0.65rem;
    }
    .survey-panel-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .survey-panel-desc {
        font-size: 0.82rem;
        color: #64748b;
        margin-bottom: 0.45rem;
        line-height: 1.45;
    }
    .survey-scale-hint {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #475569;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.45rem 0.75rem;
        margin-bottom: 0.5rem;
    }
    .survey-field-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        margin-bottom: 0.35rem;
    }
    .survey-field-table th {
        background: #f8fafc;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.68rem;
        letter-spacing: 0.05em;
        padding: 0.55rem 0.75rem;
        border: 1px solid #e2e8f0;
        text-align: left;
    }
    .survey-field-table td {
        padding: 0.5rem 0.75rem;
        border: 1px solid #e2e8f0;
        color: #334155;
        vertical-align: middle;
    }
    div[data-testid="stForm"] {
        margin-top: 0.5rem;
    }
    div[data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] {
        margin-bottom: 1rem;
    }
    .profile-card {
        background: #ffffff; border: 1px solid #e2e8f0;
        border-radius: 10px; padding: 1.1rem 1.25rem; margin-bottom: 1.25rem;
    }

    .status-pill {
        display: inline-flex; align-items: center; gap: 0.4rem;
        padding: 0.3rem 0.7rem; border-radius: 6px; font-size: 0.72rem;
        margin: 0.2rem 0.25rem 0.2rem 0; border: 1px solid #e2e8f0;
        background: #f8fafc; color: #64748b;
    }
    .status-pill.done { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }

    .workflow-step {
        display: flex; align-items: flex-start; gap: 0.7rem;
        padding: 0.5rem 0; font-size: 0.8rem; color: #475569; line-height: 1.45;
    }
    .workflow-num {
        width: 1.4rem; height: 1.4rem; border-radius: 6px;
        background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 0.68rem; font-weight: 700; flex-shrink: 0;
    }

    .section-label {
        font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.06em; color: #64748b;
        margin: 0 0 0.65rem 0; display: block;
    }
    .skill-list-heading {
        font-weight: 600;
        font-size: 0.95rem;
        color: #0f172a;
        margin-bottom: 0.35rem;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    """
