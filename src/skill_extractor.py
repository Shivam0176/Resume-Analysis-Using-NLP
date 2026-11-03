import json
import re
from pathlib import Path
from src.ner_extractor import extract_skills as extract_ner_skills
SKILLS_FILE = Path(__file__).parent.parent / "data" / "skills.json"

def load_skills() -> dict[str,list[str]]:
    with open(SKILLS_FILE,"r",encoding="utf-8") as file:
        return json.load(file)

def normalize_skill(skill: str) -> str:
    skill = skill.lower().strip()
    skill = re.sub(r"[\u2010-\u2015]", "-", skill)
    skill = re.sub(r"\s*\+\s*", "+", skill)
    skill = re.sub(r"\s*-\s*", "-", skill)
    skill = re.sub(r"\s*/\s*", "/", skill)
    skill = re.sub(r"[,:;.!]+$", "", skill)
    skill = re.sub(r"\s+", " ", skill)

    return skill.strip()

def build_alias_map() -> dict[str, str]:
    skills = load_skills()
    alias_map = {}

    for canonical_skill, aliases in skills.items():
        canonical = normalize_skill(canonical_skill)

        alias_map[canonical] = canonical

        for alias in aliases:
            alias_map[normalize_skill(alias)] = canonical

    return alias_map


def extract_dictionary_skills(text: str) -> set[str]:
    normalized_text = normalize_skill(text)
    alias_map = build_alias_map()
    detected_skills = set()

    for alias, canonical in alias_map.items():
        pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

        if re.search(pattern, normalized_text):
            detected_skills.add(canonical)

    return detected_skills

def extract_hybrid_skills(
    text: str,
    ner_skills: set[str] | list[str] | None = None,
) -> set[str]:
    alias_map = build_alias_map()

    if ner_skills is None:
        ner_skills = extract_ner_skills(text)

    dictionary_skills = extract_dictionary_skills(text)

    normalized_ner_skills = {
        normalize_skill(skill)
        for skill in ner_skills
    }

    recognized_ner_skills = {
        alias_map[skill]
        for skill in normalized_ner_skills
        if skill in alias_map
    }

    return dictionary_skills.union(recognized_ner_skills)

def extract_skills(text: str) -> set[str]:
    return extract_hybrid_skills(text)


def compare_skill_sets(
    resume_skills: set[str],
    job_skills: set[str],
) -> dict:
    matched_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills.difference(resume_skills)

    skill_score = (
        len(matched_skills) / len(job_skills) * 100
        if job_skills
        else 0.0
    )

    return {
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "skill_score": round(float(skill_score), 2),
    }

def compare_skills(
    resume_text: str,
    job_description: str,
) -> dict:
    resume_skills = extract_hybrid_skills(resume_text)
    job_skills = extract_hybrid_skills(job_description)

    return compare_skill_sets(
        resume_skills,
        job_skills,
    )


if __name__ == "__main__":
    print(
        compare_skills(
            "I use Python, NLP and SQL",
            "Looking for Python, natural language processing, SQL and Docker",
        )
    )