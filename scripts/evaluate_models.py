"""Evaluate TF-IDF, embedding, and hybrid resume matching scores."""

import csv
import json
import math
import os
from pathlib import Path

# Evaluation should be reproducible and must not depend on a live Hub request.
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.matcher import calculate_semantic_score
from src.skill_extractor import compare_skills


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESUME_FILE = PROJECT_ROOT / "data" / "processed" / "resumes.csv"
JOB_FILE = PROJECT_ROOT / "data" / "processed" / "job_descriptions.csv"
PAIR_FILE = PROJECT_ROOT / "data" / "evaluation" / "matching_pairs.csv"
RESULT_FILE = PROJECT_ROOT / "data" / "evaluation" / "model_results.csv"
SUMMARY_FILE = PROJECT_ROOT / "data" / "evaluation" / "evaluation_summary.json"

SEMANTIC_WEIGHT = 0.60
SKILL_WEIGHT = 0.40


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def tfidf_score(resume_text: str, job_description: str) -> float:
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
    )
    matrix = vectorizer.fit_transform([resume_text, job_description])
    score = cosine_similarity(matrix[0], matrix[1])[0][0] * 100
    return round(float(score), 2)


def score_to_label(score: float) -> str:
    if score < 40:
        return "low"
    if score < 70:
        return "medium"
    return "high"


def average_ranks(values: list[float]) -> list[float]:
    sorted_values = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    position = 0

    while position < len(sorted_values):
        end = position

        while (
            end + 1 < len(sorted_values)
            and sorted_values[end + 1][1] == sorted_values[position][1]
        ):
            end += 1

        average_rank = (position + end) / 2 + 1

        for index in range(position, end + 1):
            original_index = sorted_values[index][0]
            ranks[original_index] = average_rank

        position = end + 1

    return ranks


def spearman_correlation(predictions: list[float], actual: list[float]) -> float:
    prediction_ranks = average_ranks(predictions)
    actual_ranks = average_ranks(actual)

    prediction_mean = sum(prediction_ranks) / len(prediction_ranks)
    actual_mean = sum(actual_ranks) / len(actual_ranks)

    numerator = sum(
        (prediction - prediction_mean) * (target - actual_mean)
        for prediction, target in zip(prediction_ranks, actual_ranks)
    )
    prediction_variance = sum(
        (prediction - prediction_mean) ** 2
        for prediction in prediction_ranks
    )
    actual_variance = sum(
        (target - actual_mean) ** 2
        for target in actual_ranks
    )

    denominator = math.sqrt(prediction_variance * actual_variance)

    if denominator == 0:
        return 0.0

    return round(numerator / denominator, 4)


def evaluate_method(
    rows: list[dict[str, str]],
    score_key: str,
) -> dict:
    scores = [float(row[score_key]) for row in rows]
    actual_scores = [float(row["relevance_score"]) for row in rows]

    correct = sum(
        score_to_label(score) == row["fit_label"]
        for score, row in zip(scores, rows)
    )

    return {
        "accuracy": round(correct / len(rows), 4),
        "spearman_correlation": spearman_correlation(scores, actual_scores),
        "mean_score": round(sum(scores) / len(scores), 2),
    }


def main() -> None:
    resumes = {
        row["resume_id"]: row["resume_text"]
        for row in load_rows(RESUME_FILE)
    }
    jobs = {
        row["job_id"]: row["job_description"]
        for row in load_rows(JOB_FILE)
    }
    pairs = load_rows(PAIR_FILE)
    results = []

    for number, pair in enumerate(pairs, start=1):
        resume_text = resumes[pair["resume_id"]]
        job_description = jobs[pair["job_id"]]

        tfidf = tfidf_score(resume_text, job_description)
        semantic = calculate_semantic_score(resume_text, job_description)
        skill_result = compare_skills(resume_text, job_description)
        skill_score = float(skill_result["skill_score"])
        hybrid = (
            SEMANTIC_WEIGHT * semantic
            + SKILL_WEIGHT * skill_score
        )

        results.append(
            {
                **pair,
                "tfidf_score": round(tfidf, 2),
                "semantic_score": round(semantic, 2),
                "skill_score": round(skill_score, 2),
                "hybrid_score": round(hybrid, 2),
                "tfidf_prediction": score_to_label(tfidf),
                "semantic_prediction": score_to_label(semantic),
                "hybrid_prediction": score_to_label(hybrid),
            }
        )

        print(f"Evaluated {number}/{len(pairs)} pairs")

    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with RESULT_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "pair_count": len(results),
        "label_source": "synthetic_category_heuristic",
        "score_thresholds": {
            "low": "score < 40",
            "medium": "40 <= score < 70",
            "high": "score >= 70",
        },
        "hybrid_weights": {
            "semantic": SEMANTIC_WEIGHT,
            "skills": SKILL_WEIGHT,
        },
        "methods": {
            "tfidf": evaluate_method(results, "tfidf_score"),
            "semantic_embeddings": evaluate_method(results, "semantic_score"),
            "hybrid": evaluate_method(results, "hybrid_score"),
        },
    }

    with SUMMARY_FILE.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print(f"Results: {RESULT_FILE}")
    print(f"Summary: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
