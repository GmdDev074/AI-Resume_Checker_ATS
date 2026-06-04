# AI-Powered Resume Analyzer and Job Matching System

**Final Year Project** — A production-quality, modular resume analysis platform that scores ATS compatibility, calculates job match scores, detects skill gaps, and exports PDF reports. No paid APIs required.

## Features

- PDF resume upload (PyMuPDF) with corruption handling
- Job description matching via Sentence Transformers + skill overlap
- ATS scoring (skills, experience, education, completeness, formatting)
- Missing skill detection and learning recommendations
- Interactive Streamlit dashboard with professional light theme
- Resume history, multi-resume comparison, and candidate ranking
- Searchable skill database
- PDF report export (ReportLab)
- Optional FastAPI REST layer
- SQLite persistence

## Tech Stack

| Layer | Tools |
|-------|-------|
| UI | Streamlit |
| API | FastAPI (optional) |
| PDF | PyMuPDF, ReportLab |
| NLP | spaCy, Sentence Transformers (`all-MiniLM-L6-v2`) |
| ML | scikit-learn, NumPy, Pandas |
| Charts | Plotly, Matplotlib |
| Database | SQLite |

## Project Structure

```
resume_analyzer/
├── app.py                 # Streamlit entry point
├── config/                # Settings and constants
├── data/                  # Skills DB, samples
├── models/                # Dataclasses
├── services/              # Business logic (Clean Architecture)
├── ui/                    # Streamlit pages & components
├── utils/                 # Helpers
├── tests/                 # Unit tests
├── api/                   # Optional FastAPI
└── docs/                  # Database schema
```

## Installation

### 1. Prerequisites

- Python 3.12+
- 4 GB+ RAM recommended (embedding model download ~90 MB on first run)

### 2. Create virtual environment

```bash
cd ResumeChecker
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r resume_analyzer/requirements.txt
python -m spacy download en_core_web_sm
```

> **Note:** The app works without spaCy or Sentence Transformers by falling back to regex and hash embeddings, but full accuracy requires both.

## Running the Application

### Streamlit UI

From the project root (`ResumeChecker`):

```bash
streamlit run resume_analyzer/app.py
```

### Optional FastAPI

```bash
uvicorn resume_analyzer.api.main:app --reload
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "job_description=Python FastAPI Docker" \
  -F "file=@resume.pdf"
```

## Usage Workflow

1. **Upload Resume** — Upload PDF(s) or use the built-in sample text resume.
2. **Job Description** — Paste text or pick a sample job from the dropdown.
3. **Analysis** — Click *Run Analysis* to view ATS score, match %, charts, and recommendations.
4. **Reports** — Generate and download a PDF report; view history in the database.

## Scoring Model

### ATS Score (0–100)

| Factor | Weight |
|--------|--------|
| Skills match | 40 |
| Experience | 25 |
| Education | 15 |
| Resume completeness | 10 |
| Formatting | 10 |

### Job Match Score

Combined score: **60%** skill overlap + **40%** semantic cosine similarity (scikit-learn cosine on Sentence Transformer embeddings).

**Keyword baseline** (thesis comparison): exact skill overlap only — shown on the Analysis page as *Keyword baseline*.

## Thesis alignment and evaluation

| Document | Purpose |
|----------|---------|
| [docs/THESIS_ALIGNMENT.md](docs/THESIS_ALIGNMENT.md) | Proposal vs implementation mapping |
| [docs/ETHICAL_AI.md](docs/ETHICAL_AI.md) | Bias and fair-use guidelines |

Run benchmarks (precision/recall/F1 + baseline comparison):

```bash
python resume_analyzer/scripts/run_evaluation.py
```

Output: `data/evaluation/latest_report.json`

| Dataset | Path | Count |
|---------|------|-------|
| Kaggle-style labeled resumes | `data/evaluation/kaggle_labeled_resumes.json` | **50** |
| Full evaluation set (default) | `data/evaluation/all_labeled_resumes.json` | **55** |

Regenerate: `python resume_analyzer/scripts/generate_kaggle_evaluation_set.py`  
Import real Kaggle CSV: see `data/evaluation/README.md`

## Database

See [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for table definitions (`users`, `analysis_history`, `reports`).

## Testing

```bash
pytest
```

## Sample Data

- `data/skills_database.json` — Searchable technical skills
- `data/sample_job_descriptions.json` — Five sample JDs
- `data/sample_resumes/` — Text resumes for testing without PDFs

## Extending the Project

| Task | Module to edit |
|------|----------------|
| Add skills | `data/skills_database.json` |
| Change ATS weights | `config/constants.py` |
| New extraction rule | `services/extraction/` |
| UI page | `ui/pages/` |
| New chart | `ui/components/charts.py` |

## Architecture Principles

1. **UI** only calls `ResumePipeline` and `DatabaseService`
2. **Services** are single-responsibility and under 300 lines
3. **Models** use dataclasses for clear data flow
4. Type hints and docstrings on all public functions

## License

Educational use — Final Year Project template for students.

## Authors

Built as a modular Final Year Project template for computer science students.
