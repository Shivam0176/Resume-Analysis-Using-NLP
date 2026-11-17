# Career Lens — Resume Matcher

A resume-to-job comparison tool with a separate React web app and Python API. Upload a PDF or DOCX resume to review semantic similarity, detected skill coverage, profile entities, and tailoring feedback.

> Scores are estimates to help review a resume. They are not hiring decisions and do not measure skill proficiency.

## Stack

- **Frontend:** React, TypeScript, and Vite (`frontend/`)
- **API:** FastAPI (`backend/`)
- **Analysis:** Existing Python document parser, resume NER model, skill dictionary, and sentence embedding model (`src/`)

The API loads `oksomu/resume-ner` and `all-MiniLM-L6-v2`. Models are cached in memory after loading. First use may download the models and can take some time; PyTorch uses CUDA when available and otherwise runs on CPU.

## Run locally

Use Python 3.10+ and Node.js 18+.

### 1. Install and start the API

From the repository root:

```bash
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
source .venv/bin/activate
```

Install the Python packages and run FastAPI:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

The API health check is at `http://localhost:8000/api/health`.

### 2. Install and start the web app

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local Vite URL shown in the terminal, usually `http://localhost:5173`. The frontend uses `http://localhost:8000` by default. To use a different API URL, set `VITE_API_URL` in a frontend `.env` file, for example:

```text
VITE_API_URL=https://api.example.com
```

For a deployed frontend, set the backend's `FRONTEND_ORIGINS` environment variable to a comma-separated list of allowed frontend origins.

## API

`POST /api/analyze` accepts multipart form data:

- `resume`: PDF or DOCX file, up to 10 MB in the web interface
- `job_description`: text field

It returns `final_score`, `semantic_score`, `skill_score`, resume/job/matched/missing skills, resume/job entities, and feedback. Unsupported files and empty inputs return a readable client error. Uploaded content is processed in memory and is not saved by the API.

## Matching details

1. PDF or DOCX text is extracted by `src/document_parser.py`. Image-only PDFs are not OCR processed.
2. `oksomu/resume-ner` identifies skills and profile entities. Long text is split into overlapping chunks.
3. Skill extraction combines NER output with canonical skills and aliases in `data/skills.json`.
4. Skill coverage is the percentage of detected job skills also detected in the resume. If no job skills are found, this score is zero.
5. Semantic similarity is the cosine similarity of resume and job-description embeddings from `all-MiniLM-L6-v2`.
6. Overall score = 60% semantic similarity + 40% skill coverage.

The dashboard displays these scores alongside matched/missing skills, extracted profile and role entities, and feedback. Skill mentions do not establish experience quality or proficiency.

## Tests

Run Python tests from the repository root:

```bash
pytest
```

Matcher and API tests mock model inference; they do not need to download the ML models. Build-check the frontend with:

```bash
cd frontend
npm run build
```

## Evaluation utilities

The scripts in `scripts/` prepare a sample resume dataset, create synthetic job descriptions and matching pairs, and compare TF-IDF, embedding, and hybrid scores. Dataset preparation expects `archive (6)/Resume/Resume.csv`. The generated labels are category-based heuristics, not human relevance judgments or hiring outcomes.
