# Usability study (EV-04)

In-app usability evaluation for the **AI-Powered Resume Analyzer and Job Matching System**.

## When the survey unlocks

The **Usability Study** navigation item appears only after the participant completes the full workflow:

1. Upload resume (PDF or sample)
2. Enter job description
3. Run analysis
4. Review results (skill gaps / recommendations)
5. **Generate a PDF report** on the Reports page

This ensures feedback is collected from users who experienced the complete system.

## Protocol

| Item | Detail |
|------|--------|
| **Participants** | Target 5–10 (classmates, job seekers, reviewers) |
| **Environment** | Local Streamlit or deployed Streamlit Cloud URL |
| **ID** | Auto-assigned study code (`P01`, `P02`, …) plus name, email, optional phone |
| **Duration** | ~15–20 minutes including tasks + survey |
| **Instruments** | Task checklist, 6 Likert items, standard 10-item SUS |

## Tasks

| ID | Task | Success criterion |
|----|------|-----------------|
| T1 | Upload resume | File parsed without error |
| T2 | Job description | JD saved and linked to session |
| T3 | Run analysis | ATS and match scores displayed |
| T4 | Skill gaps | User can name ≥1 missing skill from UI |
| T5 | PDF report | Report generated and downloadable |

## Collecting responses

1. Ask participant to complete the workflow through **Generate PDF report**.
2. Open **Usability Study** in the sidebar.
3. Participant fills the form and submits.
4. Repeat with a new participant ID.

## Download responses for thesis (student / researcher)

Responses are saved in SQLite (`usability_responses` table). Use **any** of these methods:

### Method 1 — In the app (easiest)

1. Open **Usability Study** (after you have unlocked it once via the workflow).
2. At the **top of the page**, see the researcher banner with response count and mean SUS.
3. Click **Download Microsoft Word (.docx)** — recommended for thesis:
   - Summary metrics (n, mean SUS)
   - Per-participant tables with **full question text** (tasks, Likert, SUS)
   - Aggregate task success rates, Likert means, SUS by participant
   - Optional comments section
4. Optional: **Download JSON** (full structured data + aggregates)

### Method 2 — Command line (local project)

```bash
python resume_analyzer/scripts/export_usability_report.py
```

Writes:

- `resume_analyzer/data/evaluation/usability_responses.json`
- `resume_analyzer/data/evaluation/usability_study_thesis.docx`
- Prints task success %, mean Likert, mean SUS in the terminal

### Method 3 — Database file (local only)

Copy `resume_analyzer/resume_analyzer.db` and open with [DB Browser for SQLite](https://sqlitebrowser.org/) → table `usability_responses` → Export to CSV.

### Streamlit Cloud note

On deployed Streamlit, use **Method 1 (in-app download)** before the app reboots, or download the DB if you have server file access. Cloud instances may reset storage on redeploy — export Word or JSON after each testing session.

### What to put in the thesis

| Source | Use for |
|--------|---------|
| Word (.docx) export | Ready-made thesis tables (participants, tasks, Likert, SUS) |
| JSON `mean_sus` | Aggregate usability score |
| JSON `task_success_rates_pct` | Task completion table |
| JSON `mean_likert` | Satisfaction subscales |
| Terminal output from export script | Quick copy-paste summary |

Copy summary tables into your thesis **Evaluation** chapter.

## Results template (fill after data collection)

| Participant | Role | T1–T5 OK | SUS | Notes |
|-------------|------|----------|-----|-------|
| P01 | Student | 5/5 | — | |
| P02 | Job seeker | — | — | |

**Aggregate (after export):**

| Metric | Value |
|--------|-------|
| n | |
| Mean SUS | |
| Mean task success | |
| Mean Likert (layout) | |

## Ethics

- Collect name and email with participant consent; phone is optional
- No hiring decisions automated — see [ETHICAL_AI.md](ETHICAL_AI.md)
- Inform participants that data is for academic evaluation

## Related

- [PROJECT_STATUS.md](../../PROJECT_STATUS.md) — requirement EV-04
- [THESIS_ALIGNMENT.md](THESIS_ALIGNMENT.md) — evaluation mapping
