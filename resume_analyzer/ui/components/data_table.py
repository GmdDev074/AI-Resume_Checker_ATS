"""Styled table helper — HTML table for consistent theming."""

import html
from typing import Any, Dict, List, Optional

import streamlit as st


def render_data_table(
    rows: List[Dict[str, Any]],
    *,
    full_width: bool = True,
    height: Optional[int] = None,
) -> None:
    """
    Render a styled data table as HTML.

    Args:
        rows: List of row dictionaries.
        full_width: Expand to container width.
        height: Optional max-height hint for scrollable wrapper.
    """
    if not rows:
        return

    headers = list(rows[0].keys())
    head_html = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    body_rows = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(str(row.get(h, '')))}</td>" for h in headers
        )
        body_rows.append(f"<tr>{cells}</tr>")
    body_html = "".join(body_rows)

    max_h = f"max-height:{height}px;" if height else "max-height:360px;"
    scroll = "overflow:auto;" if height or len(rows) > 8 else ""

    st.markdown(
        f"""
        <div class="table-panel" style="width:{'100%' if full_width else 'auto'};">
            <div class="app-table-scroll" style="{max_h}{scroll}">
                <table class="app-data-table">
                    <thead><tr>{head_html}</tr></thead>
                    <tbody>{body_html}</tbody>
                </table>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
