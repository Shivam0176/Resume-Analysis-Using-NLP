def generate_feedback(match_result: dict) -> list[str]:
    feedback = []

    final_score = match_result['final_score']
    matched_skills = match_result['matched_skills']
    missing_skills = match_result['missing_skills']

    if final_score >= 75:
        feedback.append(
            "Your resume has a strong overall match with this job description."
        )
    elif final_score >= 50:
        feedback.append(
            "Your resume has a moderate match. Adding more relevant evidence could improve it."
        )
    else:
        feedback.append(
            "Your resume has a low match. Consider tailoring it more closely to this role."
        )

    if matched_skills:
        skills = ", ".join(matched_skills)
        feedback.append(f"Matched skills: {skills}.")
    else:
        feedback.append(
            "No matching skills were detected between the resume and job description."
        )

    if missing_skills:
        skills = ", ".join(missing_skills)
        feedback.append(
            f"Consider highlighting relevant experience with: {skills}."
        )

    feedback.append(
        "Where possible, include measurable results from your projects or work experience."
    )

    return feedback
