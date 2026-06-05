"""Usability study survey — unlocked after full workflow including PDF report."""

import streamlit as st

from resume_analyzer.services.storage.database_service import DatabaseService
from resume_analyzer.services.storage.usability_service import (
    LIKERT_QUESTIONS,
    SUS_QUESTIONS,
    TASK_LABELS,
    UsabilityService,
    compute_sus_score,
    is_usability_study_unlocked,
    openpyxl_available,
)
from resume_analyzer.ui.components.data_table import render_data_table
from resume_analyzer.ui.components.layout import (
    render_empty_state,
    render_page_header,
    render_section,
    vertical_spacer,
)
from resume_analyzer.ui.icons import material


def _render_researcher_export(service: UsabilityService) -> None:
    """Download section for the student/researcher to export data for the thesis."""
    summary = service.summarize()

    st.markdown(
        """
        <div class="info-banner" style="margin-bottom:1rem;">
            <strong>Researcher — download responses for thesis</strong><br/>
            After participants submit (P01, P02, …), export data below. The Excel file includes
            <em>tables + bar charts</em> ready for your evaluation chapter.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if summary.response_count == 0:
        st.info("No responses yet. Share your app link and ask each tester to submit the survey.")
        return

    m1, m2, m3 = st.columns(3)
    m1.metric("Responses collected", summary.response_count)
    m2.metric("Mean SUS", f"{summary.mean_sus} / 100")
    m3.metric("Recommended export", "Excel (.xlsx)")

    render_section("Participant summary")
    render_data_table(service.thesis_summary_rows())

    vertical_spacer(8)
    render_section("Download files")

    csv_data = service.export_csv_text()
    json_data = service.export_json_text()

    d1, d2, d3 = st.columns(3)
    with d1:
        if openpyxl_available():
            try:
                excel_bytes = service.export_excel_bytes()
                st.download_button(
                    label="Download Excel (tables + charts)",
                    data=excel_bytes,
                    file_name="usability_study_thesis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary",
                    icon=material("download"),
                )
                st.caption("Sheets: Responses, Summary, Charts with bar graphs.")
            except Exception as exc:
                st.error(f"Excel export failed: {exc}")
        else:
            st.warning("Install openpyxl for Excel export:")
            st.code("pip install openpyxl", language="bash")
    with d2:
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="usability_responses.csv",
            mime="text/csv",
            use_container_width=True,
            icon=material("download"),
        )
        st.caption("Raw rows for simple tables.")
    with d3:
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="usability_responses.json",
            mime="application/json",
            use_container_width=True,
            icon=material("download"),
        )
        st.caption("Full data + aggregate stats.")

    st.caption(
        "CLI: `python resume_analyzer/scripts/export_usability_report.py` also writes JSON to "
        "`data/evaluation/usability_responses.json`."
    )


def render_usability_page(db: DatabaseService) -> None:
    """
    Render usability study form (only when workflow is complete).

    Args:
        db: Database service.
    """
    if not is_usability_study_unlocked():
        render_page_header(
            "Usability study",
            "Complete the full workflow before participating in the study.",
            "rate_review",
        )
        render_empty_state(
            "The usability survey is not available yet.",
            "Complete Upload → Analysis → then click **Generate PDF report** on the "
            "Reports page. The Usability Study menu appears after that step.",
        )
        return

    service = UsabilityService(db)

    render_page_header(
        "Usability study",
        "Anonymous academic feedback after completing the end-to-end workflow.",
        "rate_review",
    )

    _render_researcher_export(service)

    vertical_spacer(20)
    st.markdown("---")
    vertical_spacer(8)

    st.markdown(
        """
        <div class="info-banner">
            <strong>Participant consent.</strong> Responses are anonymous and used for Final Year
            Project evaluation only. Do not enter real names. Use a code such as <em>P01</em>,
            <em>P02</em>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("usability_submitted"):
        st.success("Thank you — your response has been recorded.")
        st.caption(
            f"Total responses: {service.summarize().response_count}. "
            "Researchers: scroll up to download Excel/CSV for the thesis."
        )
        if st.button("Submit another response (new participant ID)", icon=material("feedback")):
            st.session_state["usability_submitted"] = False
            st.rerun()
        return

    with st.form("usability_study_form", clear_on_submit=False):
        render_section("Participant", "Optional demographics — no personal names")
        participant_id = st.text_input(
            "Participant ID *",
            placeholder="e.g. P01",
            max_chars=20,
            help="Required. Use a unique code per person.",
        )
        role = st.selectbox(
            "Your role",
            options=["Student", "Job seeker", "Recruiter / HR", "Academic reviewer", "Other"],
        )

        vertical_spacer(8)
        render_section(
            "Task checklist",
            "Confirm each step you completed during this session (after trying the app)",
        )
        task_success: dict[int, bool] = {}
        task_times: dict[int, int] = {}
        for i, label in enumerate(TASK_LABELS, start=1):
            c1, c2 = st.columns([3, 1])
            with c1:
                task_success[i] = st.checkbox(label, value=True, key=f"task_ok_{i}")
            with c2:
                task_times[i] = st.number_input(
                    f"T{i} min",
                    min_value=0,
                    max_value=120,
                    value=0,
                    step=1,
                    key=f"task_min_{i}",
                    help="Approximate minutes spent on this task (0 if skipped)",
                )

        vertical_spacer(8)
        render_section("Experience survey", "1 = Strongly disagree · 5 = Strongly agree")
        likert: dict[int, int] = {}
        for i, question in enumerate(LIKERT_QUESTIONS, start=1):
            likert[i] = st.slider(question, 1, 5, 3, key=f"likert_{i}")

        vertical_spacer(8)
        render_section("System Usability Scale (SUS)", "Standard 10-item SUS questionnaire")
        sus: dict[int, int] = {}
        for i, question in enumerate(SUS_QUESTIONS, start=1):
            sus[i] = st.slider(f"{i}. {question}", 1, 5, 3, key=f"sus_{i}")

        comments = st.text_area(
            "Optional comments",
            placeholder="What would you improve? Which step was hardest?",
            height=100,
        )

        submitted = st.form_submit_button(
            "Submit usability response",
            type="primary",
            use_container_width=True,
            icon=material("check"),
        )

    if submitted:
        pid = (participant_id or "").strip()
        if not pid:
            st.error("Participant ID is required (e.g. P01).")
            return
        if db.participant_id_exists(pid):
            st.error(f"Participant ID '{pid}' already exists. Use a unique code.")
            return

        sus_ratings = [sus[i] for i in range(1, 11)]
        try:
            sus_score = compute_sus_score(sus_ratings)
        except ValueError as exc:
            st.error(str(exc))
            return

        payload = {
            "participant_id": pid,
            "role": role,
            "analysis_id": st.session_state.get("last_analysis_id"),
        }
        for i in range(1, 6):
            payload[f"task_t{i}_success"] = 1 if task_success.get(i) else 0
            minutes = int(task_times.get(i) or 0)
            payload[f"task_t{i}_time_sec"] = minutes * 60 if minutes > 0 else None
        for i in range(1, 7):
            payload[f"likert_q{i}"] = likert[i]
        for i in range(1, 11):
            payload[f"sus_q{i}"] = sus[i]
        payload["sus_score"] = sus_score
        payload["comments"] = comments.strip() or None

        record_id = service.save_response(payload)
        st.session_state["usability_submitted"] = True
        st.success(f"Response saved (record #{record_id}). SUS score: {sus_score}/100")
        st.rerun()
