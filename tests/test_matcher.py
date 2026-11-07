import pytest

from src import matcher


def fake_entities(text: str) -> dict[str, list[str]]:
    if text.startswith("resume"):
        return {
            "SKILL": ["Python", "SQL"],
            "TITLE": ["Data Analyst"],
        }

    return {
        "SKILL": ["Python", "SQL", "Docker"],
        "TITLE": ["Data Engineer"],
    }


def test_analyze_match_returns_complete_result(monkeypatch):
    monkeypatch.setattr(matcher, "extract_entities", fake_entities)
    monkeypatch.setattr(
        matcher,
        "calculate_semantic_score",
        lambda resume_text, job_description: 80.0,
    )

    result = matcher.analyze_match(
        "resume Python SQL",
        "job Python SQL Docker",
    )

    assert result["semantic_score"] == 80.0
    assert result["skill_score"] == pytest.approx(66.67, abs=0.01)
    assert result["final_score"] == pytest.approx(74.67, abs=0.01)
    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["docker"]
    assert result["resume_entities"]["TITLE"] == ["Data Analyst"]
    assert result["job_entities"]["TITLE"] == ["Data Engineer"]


def test_analyze_match_rejects_empty_resume():
    with pytest.raises(ValueError, match="Resume text cannot be empty"):
        matcher.analyze_match(
            "",
            "Python developer",
        )


def test_analyze_match_rejects_empty_job_description():
    with pytest.raises(ValueError, match="Job description cannot be empty"):
        matcher.analyze_match(
            "Python developer",
            "",
        )

