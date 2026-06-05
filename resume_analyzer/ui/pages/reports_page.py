"""Reports download and history page."""

from pathlib import Path

import streamlit as st

from resume_analyzer.services.resume_pipeline import ResumePipeline
from resume_analyzer.services.storage.database_service import DatabaseService
from resume_analyzer.services.storage.usability_service import mark_report_generated
from resume_analyzer.ui.components.data_table import render_data_table
from resume_analyzer.ui.components.layout import render_empty_state, render_page_header, render_section
from resume_analyzer.ui.icons import material


def render_reports_page(pipeline: ResumePipeline, db: DatabaseService) -> None:
    """
    Generate and download PDF reports.

    Args:
        pipeline: Resume pipeline.
        db: Database service.
    """
    render_page_header(
        "Reports & export",
        "Generate formal PDF reports and access previously exported documents.",
        "description",
    )

    has_analysis = bool(
        st.session_state.get("last_analysis") and st.session_state.get("last_resume")
    )

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        render_section("PDF report generation")
        if not has_analysis:
            render_empty_state(
                "No analysis available for export.",
                "Run a complete analysis before generating a report.",
            )
        else:
            resume = st.session_state["last_resume"]
            job = st.session_state.get("job")
            analysis = st.session_state["last_analysis"]
            st.caption(f"Subject: {resume.contact.name or resume.file_name}")

            if st.button(
                "Generate PDF report",
                type="primary",
                use_container_width=True,
                icon=material("pdf"),
            ):
                if job:
                    report_path = pipeline.generate_report(resume, job, analysis)
                    st.session_state["last_report_path"] = str(report_path)
                    aid = st.session_state.get("last_analysis_id")
                    if aid:
                        db.save_report(aid, report_path)
                    mark_report_generated()
                    st.success(f"Report generated: {report_path.name}")
                    st.info(
                        "Workflow complete. You can now open **Usability Study** in the sidebar "
                        "to submit anonymous feedback."
                    )

            report_path = st.session_state.get("last_report_path")
            if report_path and Path(report_path).exists():
                with open(report_path, "rb") as handle:
                    st.download_button(
                        label="Download report",
                        data=handle.read(),
                        file_name=Path(report_path).name,
                        mime="application/pdf",
                        use_container_width=True,
                        icon=material("download"),
                    )

    with col_b:
        render_section("Multi-candidate comparison")
        if st.session_state.get("resumes") and len(st.session_state["resumes"]) > 1:
            job = st.session_state.get("job")
            if job:
                comparison = pipeline.compare_resumes(st.session_state["resumes"], job)
                render_data_table(
                    [
                        {
                            "Resume": r.file_name,
                            "Match (%)": round(a.match.match_score, 1),
                            "ATS": round(a.ats.ats_score, 1),
                            "Skill gaps": len(a.match.missing_skills),
                        }
                        for r, a in comparison
                    ],
                )
        else:
            st.caption("Upload multiple resumes to enable side-by-side comparison.")

    render_section("Export history")
    reports = db.get_reports(limit=20)
    if reports:
        render_data_table(
            [
                {
                    "Resume": r["resume_name"],
                    "ATS": round(r["ats_score"] or 0, 1),
                    "Match (%)": round(r["match_score"] or 0, 1),
                    "Generated": (r["created_at"] or "")[:19].replace("T", " "),
                }
                for r in reports
            ],
        )
        valid_paths = [r["file_path"] for r in reports if Path(r["file_path"]).exists()]
        if valid_paths:
            selected = st.selectbox("Select archived report", valid_paths)
            if selected and Path(selected).exists():
                with open(selected, "rb") as handle:
                    st.download_button(
                        "Download selected report",
                        data=handle.read(),
                        file_name=Path(selected).name,
                        mime="application/pdf",
                        icon=material("download"),
                    )
    else:
        st.caption("Exported reports will appear in this section.")
