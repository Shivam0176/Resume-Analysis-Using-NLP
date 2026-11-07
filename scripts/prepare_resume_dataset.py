"""Create a small, reproducible processed resume dataset.

The source archive is intentionally kept outside data/raw so that this script
does not duplicate potentially sensitive PDF files.
"""

import csv
import random
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_ROOT / "archive (6)" / "Resume" / "Resume.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "resumes.csv"

SAMPLES_PER_CATEGORY = 5
RANDOM_SEED = 42

MOJIBAKE_REPLACEMENTS = {
    "â€“": "-",
    "â€”": "-",
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€¦": "...",
    "Â": "",
    "�": "",
}


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)

    for broken_text, replacement in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(broken_text, replacement)

    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()


def load_resume_rows() -> dict[str, list[dict[str, str]]]:
    categories = defaultdict(list)

    with SOURCE_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {"ID", "Resume_str", "Category"}
        missing_columns = required_columns.difference(reader.fieldnames or [])

        if missing_columns:
            raise ValueError(
                f"Missing columns in source CSV: {sorted(missing_columns)}"
            )

        for row in reader:
            resume_text = clean_text(row.get("Resume_str") or "")
            category = (row.get("Category") or "").strip()

            if resume_text and category:
                categories[category].append(row)

    return categories


def select_rows(categories: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rng = random.Random(RANDOM_SEED)
    selected = []

    for category in sorted(categories):
        rows = categories[category].copy()
        rng.shuffle(rows)
        selected.extend(rows[:SAMPLES_PER_CATEGORY])

    return sorted(
        selected,
        key=lambda row: (row["Category"], row["ID"]),
    )


def write_processed_rows(rows: list[dict[str, str]]) -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "resume_id",
                "resume_text",
                "category",
                "source_file",
            ],
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "resume_id": row["ID"],
                    "resume_text": clean_text(row["Resume_str"]),
                    "category": row["Category"].strip(),
                    "source_file": "archive (6)/Resume/Resume.csv",
                }
            )


def main() -> None:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source dataset not found: {SOURCE_FILE}")

    categories = load_resume_rows()
    selected_rows = select_rows(categories)
    write_processed_rows(selected_rows)

    print(f"Categories processed: {len(categories)}")
    print(f"Rows written: {len(selected_rows)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
