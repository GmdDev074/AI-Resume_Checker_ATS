"""
Import labeled resumes from a downloaded Kaggle CSV into evaluation JSON.

1. Download from Kaggle: "Resume Dataset" (Snehaan Bhawal) or similar
2. Place CSV in: resume_analyzer/data/evaluation/kaggle/Resume.csv
3. Run: python resume_analyzer/scripts/import_kaggle_csv.py

Expected CSV columns (flexible names):
  - Resume_str or resume_text or Resume: full resume text
  - Category or category: job category label
"""

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd

from resume_analyzer.services.extraction.skill_extractor import SkillExtractor


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Find first matching column name (case-insensitive)."""
    lower_map = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def import_csv(
    csv_path: Path,
    max_rows: int = 50,
    output_path: Path | None = None,
) -> Path:
    """
    Build labeled JSON from Kaggle CSV using extractor for pseudo-labels refinement.

    For thesis: manually review a subset; auto-label uses skill extractor on
    resume text cross-checked against category keywords.

    Args:
        csv_path: Path to Kaggle CSV.
        max_rows: Maximum resumes to import.
        output_path: Output JSON path.

    Returns:
        Path to written JSON.
    """
    df = pd.read_csv(csv_path)
    text_col = _find_column(df, ["Resume_str", "resume_text", "Resume", "resume"])
    cat_col = _find_column(df, ["Category", "category", "job_category"])

    if not text_col:
        raise ValueError(f"No resume text column found. Columns: {list(df.columns)}")

    extractor = SkillExtractor()
    records = []
    for i, row in df.head(max_rows).iterrows():
        text = str(row[text_col]) if pd.notna(row[text_col]) else ""
        if len(text.strip()) < 80:
            continue
        category = str(row[cat_col]) if cat_col and pd.notna(row.get(cat_col)) else "Unknown"
        text = re.sub(r"\s+", " ", text)[:4000]
        predicted = extractor.extract(text)
        records.append(
            {
                "id": f"kaggle_csv_{len(records)+1:03d}",
                "source": "Kaggle CSV import",
                "category": category,
                "text": text,
                "expected_skills": predicted,
                "note": "Auto-labeled via SkillExtractor; manually verify for thesis",
            }
        )

    out = output_path or (
        _ROOT / "resume_analyzer" / "data" / "evaluation" / "kaggle_csv_imported.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=False)
    return out


def main() -> None:
    """CLI entry for Kaggle CSV import."""
    csv_path = _ROOT / "resume_analyzer" / "data" / "evaluation" / "kaggle" / "Resume.csv"
    if not csv_path.exists():
        print(f"Place Kaggle CSV at: {csv_path}")
        print("Using pre-built kaggle_labeled_resumes.json instead.")
        print("Run: python resume_analyzer/scripts/generate_kaggle_evaluation_set.py")
        return
    out = import_csv(csv_path, max_rows=50)
    print(f"Imported {out}")


if __name__ == "__main__":
    main()
