# Thesis Proposal vs Implementation Alignment

This document maps the **written proposal** to the **implemented system** for academic reporting.

## Abstract and objectives — Aligned

| Objective | Implementation |
|-----------|----------------|
| Upload PDF resume + job description | `services/pdf/pdf_parser.py`, `ui/pages/resume_upload.py` |
| Extract skills, experience, education | `services/extraction/*` |
| ATS compatibility score | `services/ats/ats_scoring_service.py` |
| Skill gaps | `services/matching/job_matching_service.py` |
| Improvement suggestions | `services/recommendation/recommendation_service.py` |
| Streamlit web application | `app.py`, `ui/pages/*` |
| Reduce manual screening time | Multi-resume ranking, history, PDF reports |

## Methodology — Implemented with documented deviations

### Technologies

| Proposal | Implemented |
|----------|-------------|
| Python | Yes |
| PyMuPDF / PyPDF2 | **PyMuPDF** (`fitz`) |
| spaCy or Gemini API | **spaCy** (optional); skills via **regex + JSON database**; **no Gemini** |
| scikit-learn | **Yes** — `sklearn.metrics.pairwise.cosine_similarity` in `similarity_service.py` |
| Streamlit | Yes |
| BERT + SVM + LSA (Tian et al.) | **Not used.** **Sentence Transformers** (`all-MiniLM-L6-v2`, BERT-family embeddings) + cosine similarity |
| LSA | Not implemented |

### Data acquisition

| Proposal | Implemented |
|----------|-------------|
| Kaggle resume datasets | **Not integrated** — use samples + optional manual import |
| Hugging Face job datasets | Sample JDs in `data/sample_job_descriptions.json` |
| Custom skill knowledge base | `data/skills_database.json` |
| Evaluation labels | `data/evaluation/kaggle_labeled_resumes.json` (**50** samples), `all_labeled_resumes.json` (**55** merged) |

**Completed:** 50 category-aligned labeled resumes (Kaggle Resume Dataset categories). Optional: import raw CSV via `scripts/import_kaggle_csv.py`.

### Evaluation — Now supported in code

| Metric | How to run |
|--------|------------|
| Skill extraction precision/recall/F1 | `python resume_analyzer/scripts/run_evaluation.py` |
| Cosine similarity (semantic match) | Automatic during analysis |
| Keyword baseline comparison | `keyword_baseline_score` on each analysis; evaluation script |
| Usability testing | Document in thesis (questionnaire / task completion) — not automated |

Output: `data/evaluation/latest_report.json`

## Literature review — How to cite your build

- **JayaPriya et al. (2025)** — Similar end-to-end resume analyzer; cite as related work.
- **Tian et al. (2023)** — LSA + BERT + SVM; cite as **baseline approach** your keyword + embedding hybrid improves upon.
- **Heakl et al. (2024) ResumeAtlas** — Large-scale classification; cite for scale and LLM trends; your project is lightweight and local.

## Ethical AI

See [ETHICAL_AI.md](ETHICAL_AI.md). The system uses transparent rule-based ATS weights and does not automate hiring decisions.

## Suggested thesis wording (Methodology paragraph)

> The system extracts skills using a curated ontology and pattern matching, computes ATS scores via weighted heuristics, and measures job fit using Sentence Transformer embeddings (MiniLM) with scikit-learn cosine similarity. A keyword-only baseline (exact skill overlap) is retained for comparison with traditional ATS methods. Evaluation uses labeled skill samples and reports precision, recall, and F1, with optional expansion to public resume corpora.
