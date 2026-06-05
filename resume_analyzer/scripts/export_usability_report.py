#!/usr/bin/env python
"""Export usability study results for thesis tables."""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from resume_analyzer.config.settings import get_settings
from resume_analyzer.services.storage.usability_service import UsabilityService


def main() -> None:
    """Write JSON export and print summary tables to stdout."""
    settings = get_settings()
    out_path = settings.data_dir / "evaluation" / "usability_responses.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    service = UsabilityService()
    payload = service.build_export_payload()
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    xlsx_path = settings.data_dir / "evaluation" / "usability_study_thesis.xlsx"
    xlsx_path.write_bytes(service.export_excel_bytes())

    summary = service.summarize()
    print("=" * 60)
    print("USABILITY STUDY EXPORT")
    print("=" * 60)
    print(f"Responses: {summary.response_count}")
    print(f"Mean SUS:  {summary.mean_sus}/100")
    print(f"JSON:      {out_path}")
    print(f"Excel:     {xlsx_path}")
    print()

    if summary.response_count == 0:
        print("No responses yet. Collect data via the Usability Study page in the app.")
        return

    print("Task success rates (%)")
    print("-" * 40)
    for task_id, rate in sorted(summary.task_success_rates.items()):
        print(f"  {task_id}: {rate}%")

    print()
    print("Mean Likert scores (1–5)")
    print("-" * 40)
    for q_id, mean in sorted(summary.mean_likert.items()):
        print(f"  {q_id}: {mean}")

    print()
    print("Mean task times (seconds)")
    print("-" * 40)
    for task_id, mean_sec in sorted(summary.mean_task_times_sec.items()):
        display = f"{mean_sec}s" if mean_sec is not None else "n/a"
        print(f"  {task_id}: {display}")

    print()
    print("Per-participant SUS")
    print("-" * 40)
    for row in payload["responses"]:
        print(
            f"  {row.get('participant_id')}: SUS={row.get('sus_score')} "
            f"role={row.get('role')}"
        )


if __name__ == "__main__":
    main()
