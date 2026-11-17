from fastapi.testclient import TestClient

from backend import main


client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_scores_skills_entities_and_feedback(monkeypatch):
    monkeypatch.setattr(main, "extract_text", lambda file, name: "Resume text")
    monkeypatch.setattr(
        main,
        "analyze_match",
        lambda resume, job: {
            "final_score": 74.67,
            "semantic_score": 80,
            "skill_score": 66.67,
            "resume_skills": ["python", "sql"],
            "job_skills": ["docker", "python", "sql"],
            "matched_skills": ["python", "sql"],
            "missing_skills": ["docker"],
            "resume_entities": {"TITLE": ["Data Analyst"]},
            "job_entities": {"TITLE": ["Data Engineer"]},
        },
    )
    monkeypatch.setattr(main, "generate_feedback", lambda result: ["Add Docker evidence."])

    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", b"fake pdf", "application/pdf")},
        data={"job_description": "Need Python and Docker"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["final_score"] == 74.67
    assert result["missing_skills"] == ["docker"]
    assert result["resume_entities"]["TITLE"] == ["Data Analyst"]
    assert result["feedback"] == ["Add Docker evidence."]


def test_analyze_rejects_unsupported_file(monkeypatch):
    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.txt", b"text", "text/plain")},
        data={"job_description": "Need Python"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Upload a PDF or DOCX resume."


def test_analyze_rejects_blank_job_description():
    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", b"fake pdf", "application/pdf")},
        data={"job_description": "  "},
    )
    assert response.status_code == 400
