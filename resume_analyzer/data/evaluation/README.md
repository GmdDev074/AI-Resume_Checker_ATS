# Evaluation datasets (thesis)

## Files

| File | Samples | Description |
|------|---------|-------------|
| `kaggle_labeled_resumes.json` | **50** | Category-aligned skill excerpts (Kaggle Resume Dataset categories) |
| `skill_extraction_labels.json` | 5 | Original small benchmark |
| `all_labeled_resumes.json` | **55** | Merged (5 + 50) — **default for evaluation** |
| `latest_report.json` | — | Output from `scripts/run_evaluation.py` |

## Regenerate the 50-sample Kaggle-style set

```bash
python resume_analyzer/scripts/generate_kaggle_evaluation_set.py
```

Categories include: Python Developer, Data Science, DevOps Engineer, Java Developer, Web Designing, Android Developer, and 30+ more (mirroring popular Kaggle resume category labels).

## Import real Kaggle CSV (optional)

1. Download [Resume Dataset on Kaggle](https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset) (Snehaan Bhawal).
2. Place `Resume.csv` in:

   `resume_analyzer/data/evaluation/kaggle/Resume.csv`

3. Run:

```bash
python resume_analyzer/scripts/import_kaggle_csv.py
```

4. Point evaluation to the import file or merge into `all_labeled_resumes.json`.

## Run evaluation

```bash
python resume_analyzer/scripts/run_evaluation.py
pytest resume_analyzer/tests/test_evaluation.py
```

## Usability study (EV-04)

Collect responses in the app: **Usability Study** (unlocked after PDF report generation).

Export for thesis:

```bash
python resume_analyzer/scripts/export_usability_report.py
```

Output: `usability_responses.json` — see [docs/USABILITY_STUDY.md](../docs/USABILITY_STUDY.md).

## Label format

```json
{
  "id": "kaggle_eval_001",
  "source": "Kaggle Resume Dataset (category-aligned)",
  "category": "Python Developer",
  "text": "Technical Skills: Python, Django, ...",
  "expected_skills": ["Python", "Django", "..."]
}
```

## Thesis tip

For strongest marks, manually verify 10–20 rows in `kaggle_labeled_resumes.json` and note inter-annotator agreement in your evaluation chapter.
