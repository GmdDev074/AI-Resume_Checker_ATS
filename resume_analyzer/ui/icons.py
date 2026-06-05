"""Icons for UI — Streamlit material tokens and inline SVG for HTML blocks."""

# Streamlit widget prefix: :material/icon_name:
MATERIAL = {
    "dashboard": "space_dashboard",
    "upload": "upload_file",
    "analysis": "analytics",
    "reports": "description",
    "brand": "work_history",
    "scores": "score",
    "skills": "construction",
    "tips": "lightbulb",
    "person": "person",
    "school": "school",
    "download": "download",
    "pdf": "picture_as_pdf",
    "play": "play_arrow",
    "check": "check_circle",
    "warning": "error_outline",
    "info": "info",
    "rank": "leaderboard",
    "job": "business_center",
    "resume": "article",
    "search": "search",
    "feedback": "rate_review",
}


def material(icon_key: str) -> str:
    """
    Return Streamlit material icon token for buttons/widgets.

    Args:
        icon_key: Key in MATERIAL dict.

    Returns:
        String like ':material/dashboard:'.
    """
    name = MATERIAL.get(icon_key, icon_key)
    return f":material/{name}:"


def symbol(icon_name: str, size: int = 22, color: str = "#1d4ed8") -> str:
    """
    Material Symbol span (requires font injected via inject_styles).

    Args:
        icon_name: Material icon ligature name.
        size: Font size in pixels.
        color: Icon color.

    Returns:
        HTML string.
    """
    return (
        f'<span class="material-symbols-outlined" '
        f'style="font-size:{size}px;color:{color};vertical-align:middle;">'
        f"{icon_name}</span>"
    )


def svg_icon(name: str, size: int = 20, color: str = "#1d4ed8") -> str:
    """
    Inline SVG icon (works without external font — use in sidebar/HTML).

    Args:
        name: Icon key (check, info, briefcase, person).
        size: Width/height in px.
        color: Fill color.

    Returns:
        HTML SVG string.
    """
    paths = {
        "check": "M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
        "circle": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z",
        "briefcase": "M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-6 0h-4V4h4v2z",
        "person": "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z",
        "info": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z",
        "warn": "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
    }
    path = paths.get(name, paths["info"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="{color}" style="vertical-align:middle;flex-shrink:0;">'
        f'<path d="{path}"/></svg>'
    )
