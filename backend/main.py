import os
from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.document_parser import extract_text
from src.feedback import generate_feedback
from src.matcher import analyze_match


app = FastAPI(title="Resume Matcher API", version="1.0.0")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

allowed_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins.split(",")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
) -> dict:
    filename = resume.filename or ""
    if not filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Upload a PDF or DOCX resume.")
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Paste a job description to continue.")

    try:
        contents = await resume.read(MAX_UPLOAD_BYTES + 1)
        if not contents:
            raise ValueError("The uploaded file is empty.")
        if len(contents) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Resume must be smaller than 10 MB.")
        resume_text = extract_text(BytesIO(contents), filename)
        result = analyze_match(resume_text, job_description)
        result["feedback"] = generate_feedback(result)
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please try again in a moment.",
        ) from error
