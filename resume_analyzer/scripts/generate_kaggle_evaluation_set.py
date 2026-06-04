"""
Generate 50 labeled resume skill samples aligned with Kaggle Resume Dataset categories.

Inspired by: Resume Dataset (Snehaan Bhawal) — category-based resume corpus.
Run: python resume_analyzer/scripts/generate_kaggle_evaluation_set.py
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Category → (skill line text, expected skills) — mirrors common Kaggle resume categories
KAGGLE_STYLE_SAMPLES: list[dict] = [
    {
        "category": "Python Developer",
        "text": "Technical Skills: Python, Django, Flask, FastAPI, REST, PostgreSQL, Git, Docker, Linux, Agile",
        "expected_skills": ["Python", "Django", "Flask", "FastAPI", "REST", "PostgreSQL", "Git", "Docker", "Linux", "Agile"],
    },
    {
        "category": "Python Developer",
        "text": "Skills — Python, Pandas, NumPy, SQL, SQLite, unit testing, GitHub Actions, CI/CD",
        "expected_skills": ["Python", "Pandas", "NumPy", "SQL", "SQLite", "GitHub Actions", "CI/CD"],
    },
    {
        "category": "Java Developer",
        "text": "Core competencies: Java, Spring Boot, Microservices, REST, MySQL, Maven, Git, Jenkins",
        "expected_skills": ["Java", "Spring Boot", "Microservices", "REST", "MySQL", "Git", "Jenkins"],
    },
    {
        "category": "Java Developer",
        "text": "Proficient in Java, Kotlin, Android SDK, MVVM, Firebase, SQLite, Git",
        "expected_skills": ["Java", "Kotlin", "Android SDK", "MVVM", "Firebase", "SQLite", "Git"],
    },
    {
        "category": "Data Science",
        "text": "Skills: Python, R, Machine Learning, Deep Learning, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy",
        "expected_skills": ["Python", "R", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy"],
    },
    {
        "category": "Data Science",
        "text": "Tools — Jupyter, Python, NLP, Computer Vision, SQL, PostgreSQL, Git, Agile",
        "expected_skills": ["Python", "NLP", "Computer Vision", "SQL", "PostgreSQL", "Git", "Agile"],
    },
    {
        "category": "Data Science",
        "text": "Expertise in Python, Statistics, Machine Learning, Pandas, NumPy, Matplotlib, SQL",
        "expected_skills": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"],
    },
    {
        "category": "Web Designing",
        "text": "HTML, CSS, JavaScript, React, Responsive Design, Figma, Git, REST APIs",
        "expected_skills": ["HTML", "CSS", "JavaScript", "React", "Figma", "Git", "REST"],
    },
    {
        "category": "Web Designing",
        "text": "Frontend: React, TypeScript, Next.js, Tailwind, Node.js, Express.js, MongoDB",
        "expected_skills": ["React", "TypeScript", "Next.js", "Node.js", "Express.js", "MongoDB"],
    },
    {
        "category": "Web Designing",
        "text": "Vue.js, JavaScript, HTML, CSS, Webpack, Git, Agile, Scrum",
        "expected_skills": ["Vue.js", "JavaScript", "HTML", "CSS", "Git", "Agile", "Scrum"],
    },
    {
        "category": "DevOps Engineer",
        "text": "DevOps, Docker, Kubernetes, Terraform, Ansible, Linux, Jenkins, GitHub Actions, AWS",
        "expected_skills": ["DevOps", "Docker", "Kubernetes", "Terraform", "Ansible", "Linux", "Jenkins", "GitHub Actions", "AWS"],
    },
    {
        "category": "DevOps Engineer",
        "text": "CI/CD pipelines, Docker, Kubernetes, Python, Bash, GCP, Monitoring, Git",
        "expected_skills": ["CI/CD", "Docker", "Kubernetes", "Python", "GCP", "Git"],
    },
    {
        "category": "DevOps Engineer",
        "text": "Cloud: AWS, Azure; Tools: Docker, Linux, Nginx, PostgreSQL, Terraform",
        "expected_skills": ["AWS", "Azure", "Docker", "Linux", "Nginx", "PostgreSQL", "Terraform"],
    },
    {
        "category": "Android Developer",
        "text": "Kotlin, Android SDK, Java, MVVM, Retrofit, REST, Firebase, Git",
        "expected_skills": ["Kotlin", "Android SDK", "Java", "MVVM", "REST", "Firebase", "Git"],
    },
    {
        "category": "Android Developer",
        "text": "Mobile development with Kotlin, Flutter, Dart, Firebase, SQLite, Agile",
        "expected_skills": ["Kotlin", "Flutter", "Dart", "Firebase", "SQLite", "Agile"],
    },
    {
        "category": "DotNet Developer",
        "text": "C#, .NET, ASP.NET, SQL Server, REST, Azure, Git, Agile",
        "expected_skills": ["C#", ".NET", "SQL", "REST", "Azure", "Git", "Agile"],
    },
    {
        "category": "Blockchain",
        "text": "Solidity, Ethereum, Smart Contracts, JavaScript, Node.js, Git, REST",
        "expected_skills": ["JavaScript", "Node.js", "Git", "REST"],
    },
    {
        "category": "Database",
        "text": "PostgreSQL, MySQL, MongoDB, SQL, Redis, Database Design, Linux",
        "expected_skills": ["PostgreSQL", "MySQL", "MongoDB", "SQL", "Redis", "Linux"],
    },
    {
        "category": "Database",
        "text": "SQL, PL/SQL, Oracle, MySQL, ETL concepts, Python, Pandas",
        "expected_skills": ["SQL", "MySQL", "Python", "Pandas"],
    },
    {
        "category": "ETL Developer",
        "text": "Python, SQL, PostgreSQL, ETL, Pandas, Apache, Linux, Git",
        "expected_skills": ["Python", "SQL", "PostgreSQL", "Pandas", "Apache", "Linux", "Git"],
    },
    {
        "category": "Hadoop",
        "text": "Hadoop ecosystem, Python, SQL, Linux, Spark knowledge, Java, Git",
        "expected_skills": ["Python", "SQL", "Linux", "Java", "Git"],
    },
    {
        "category": "Automation Testing",
        "text": "Selenium, Java, Python, Test Automation, Jenkins, Git, Agile, REST",
        "expected_skills": ["Java", "Python", "Jenkins", "Git", "Agile", "REST"],
    },
    {
        "category": "Automation Testing",
        "text": "QA Automation, Postman, API testing, JavaScript, Node.js, CI/CD, Git",
        "expected_skills": ["Postman", "JavaScript", "Node.js", "CI/CD", "Git"],
    },
    {
        "category": "Network Security Engineer",
        "text": "Linux, Networking, Security, Python, Firewall, VPN, Git",
        "expected_skills": ["Linux", "Python", "Git"],
    },
    {
        "category": "SAP Developer",
        "text": "SAP modules, ABAP, SQL, Agile, Business analysis basics",
        "expected_skills": ["SQL", "Agile"],
    },
    {
        "category": "React Developer",
        "text": "React, Redux, TypeScript, JavaScript, HTML, CSS, Node.js, Git, REST",
        "expected_skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Node.js", "Git", "REST"],
    },
    {
        "category": "Angular Developer",
        "text": "Angular, TypeScript, RxJS, HTML, CSS, REST, Git, Agile",
        "expected_skills": ["Angular", "TypeScript", "HTML", "CSS", "REST", "Git", "Agile"],
    },
    {
        "category": "Full Stack Developer",
        "text": "React, Node.js, Express.js, MongoDB, PostgreSQL, Docker, AWS, Git",
        "expected_skills": ["React", "Node.js", "Express.js", "MongoDB", "PostgreSQL", "Docker", "AWS", "Git"],
    },
    {
        "category": "Machine Learning Engineer",
        "text": "Python, TensorFlow, PyTorch, Scikit-learn, MLOps, Docker, Kubernetes, AWS",
        "expected_skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Docker", "Kubernetes", "AWS"],
    },
    {
        "category": "Cloud Engineer",
        "text": "AWS, Azure, GCP, Docker, Kubernetes, Terraform, Linux, Python",
        "expected_skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Linux", "Python"],
    },
    {
        "category": "iOS Developer",
        "text": "Swift, Objective-C, iOS, Xcode, REST, Git, Agile",
        "expected_skills": ["Swift", "Objective-C", "REST", "Git", "Agile"],
    },
    {
        "category": "PHP Developer",
        "text": "PHP, Laravel, MySQL, JavaScript, HTML, CSS, Git, Linux",
        "expected_skills": ["PHP", "Laravel", "MySQL", "JavaScript", "HTML", "CSS", "Git", "Linux"],
    },
    {
        "category": "Ruby Developer",
        "text": "Ruby, Rails, PostgreSQL, Git, REST, Agile, TDD",
        "expected_skills": ["Ruby", "Rails", "PostgreSQL", "Git", "REST", "Agile", "TDD"],
    },
    {
        "category": "Go Developer",
        "text": "Go, Microservices, Docker, Kubernetes, PostgreSQL, gRPC, Git, Linux",
        "expected_skills": ["Go", "Microservices", "Docker", "Kubernetes", "PostgreSQL", "Git", "Linux"],
    },
    {
        "category": "Rust Developer",
        "text": "Rust, Systems programming, Git, Linux, REST, PostgreSQL",
        "expected_skills": ["Rust", "Git", "Linux", "REST", "PostgreSQL"],
    },
    {
        "category": "Business Analyst",
        "text": "SQL, Excel, Agile, Scrum, Jira, Communication, Problem Solving",
        "expected_skills": ["SQL", "Agile", "Scrum", "Jira", "Communication", "Problem Solving"],
    },
    {
        "category": "Project Manager",
        "text": "Agile, Scrum, Kanban, Jira, Leadership, Communication, Project Management",
        "expected_skills": ["Agile", "Scrum", "Kanban", "Jira", "Leadership", "Communication", "Project Management"],
    },
    {
        "category": "UI UX Designer",
        "text": "Figma, HTML, CSS, JavaScript, Design Systems, Communication",
        "expected_skills": ["Figma", "HTML", "CSS", "JavaScript", "Communication"],
    },
    {
        "category": "Cybersecurity",
        "text": "Linux, Python, Networking, Security tools, Git, Problem Solving",
        "expected_skills": ["Linux", "Python", "Git", "Problem Solving"],
    },
    {
        "category": "Embedded Systems",
        "text": "C, C++, Python, Linux, Git, Microcontrollers, Problem Solving",
        "expected_skills": ["C", "C++", "Python", "Linux", "Git", "Problem Solving"],
    },
    {
        "category": "Game Developer",
        "text": "C++, C#, Unity, Git, OOP, Problem Solving, Agile",
        "expected_skills": ["C++", "C#", "Git", "OOP", "Problem Solving", "Agile"],
    },
    {
        "category": "Salesforce Developer",
        "text": "Salesforce, Apex, JavaScript, REST, Agile, Communication",
        "expected_skills": ["JavaScript", "REST", "Agile", "Communication"],
    },
    {
        "category": "Technical Writer",
        "text": "Documentation, Git, Markdown, Communication, Agile",
        "expected_skills": ["Git", "Communication", "Agile"],
    },
    {
        "category": "Scrum Master",
        "text": "Scrum, Agile, Kanban, Jira, Leadership, Communication, Teamwork",
        "expected_skills": ["Scrum", "Agile", "Kanban", "Jira", "Leadership", "Communication", "Teamwork"],
    },
    {
        "category": "AI Research",
        "text": "Python, PyTorch, TensorFlow, NLP, Deep Learning, Research, Git",
        "expected_skills": ["Python", "PyTorch", "TensorFlow", "NLP", "Deep Learning", "Git"],
    },
    {
        "category": "Computer Vision",
        "text": "Python, OpenCV, TensorFlow, PyTorch, Computer Vision, Deep Learning, Git",
        "expected_skills": ["Python", "TensorFlow", "PyTorch", "Computer Vision", "Deep Learning", "Git"],
    },
    {
        "category": "Backend Developer",
        "text": "Node.js, Express.js, Python, FastAPI, PostgreSQL, Redis, Docker, Git",
        "expected_skills": ["Node.js", "Express.js", "Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Git"],
    },
    {
        "category": "Frontend Developer",
        "text": "React, JavaScript, TypeScript, HTML, CSS, Webpack, Git, REST",
        "expected_skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Git", "REST"],
    },
    {
        "category": "SRE",
        "text": "Linux, Python, Go, Kubernetes, Docker, Monitoring, AWS, Git, CI/CD",
        "expected_skills": ["Linux", "Python", "Go", "Kubernetes", "Docker", "AWS", "Git", "CI/CD"],
    },
    {
        "category": "Data Engineer",
        "text": "Python, SQL, Spark, Airflow, AWS, Docker, PostgreSQL, Git",
        "expected_skills": ["Python", "SQL", "AWS", "Docker", "PostgreSQL", "Git"],
    },
]


def build_dataset() -> list[dict]:
    """Build numbered evaluation records with metadata."""
    records = []
    for i, sample in enumerate(KAGGLE_STYLE_SAMPLES, start=1):
        records.append(
            {
                "id": f"kaggle_eval_{i:03d}",
                "source": "Kaggle Resume Dataset (category-aligned)",
                "category": sample["category"],
                "text": sample["text"],
                "expected_skills": sample["expected_skills"],
            }
        )
    return records


def main() -> None:
    """Write kaggle_labeled_resumes.json and merged all_labeled_resumes.json."""
    out_dir = _ROOT / "resume_analyzer" / "data" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)

    kaggle_set = build_dataset()
    kaggle_path = out_dir / "kaggle_labeled_resumes.json"
    with kaggle_path.open("w", encoding="utf-8") as f:
        json.dump(kaggle_set, f, indent=2, ensure_ascii=False)

    legacy_path = out_dir / "skill_extraction_labels.json"
    legacy = []
    if legacy_path.exists():
        with legacy_path.open(encoding="utf-8") as f:
            legacy = json.load(f)

    merged = legacy + kaggle_set
    merged_path = out_dir / "all_labeled_resumes.json"
    with merged_path.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(kaggle_set)} Kaggle-style samples -> {kaggle_path}")
    print(f"Wrote {len(merged)} total samples -> {merged_path}")


if __name__ == "__main__":
    main()
