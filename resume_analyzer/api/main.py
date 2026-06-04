"""
Optional FastAPI layer for programmatic resume analysis.
Run: uvicorn resume_analyzer.api.main:app --reload
"""

import sys
from pathlib import Path
from typing import List, Optional

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from resume_analyzer.services.resume_pipeline import ResumePipeline
from resume_analyzer.services.storage.database_service import DatabaseService

app = FastAPI(
    title="Resume Analyzer API",
    description="AI-Powered Resume Analyzer and Job Matching System",
    version="1.0.0",
)
pipeline = ResumePipeline()
db = DatabaseService()


class AnalysisResponse(BaseModel):
    """API response model for analysis."""

    ats_score: float
    ats_grade: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    job_description: str = Form(...),
    file: UploadFile = File(...),
    job_title: Optional[str] = Form(None),
) -> AnalysisResponse:
    """
    Analyze uploaded resume PDF against job description.

    Args:
        job_description: Job description text.
        file: Resume PDF file.
        job_title: Optional job title.

    Returns:
        Analysis scores and skill breakdown.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF file required.")
    data = await file.read()
    try:
        resume = pipeline.parse_resume(data, file_name=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = pipeline.build_job(job_description, title=job_title)
    result = pipeline.analyze(resume, job)
    db.save_analysis(
        resume_name=file.filename,
        job_title=job.title or "Job",
        resume_text=resume.raw_text,
        job_description=job.raw_text,
        analysis=result,
        skills=resume.skills,
    )
    return AnalysisResponse(
        ats_score=result.ats.ats_score,
        ats_grade=result.ats.grade,
        match_score=result.match.match_score,
        matched_skills=result.match.matched_skills,
        missing_skills=result.match.missing_skills,
        recommendations=result.recommendations,
    )
