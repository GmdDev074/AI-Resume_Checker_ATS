# Database Schema (SQLite)

Database file: `resume_analyzer/resume_analyzer.db`

## Table: `users`

| Column     | Type    | Constraints              |
|------------|---------|--------------------------|
| id         | INTEGER | PRIMARY KEY AUTOINCREMENT|
| name       | TEXT    |                          |
| email      | TEXT    | UNIQUE                   |
| created_at | TEXT    | NOT NULL                 |

## Table: `analysis_history`

| Column              | Type    | Constraints                          |
|---------------------|---------|--------------------------------------|
| id                  | INTEGER | PRIMARY KEY AUTOINCREMENT            |
| user_id             | INTEGER | FOREIGN KEY → users(id)              |
| resume_name         | TEXT    | NOT NULL                             |
| job_title           | TEXT    |                                      |
| resume_text         | TEXT    |                                      |
| job_description     | TEXT    |                                      |
| ats_score           | REAL    |                                      |
| match_score         | REAL    |                                      |
| skills_json         | TEXT    | JSON array of skills                 |
| missing_skills_json | TEXT    | JSON array of missing skills         |
| analysis_json       | TEXT    | Full analysis payload (JSON)       |
| created_at          | TEXT    | NOT NULL                             |

## Table: `reports`

| Column      | Type    | Constraints                              |
|-------------|---------|------------------------------------------|
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT                |
| analysis_id | INTEGER | NOT NULL, FOREIGN KEY → analysis_history |
| file_path   | TEXT    | NOT NULL                                 |
| created_at  | TEXT    | NOT NULL                                 |

## Relationships

- `users` 1 — N `analysis_history`
- `analysis_history` 1 — N `reports`
