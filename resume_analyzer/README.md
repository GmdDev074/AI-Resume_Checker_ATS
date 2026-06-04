# Resume Analyzer package

This folder contains the full application. **Start with the [root README](../README.md)** for purpose, achievements, clone/run instructions, stack, models, troubleshooting, and repository structure.

**License:** Proprietary — see [LICENSE](../LICENSE). Use requires permission from the copyright holder.

**Requirements progress:** [PROJECT_STATUS.md](../PROJECT_STATUS.md)

## Quick run

From the repository root:

```bash
pip install -r resume_analyzer/requirements.txt
python -m spacy download en_core_web_sm
streamlit run resume_analyzer/app.py
```

## Entry points

| File | Command |
|------|---------|
| Streamlit UI | `streamlit run resume_analyzer/app.py` |
| FastAPI | `uvicorn resume_analyzer.api.main:app --reload` |
| Evaluation | `python resume_analyzer/scripts/run_evaluation.py` |
| Tests | `pytest` |

## Key modules

| Path | Responsibility |
|------|----------------|
| `app.py` | Streamlit routing and session state |
| `services/resume_pipeline.py` | Orchestrates parse → extract → score → recommend |
| `services/matching/embedding_service.py` | Loads `all-MiniLM-L6-v2` |
| `services/matching/similarity_service.py` | scikit-learn cosine similarity |
| `services/ats/ats_scoring_service.py` | Weighted ATS score |
| `ui/pages/` | Dashboard, Upload, Analysis, Reports |

## Documentation

- [THESIS_ALIGNMENT.md](docs/THESIS_ALIGNMENT.md)
- [ETHICAL_AI.md](docs/ETHICAL_AI.md)
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)
- [data/evaluation/README.md](data/evaluation/README.md)
