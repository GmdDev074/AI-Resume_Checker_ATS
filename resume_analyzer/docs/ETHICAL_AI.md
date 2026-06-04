# Ethical AI Considerations

This project supports recruitment **decision support**, not automated hiring decisions.

## Design principles

1. **Transparency** — ATS breakdown (skills, experience, education, completeness, formatting) is visible to the user.
2. **Human in the loop** — Scores and recommendations assist recruiters and candidates; they do not replace interviews or judgment.
3. **No protected attributes** — The system does not extract or score gender, age, ethnicity, or religion.
4. **Local processing** — No paid third-party APIs; resume text stays on the user’s machine unless they choose to deploy remotely.
5. **Bias awareness** — Keyword and ontology bias may favor Western job titles and English resumes. Users should validate on diverse samples.

## Limitations to disclose in thesis

- Skill list bias from `skills_database.json`
- English-centric parsing and section heuristics
- Semantic models may reflect training data biases from Hugging Face models
- Small evaluation set unless extended with Kaggle data

## Recommendations for fair use

- Use scores as one signal among many
- Audit missing-skill suggestions for unrealistic requirements
- Allow candidates to refine resumes based on feedback, not as sole rejection criterion
