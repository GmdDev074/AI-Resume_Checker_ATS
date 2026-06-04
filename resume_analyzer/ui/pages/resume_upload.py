"""Resume upload and job description entry page."""

import streamlit as st

from resume_analyzer.config.settings import get_settings
from resume_analyzer.services.resume_pipeline import ResumePipeline
from resume_analyzer.services.storage.database_service import DatabaseService
from resume_analyzer.ui.components.layout import render_empty_state, render_page_header, render_section
from resume_analyzer.ui.icons import material
from resume_analyzer.utils.file_utils import read_json
from resume_analyzer.utils.validators import validate_job_description, validate_pdf_size


def render_resume_upload(pipeline: ResumePipeline, db: DatabaseService) -> None:
    """
    Render upload form and store session state.

    Args:
        pipeline: Resume processing pipeline.
        db: Database service.
    """
    render_page_header(
        "Upload & configure",
        "Provide the job description and candidate resume(s) for analysis.",
        "upload_file",
    )

    settings = get_settings()
    sample_jobs = read_json(settings.sample_jobs_path) if settings.sample_jobs_path.exists() else []

    col_job, col_resume = st.columns(2, gap="large")

    with col_job:
        render_section("Job description")
        job_options = ["Custom description"] + [j["title"] for j in sample_jobs]
        selected_job = st.selectbox("Template", job_options, label_visibility="collapsed")

        default_job_text = ""
        job_title = "Target Position"
        if selected_job != "Custom description" and sample_jobs:
            idx = job_options.index(selected_job) - 1
            default_job_text = sample_jobs[idx]["description"]
            job_title = sample_jobs[idx]["title"]

        job_text = st.text_area(
            "Job description text",
            value=default_job_text,
            height=220,
            placeholder="Paste the complete job description including required skills and experience.",
            label_visibility="collapsed",
        )

    with col_resume:
        render_section("Resume document(s)")
        uploaded_files = st.file_uploader(
            "PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        use_sample = st.toggle("Use sample resume (development / demo)", value=False)
        if use_sample:
            sample_path = settings.sample_resumes_dir / "sample_resume_01.txt"
            if sample_path.exists():
                st.session_state["sample_text"] = sample_path.read_text(encoding="utf-8")
                st.caption("Sample resume loaded successfully.")

    st.markdown("")
    parse_col, _ = st.columns([1, 2])
    with parse_col:
        run_parse = st.button(
            "Parse documents and continue",
            type="primary",
            use_container_width=True,
            icon=material("play"),
        )

    if run_parse:
        valid, err = validate_job_description(job_text)
        if not valid:
            st.error(err)
            return

        resumes = []
        if use_sample and st.session_state.get("sample_text"):
            resumes.append(
                pipeline.parse_resume(
                    st.session_state["sample_text"],
                    file_name="sample_resume_01.txt",
                    is_text=True,
                )
            )
        elif uploaded_files:
            for uploaded in uploaded_files:
                data = uploaded.read()
                ok, msg = validate_pdf_size(len(data), settings.max_upload_mb)
                if not ok:
                    st.error(f"{uploaded.name}: {msg}")
                    continue
                try:
                    resumes.append(pipeline.parse_resume(data, file_name=uploaded.name))
                except ValueError as exc:
                    st.error(f"{uploaded.name}: {exc}")
        else:
            st.warning("Please upload a PDF or enable the sample resume.")
            return

        if not resumes:
            return

        job = pipeline.build_job(job_text, title=job_title)
        st.session_state["resumes"] = resumes
        st.session_state["job"] = job
        st.session_state["job_text"] = job.raw_text
        st.success(
            f"Successfully parsed {len(resumes)} document(s). "
            "Proceed to **Analysis** in the navigation menu."
        )

    if st.session_state.get("resumes"):
        render_section("Extraction preview")
        for r in st.session_state["resumes"]:
            with st.expander(r.file_name or "Resume", expanded=False):
                m1, m2, m3 = st.columns(3)
                m1.metric("Skills detected", r.skills_count)
                m2.metric("Experience", f"{r.total_experience_years} yrs")
                m3.metric("Email on file", "Yes" if r.contact.email else "No")
                if r.skills:
                    chips = "".join(
                        f'<span class="skill-chip skill-chip-match">{s}</span>'
                        for s in r.skills[:15]
                    )
                    st.markdown(
                        f'<div class="skill-tags-wrap">{chips}</div>',
                        unsafe_allow_html=True,
                    )
    else:
        render_empty_state(
            "Upload materials and select **Parse documents and continue** to begin.",
            "",
        )
