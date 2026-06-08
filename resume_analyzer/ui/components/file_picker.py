"""Native file picker helpers for resume uploads."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, TypedDict


class PickedResumeFile(TypedDict):
    """Resume file selected outside the browser upload widget."""

    name: str
    data: bytes


def windows_file_picker_available() -> bool:
    """Return True when the native Windows dialog can be used."""
    return sys.platform == "win32"


def pick_resume_files_native() -> List[PickedResumeFile]:
    """
    Open the Windows file dialog with explicit Word/PDF filters.

    Returns:
        Selected files as name/bytes pairs. Empty if cancelled or unavailable.
    """
    if not windows_file_picker_available():
        return []

    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        paths = filedialog.askopenfilenames(
            title="Select resume file(s)",
            filetypes=[
                ("Resume files", "*.pdf;*.doc;*.docx"),
                ("PDF files", "*.pdf"),
                ("Word documents", "*.doc;*.docx"),
                ("All files", "*.*"),
            ],
        )
    finally:
        root.destroy()

    picked: List[PickedResumeFile] = []
    for path in paths:
        file_path = Path(path)
        picked.append({"name": file_path.name, "data": file_path.read_bytes()})
    return picked
