# Project requirements & progress tracker

**Project:** AI-Powered Resume Analyzer and Job Matching System  
**Last updated:** 2025-06-06 *(change this date when you edit)*  
**Maintainer:** [GmdDev074](https://github.com/GmdDev074)

Use this file as the **single place to update** proposal compliance. Keep the [README](README.md) summary in sync when statuses change.

---

## How to update

1. Change the **Status** column using the legend below.
2. Edit **Notes / next step** with what you finished or still need.
3. Update **Last updated** at the top.
4. Refresh the [Progress summary](#progress-summary) counts (or run the checklist below).
5. Optionally copy key changes into [README — Requirements progress](README.md#requirements-progress).

### Status legend

| Icon | Meaning |
|------|---------|
| ✅ | **Achieved** — implemented and usable in the repo |
| 🟡 | **Partially achieved** — started but incomplete vs proposal |
| ⬜ | **Remaining** — not done or out of scope for code (thesis-only) |
| ➖ | **Not planned** — deliberate deviation (document in thesis) |

---

## Progress summary

| Category | ✅ | 🟡 | ⬜ | ➖ |
|----------|----|----|----|-----|
| Functional requirements | 10 | 0 | 0 | 0 |
| Technology & methodology | 5 | 1 | 0 | 3 |
| Data acquisition | 1 | 3 | 0 | 0 |
| Evaluation | 3 | 1 | 1 | 0 |
| Non-functional & ethics | 2 | 1 | 0 | 0 |
| **Totals** | **21** | **6** | **1** | **3** |

**Overall (proposal-mandatory items only, excluding ➖):** ~88% complete · **6** partial · **1** remaining  

*Recalculate when you edit tables: count rows per status.*

---

## 1. Functional requirements (proposal core)

| ID | Requirement (from proposal) | Status | Evidence / location | Notes / next step |
|----|----------------------------|--------|---------------------|-------------------|
| FR-01 | Upload PDF resume | ✅ | `ui/pages/resume_upload.py`, `services/pdf/` | Multi-file upload supported |
| FR-02 | Provide job description | ✅ | Upload page + `data/sample_job_descriptions.json` | Templates + free text |
| FR-03 | Extract **skills** | ✅ | `services/extraction/skill_extractor.py` | JSON ontology + regex; spaCy optional |
| FR-04 | Extract **experience** | ✅ | `services/extraction/experience_extractor.py` | Heuristic years + sections |
| FR-05 | Extract **education** | ✅ | `services/extraction/education_extractor.py` | Degree/institution patterns |
| FR-06 | **ATS compatibility** score | ✅ | `services/ats/ats_scoring_service.py` | Weighted 0–100 + grade |
| FR-07 | **Skill gap** identification | ✅ | `job_matching_service.py`, Analysis UI | Matched vs missing lists + chart |
| FR-08 | **Personalized improvement** suggestions | ✅ | `services/recommendation/` | ATS + career tips |
| FR-09 | **Streamlit** web application | ✅ | `app.py`, `ui/pages/*` | Dashboard, Upload, Analysis, Reports |
| FR-10 | Reduce manual screening; help seekers & recruiters | ✅ | Ranking, history, reports | Describe user study in thesis chapter |

---

## 2. Technology & methodology

| ID | Proposal item | Status | Implemented as | Notes / next step |
|----|---------------|--------|----------------|-------------------|
| TM-01 | Python | ✅ | Whole project | 3.12+ |
| TM-02 | PyMuPDF / PyPDF2 | ✅ | **PyMuPDF** (`fitz`) | PyPDF2 not required |
| TM-03 | spaCy for NLP | 🟡 | Optional `en_core_web_sm` | Works without; install for bonus NLP |
| TM-04 | Gemini API | ➖ | Not used | **Local / free** design; cite in thesis |
| TM-05 | scikit-learn (matching/scoring) | ✅ | `similarity_service.py` | Cosine similarity |
| TM-06 | Streamlit UI | ✅ | `app.py` | Light theme |
| TM-07 | LSA (Tian et al. baseline) | ➖ | Not implemented | Compare via **keyword baseline** instead |
| TM-08 | BERT + SVM (Tian et al.) | ➖ | Not implemented | Use **MiniLM embeddings** + cosine |
| TM-09 | Semantic embeddings (enhancement) | ✅ | `all-MiniLM-L6-v2` | Document as modern alternative to LSA+SVM |

---

## 3. Data acquisition

| ID | Proposal item | Status | Evidence | Notes / next step |
|----|---------------|--------|----------|-------------------|
| DA-01 | Kaggle resume dataset (Snehaan Bhawal) | 🟡 | `scripts/import_kaggle_csv.py`, `data/evaluation/kaggle/` | Download CSV → import; not bundled in repo |
| DA-02 | Hugging Face job description datasets | 🟡 | `sample_job_descriptions.json` only | Add HF dataset pull or more JD samples |
| DA-03 | Custom skill knowledge base | ✅ | `data/skills_database.json` | Search on Dashboard |
| DA-04 | Large-scale labeled training data | 🟡 | 55 labeled samples in `data/evaluation/` | Expand labels; verify 10–20 rows manually |
| DA-05 | Synthetic / category-aligned eval set | ✅ | `kaggle_labeled_resumes.json` (50) | Regenerate via `generate_kaggle_evaluation_set.py` |

---

## 4. Evaluation (methodology)

| ID | Proposal item | Status | How to run / where | Notes / next step |
|----|---------------|--------|-------------------|-------------------|
| EV-01 | Skill extraction accuracy | ✅ | `scripts/run_evaluation.py` | See `latest_report.json` (e.g. F1 ~0.99 on 55 samples) |
| EV-02 | Cosine similarity for job match | ✅ | Analysis pipeline | Shown as semantic similarity % |
| EV-03 | Baseline **keyword** matching comparison | ✅ | `baseline_matcher.py`, Analysis UI | Hybrid vs keyword baseline |
| EV-04 | **User testing** (usability) | ✅ | `ui/pages/usability_page.py`, `docs/USABILITY_STUDY.md` | In-app SUS + Likert survey; JSON + Word export via app or `export_usability_report.py` |
| EV-05 | Comparison with Tian / ResumeAtlas metrics | ⬜ | Discussion section | Qualitative comparison; no full replication |

**Latest automated metrics** (`resume_analyzer/data/evaluation/latest_report.json`):

| Metric | Value |
|--------|-------|
| Skill extraction F1 | ~0.992 (55 samples) |
| Skill extraction precision | ~0.986 |
| Skill extraction recall | ~0.997 |

*Re-run `python resume_analyzer/scripts/run_evaluation.py` after label changes and paste new numbers here.*

---

## 5. Non-functional & ethical requirements

| ID | Requirement | Status | Evidence | Notes / next step |
|----|-------------|--------|----------|-------------------|
| NF-01 | No additional hardware | ✅ | Local CPU/RAM only | 4 GB+ RAM for embeddings |
| NF-02 | Ethical AI (bias reduction) | 🟡 | `docs/ETHICAL_AI.md` | Add fairness audit or diverse test set in thesis |
| NF-03 | No paid third-party APIs | ✅ | Local models | Mention in methodology |
| NF-04 | Proprietary / permission-based use | ✅ | `LICENSE` | All rights reserved |

---

## 6. Delivered beyond original proposal (bonus)

| ID | Feature | Status | Location |
|----|---------|--------|----------|
| EX-01 | Multi-resume comparison & ranking | ✅ | `analysis_page.py`, pipeline |
| EX-02 | PDF report export | ✅ | `services/report/` |
| EX-03 | SQLite analysis history | ✅ | `services/storage/` |
| EX-04 | Optional FastAPI REST API | ✅ | `api/main.py` |
| EX-05 | Dashboard analytics | ✅ | `ui/pages/dashboard.py` |
| EX-06 | pytest test suite | ✅ | `tests/` |
| EX-07 | In-app usability study (SUS + Likert) | ✅ | `usability_page.py`, `usability_service.py` | Gated until PDF report; exports JSON + Word with question text |

---

## 7. Remaining work (priority order)

Use this checklist for thesis completion:

- [x] **EV-04** — Collect 5–10 usability responses in app; export via `export_usability_report.py`; add results table to thesis  
- [ ] **DA-01** — Import full Kaggle `Resume.csv` and document dataset size in methodology  
- [ ] **DA-02** — Add more job descriptions (HF or manual) for domain diversity  
- [ ] **DA-04** — Grow labeled set (target: 100+ verified samples) and re-run evaluation  
- [ ] **NF-02** — Write bias/limitations subsection with English-only and ontology bias examples  
- [ ] **EV-05** — Related-work table: JayaPriya vs Tian vs ResumeAtlas vs **this system**  

### Partial items to close (optional → ✅)

- [ ] **TM-03** — Document spaCy install step in thesis appendix; show with/without comparison  
- [ ] **DA-01** — Mark ✅ when Kaggle CSV imported and cited in report  

---

## 8. Related documents

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Setup, run, stack, clone |
| [resume_analyzer/docs/THESIS_ALIGNMENT.md](resume_analyzer/docs/THESIS_ALIGNMENT.md) | Academic wording & deviations |
| [resume_analyzer/docs/ETHICAL_AI.md](resume_analyzer/docs/ETHICAL_AI.md) | Ethics section |
| [resume_analyzer/data/evaluation/README.md](resume_analyzer/data/evaluation/README.md) | Datasets & evaluation commands |

---

*Template: copy a row to add new requirements. Keep IDs stable (FR-11, EV-06) for thesis traceability.*
