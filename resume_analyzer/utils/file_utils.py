"""File and path helper utilities."""

import json
from pathlib import Path
from typing import Any, Dict, List


def ensure_dir(path: Path) -> Path:
    """
    Create directory if it does not exist.

    Args:
        path: Directory path.

    Returns:
        The same path after creation.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> Any:
    """
    Read JSON file safely.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed JSON content.

    Raises:
        FileNotFoundError: If file missing.
    """
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    """
    Write data to JSON file.

    Args:
        path: Target path.
        data: Serializable data.
    """
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def list_pdf_files(directory: Path) -> List[Path]:
    """
    List PDF files in a directory.

    Args:
        directory: Folder to scan.

    Returns:
        Sorted list of PDF paths.
    """
    if not directory.exists():
        return []
    return sorted(directory.glob("*.pdf"))
