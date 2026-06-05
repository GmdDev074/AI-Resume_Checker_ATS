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
    docx_install_hint,
)
from resume_analyzer.ui.components.data_table import render_data_table
from resume_analyzer.ui.components.layout import (
    render_empty_state,
    render_page_header,
    render_section,
    vertical_spacer,
)
from resume_analyzer.ui.icons import material

LIKERT_MIN = "1 — Strongly disagree"
LIKERT_MAX = "5 — Strongly agree"
TIME_MIN = "0 min"
TIME_MAX = "120 min"
TIME_MINUTE_OPTIONS = [f"{m} min" for m in range(121)]


def _parse_minutes(label: str) -> int:
    """Convert a selectbox label like '5 min' to integer minutes."""
    return int(str(label).split()[0])


def _valid_email(email: str) -> bool:
    """Basic email format check."""
    value = (email or "").strip()
    if "@" not in value or len(value) < 5:
        return False
    local, _, domain = value.partition("@")
    return bool(local and domain and "." in domain)


def _panel_header(title: str, description: str, min_label: str = "", max_label: str = "") -> None:
    """Section title with optional min/max scale indicators."""
    scale_block = ""
    if min_label and max_label:
        scale_block = (
            f'<div class="survey-scale-hint">'
            f"<span>Min: {min_label}</span><span>Max: {max_label}</span>"
            f"</div>"
        )
    st.markdown(
        f"""
        <div class="survey-panel-meta">
            <div class="survey-panel-title">{title}</div>
            <div class="survey-panel-desc">{description}</div>
            {scale_block}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_researcher_export(service: UsabilityService) -> None:
    """Download section for the student/researcher to export data for the thesis."""
    summary = service.summarize()

    st.markdown(
        """
        <div class="info-banner" style="margin-bottom:1rem;">
            <strong>Researcher — download responses for thesis</strong><br/>
            After participants submit (P01, P02, …), download <strong>JSON</strong> or
            <strong>Microsoft Word</strong> for your thesis evaluation chapter.
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
    m3.metric("Recommended export", "Word (.docx)")

    render_section("Participant summary")
    render_data_table(service.thesis_summary_rows())

    vertical_spacer(8)
    render_section("Download files")

    json_data = service.export_json_text()

    d1, d2 = st.columns(2)
    with d1:
        try:
            docx_bytes = service.export_docx_bytes()
            st.download_button(
                label="Download Microsoft Word (.docx)",
                data=docx_bytes,
                file_name="usability_study_thesis.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="primary",
                icon=material("download"),
            )
            st.caption(
                "Thesis-ready tables with full question text: tasks, Likert, SUS, aggregates."
            )
        except ImportError:
            st.warning(
                "Word export needs **python-docx** in the same Python environment "
                "that runs Streamlit (not just your terminal `pip`)."
            )
            st.code(docx_install_hint(), language="bash")
            st.caption(
                "Then restart the app: stop Streamlit (Ctrl+C) and run "
                "`python -m streamlit run resume_analyzer/app.py` again. "
                "On Streamlit Cloud, push `requirements.txt` and redeploy."
            )
        except Exception as exc:
            st.error(f"Word export failed: {exc}")
    with d2:
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="usability_responses.json",
            mime="application/json",
            use_container_width=True,
            icon=material("download"),
        )
        st.caption("Full structured data + aggregate statistics.")

    st.caption(
        "CLI: `python resume_analyzer/scripts/export_usability_report.py` also writes JSON to "
        "`data/evaluation/usability_responses.json`."
    )


def _save_usability_response(
    service: UsabilityService,
    db: DatabaseService,
    *,
    full_name: str,
    email: str,
    phone: str,
    role: str,
    task_success: dict[int, bool],
    task_times: dict[int, int],
    likert: dict[int, int],
    sus: dict[int, int],
    comments: str,
) -> tuple[bool, str]:
    """
    Validate and persist survey. Returns (success, message).
    """
    name = (full_name or "").strip()
    if not name:
        return False, "Full name is required."
    email_value = (email or "").strip()
    if not email_value:
        return False, "Email is required."
    if not _valid_email(email_value):
        return False, "Enter a valid email address."
    if db.usability_email_exists(email_value):
        return False, f"Email '{email_value}' already submitted a response."

    sus_ratings = [sus[i] for i in range(1, 11)]
    try:
        sus_score = compute_sus_score(sus_ratings)
    except ValueError as exc:
        return False, str(exc)

    payload = {
        "participant_id": db.next_participant_code(),
        "full_name": name,
        "email": email_value,
        "phone": (phone or "").strip() or None,
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
    return True, f"Response saved (record #{record_id}). SUS score: {sus_score}/100"


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
            "Researchers: scroll up to download Word or JSON for the thesis."
        )
        if st.button("Submit another response", icon=material("feedback")):
            st.session_state["usability_submitted"] = False
            st.session_state["usability_submitting"] = False
            st.rerun()
        return

    is_submitting = st.session_state.get("usability_submitting", False)

    with st.form("usability_study_form", clear_on_submit=False):
        with st.container(border=True):
            _panel_header(
                "Participant",
                "Your contact details for the usability study.",
            )
            st.markdown(
                """
                <table class="survey-field-table">
                    <thead><tr>
                        <th>Field</th><th>Input</th><th>Required</th>
                    </tr></thead>
                    <tbody>
                        <tr><td>Full name</td><td>Text</td><td>Yes</td></tr>
                        <tr><td>Email</td><td>Text</td><td>Yes</td></tr>
                        <tr><td>Phone number</td><td>Text</td><td>No</td></tr>
                        <tr><td>Role</td><td>Dropdown</td><td>No</td></tr>
                    </tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )
            full_name = st.text_input(
                "Full name *",
                placeholder="e.g. Muhammad Salman",
                max_chars=80,
                disabled=is_submitting,
            )
            email = st.text_input(
                "Email *",
                placeholder="e.g. name@example.com",
                max_chars=120,
                disabled=is_submitting,
            )
            phone = st.text_input(
                "Phone number",
                placeholder="Optional",
                max_chars=30,
                disabled=is_submitting,
            )
            role = st.selectbox(
                "Your role",
                options=["Student", "Job seeker", "Recruiter / HR", "Academic reviewer", "Other"],
                disabled=is_submitting,
            )

        vertical_spacer(8)

        with st.container(border=True):
            _panel_header(
                "Task checklist",
                "Confirm each workflow step you completed in this session.",
                min_label=TIME_MIN,
                max_label=TIME_MAX,
            )
            st.markdown(
                """
                <table class="survey-field-table">
                    <thead><tr>
                        <th>Task</th><th>Completed</th><th>Time (minutes)</th>
                    </tr></thead>
                </table>
                """,
                unsafe_allow_html=True,
            )
            task_success: dict[int, bool] = {}
            task_times: dict[int, int] = {}
            for i, label in enumerate(TASK_LABELS, start=1):
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.caption(label)
                with c2:
                    task_success[i] = st.checkbox(
                        "Done",
                        value=True,
                        key=f"task_ok_{i}",
                        label_visibility="collapsed",
                        disabled=is_submitting,
                    )
                with c3:
                    selected_minutes = st.selectbox(
                        "Time (minutes)",
                        options=TIME_MINUTE_OPTIONS,
                        index=0,
                        key=f"task_min_{i}",
                        label_visibility="collapsed",
                        disabled=is_submitting,
                    )
                    task_times[i] = _parse_minutes(selected_minutes)

        vertical_spacer(8)

        with st.container(border=True):
            _panel_header(
                "Experience survey",
                "Rate your experience with the application.",
                min_label=LIKERT_MIN,
                max_label=LIKERT_MAX,
            )
            st.markdown(
                """
                <table class="survey-field-table">
                    <thead><tr>
                        <th>#</th><th>Statement</th><th>Rating (1–5)</th>
                    </tr></thead>
                </table>
                """,
                unsafe_allow_html=True,
            )
            likert: dict[int, int] = {}
            for i, question in enumerate(LIKERT_QUESTIONS, start=1):
                likert[i] = st.slider(
                    f"Q{i}. {question}",
                    1,
                    5,
                    3,
                    key=f"likert_{i}",
                    disabled=is_submitting,
                )

        vertical_spacer(8)

        with st.container(border=True):
            _panel_header(
                "System Usability Scale (SUS)",
                "Standard 10-item usability questionnaire (Brooke, 1996).",
                min_label=LIKERT_MIN,
                max_label=LIKERT_MAX,
            )
            st.markdown(
                """
                <table class="survey-field-table">
                    <thead><tr>
                        <th>#</th><th>Statement</th><th>Rating (1–5)</th>
                    </tr></thead>
                </table>
                """,
                unsafe_allow_html=True,
            )
            sus: dict[int, int] = {}
            for i, question in enumerate(SUS_QUESTIONS, start=1):
                sus[i] = st.slider(
                    f"{i}. {question}",
                    1,
                    5,
                    3,
                    key=f"sus_{i}",
                    disabled=is_submitting,
                )

        vertical_spacer(8)

        render_section("Optional comments", "Free text — suggestions or hardest step")
        comments = st.text_area(
            "Your comments",
            placeholder="What would you improve? Which step was hardest?",
            height=100,
            label_visibility="collapsed",
            disabled=is_submitting,
        )

        vertical_spacer(8)

        submit_label = "Saving response…" if is_submitting else "Submit usability response"
        submitted = st.form_submit_button(
            submit_label,
            type="primary",
            use_container_width=True,
            icon=material("check"),
            disabled=is_submitting,
        )

    if submitted and not is_submitting:
        st.session_state["usability_submitting"] = True
        with st.status("Submitting your response…", expanded=True) as status:
            status.update(label="Validating participant details…")
            ok, message = _save_usability_response(
                service,
                db,
                full_name=full_name,
                email=email,
                phone=phone,
                role=role,
                task_success=task_success,
                task_times=task_times,
                likert=likert,
                sus=sus,
                comments=comments,
            )
            if not ok:
                status.update(label="Validation failed", state="error")
                st.session_state["usability_submitting"] = False
                st.error(message)
                return
            status.update(label="Saving to database…")
            status.update(label="Complete!", state="complete")
        st.session_state["usability_submitting"] = False
        st.session_state["usability_submitted"] = True
        st.success(message)
        st.rerun()
