from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from src.ner_extractor import extract_entities
from src.skill_extractor import compare_skill_sets,extract_hybrid_skills


@lru_cache(maxsize=1)
def load_model():
    '''caching the embedding model to reuse later'''
    return SentenceTransformer("all-MiniLM-L6-v2")

def calculate_semantic_score(
        resume_text: str,
        job_description: str
    ) -> float:
        model = load_model()

        embeddings = model.encode(
        [resume_text,job_description],
        normalize_embeddings=True
        )

        similarity = float(cosine_similarity(
              [embeddings[0]],
              [embeddings[1]]
        )[0][0])

        score = max(0.0,min(100.0,similarity * 100))
        return round(float(score),2)

def analyze_match(
    resume_text: str,
    job_description: str
) -> dict:
    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    resume_entities = extract_entities(resume_text)
    job_entities = extract_entities(job_description)

    resume_ner_skills = set(
        resume_entities.get("SKILL", [])
    )

    job_ner_skills = set(
        job_entities.get("SKILL", [])
    )

    resume_skills = extract_hybrid_skills(
        resume_text,
        ner_skills=resume_ner_skills,
    )

    job_skills = extract_hybrid_skills(
        job_description,
        ner_skills=job_ner_skills,
    )

    skill_results = compare_skill_sets(
        resume_skills,
        job_skills,
    )

    semantic_score = calculate_semantic_score(
        resume_text,
        job_description
    )

    final_score = (
        0.60 * semantic_score
        + 0.40 * skill_results["skill_score"]
    )


    return {
        "final_score": round(final_score, 2),
        "semantic_score": semantic_score,
        "skill_score": skill_results["skill_score"],
        "resume_skills": skill_results["resume_skills"],
        "job_skills": skill_results["job_skills"],
        "matched_skills": skill_results["matched_skills"],
        "missing_skills": skill_results["missing_skills"],
        "resume_entities": resume_entities,
        "job_entities": job_entities,
    }

