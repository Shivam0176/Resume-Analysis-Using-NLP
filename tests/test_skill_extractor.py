import pytest

from src.skill_extractor import compare_skills, extract_skills


@pytest.fixture(autouse=True)
def disable_ner_model(monkeypatch):
    monkeypatch.setattr(
        "src.skill_extractor.extract_ner_skills",
        lambda text: set(),
    )


def test_skill_aliases_are_detected():
    skills = extract_skills(
        "Experienced in Python, NLP, and sklearn."
    )

    assert "python" in skills
    assert "natural language processing" in skills
    assert "scikit-learn" in skills


def test_matching_and_missing_skills():
    result = compare_skills(
        "Python and SQL developer",
        "Looking for Python, SQL, and Docker"
    )

    assert "python" in result["matched_skills"]
    assert "sql" in result["matched_skills"]
    assert "docker" in result["missing_skills"]


def test_skill_score_is_between_zero_and_one_hundred():
    result = compare_skills(
        "Python developer",
        "Looking for Python and SQL"
    )

    assert 0 <= result["skill_score"] <= 100
