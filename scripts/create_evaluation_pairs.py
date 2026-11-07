"""Create synthetic resume/job-description evaluation pairs.

This creates a reproducible benchmark for the matching pipeline. The labels
are category-based synthetic labels and must not be presented as real hiring
outcomes.
"""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESUME_FILE = PROJECT_ROOT / "data" / "processed" / "resumes.csv"
JOB_FILE = PROJECT_ROOT / "data" / "processed" / "job_descriptions.csv"
PAIR_FILE = PROJECT_ROOT / "data" / "evaluation" / "matching_pairs.csv"


JOB_TEMPLATES = {
    "INFORMATION-TECHNOLOGY": {
        "title": "Information Technology Specialist",
        "description": (
            "We are looking for an Information Technology Specialist with "
            "experience in Python, SQL, Git, Docker, AWS, and software "
            "troubleshooting. The role includes automation, system support, "
            "data analysis, documentation, and collaboration with engineering "
            "teams."
        ),
    },
    "ENGINEERING": {
        "title": "Software Engineering Associate",
        "description": (
            "We are hiring a Software Engineering Associate with experience "
            "in Python, SQL, Git, Docker, and AWS. Responsibilities include "
            "building reliable software, debugging applications, writing "
            "technical documentation, and collaborating on engineering projects."
        ),
    },
    "BUSINESS-DEVELOPMENT": {
        "title": "Business Development Analyst",
        "description": (
            "We are looking for a Business Development Analyst who can use "
            "Python, SQL, and data analysis to support market research, "
            "reporting, customer insights, and business decisions. Strong "
            "communication and documentation skills are required."
        ),
    },
    "FINANCE": {
        "title": "Finance Data Analyst",
        "description": (
            "We are hiring a Finance Data Analyst with Python, SQL, and "
            "machine learning experience. The role includes financial data "
            "analysis, reporting, data quality checks, automation, and clear "
            "communication of analytical findings."
        ),
    },
    "HR": {
        "title": "Human Resources Technology Analyst",
        "description": (
            "We are looking for an HR Technology Analyst with SQL, Python, "
            "Git, and data analysis experience. Responsibilities include "
            "reporting, process improvement, system documentation, employee "
            "data quality, and collaboration with business teams."
        ),
    },
    "HEALTHCARE": {
        "title": "Healthcare Data Analyst",
        "description": (
            "We are hiring a Healthcare Data Analyst with Python, SQL, and "
            "machine learning experience. The role includes healthcare data "
            "quality, reporting, statistical analysis, documentation, and "
            "privacy-conscious handling of sensitive information."
        ),
    },
}


RELATED_CATEGORY = {
    "INFORMATION-TECHNOLOGY": "ENGINEERING",
    "ENGINEERING": "INFORMATION-TECHNOLOGY",
    "BUSINESS-DEVELOPMENT": "HR",
    "FINANCE": "BUSINESS-DEVELOPMENT",
    "HR": "BUSINESS-DEVELOPMENT",
    "HEALTHCARE": "FINANCE",
}


OPPOSITE_CATEGORY = {
    "INFORMATION-TECHNOLOGY": "HEALTHCARE",
    "ENGINEERING": "HR",
    "BUSINESS-DEVELOPMENT": "HEALTHCARE",
    "FINANCE": "INFORMATION-TECHNOLOGY",
    "HR": "ENGINEERING",
    "HEALTHCARE": "INFORMATION-TECHNOLOGY",
}


def load_resumes() -> dict[str, list[dict[str, str]]]:
    grouped = {category: [] for category in JOB_TEMPLATES}

    with RESUME_FILE.open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            category = row["category"]
            if category in grouped and row["resume_text"].strip():
                grouped[category].append(row)

    for category in grouped:
        grouped[category].sort(key=lambda row: row["resume_id"])

    return grouped


def select_resumes(grouped: dict[str, list[dict[str, str]]], count: int):
    selected = []
    categories = sorted(grouped)
    index = 0

    while len(selected) < count:
        category = categories[index % len(categories)]
        rows = grouped[category]

        if rows:
            selected.append(rows[(index // len(categories)) % len(rows)])

        index += 1

    return selected


def write_job_descriptions() -> None:
    JOB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with JOB_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["job_id", "job_title", "job_description", "source_file"],
        )
        writer.writeheader()

        for category, template in sorted(JOB_TEMPLATES.items()):
            writer.writerow(
                {
                    "job_id": f"job_{category.lower().replace('-', '_')}",
                    "job_title": template["title"],
                    "job_description": template["description"],
                    "source_file": "synthetic_template",
                }
            )


def write_pairs(grouped: dict[str, list[dict[str, str]]]) -> None:
    pairs = []
    pair_id = 1

    configurations = [
        (20, "high", 5, lambda category: category),
        (15, "medium", 3, lambda category: RELATED_CATEGORY[category]),
        (15, "low", 1, lambda category: OPPOSITE_CATEGORY[category]),
    ]

    for count, label, relevance_score, target_category in configurations:
        for resume in select_resumes(grouped, count):
            job_category = target_category(resume["category"])
            job_id = f"job_{job_category.lower().replace('-', '_')}"

            pairs.append(
                {
                    "pair_id": f"pair_{pair_id:03d}",
                    "resume_id": resume["resume_id"],
                    "job_id": job_id,
                    "resume_category": resume["category"],
                    "job_category": job_category,
                    "fit_label": label,
                    "relevance_score": relevance_score,
                    "label_source": "synthetic_category_heuristic",
                }
            )
            pair_id += 1

    PAIR_FILE.parent.mkdir(parents=True, exist_ok=True)

    with PAIR_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "pair_id",
                "resume_id",
                "job_id",
                "resume_category",
                "job_category",
                "fit_label",
                "relevance_score",
                "label_source",
            ],
        )
        writer.writeheader()
        writer.writerows(pairs)


def main() -> None:
    if not RESUME_FILE.exists():
        raise FileNotFoundError(f"Processed resumes not found: {RESUME_FILE}")

    grouped = load_resumes()
    write_job_descriptions()
    write_pairs(grouped)

    print("Job descriptions written: 6")
    print("Evaluation pairs written: 50")
    print(f"Job output: {JOB_FILE}")
    print(f"Pair output: {PAIR_FILE}")


if __name__ == "__main__":
    main()
