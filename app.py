#Streamlit UI
import streamlit as st

from src.document_parser import extract_text
from src.feedback import generate_feedback
from src.matcher import analyze_match


st.set_page_config(
    page_title="Resume Matcher",
    page_icon=":page_facing_up:",
    layout="wide"
)

st.title("Resume - Job Description Matcher")
st.write(
    "Upload your resume and paste a job description to see how closely they match."
)

resume_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)

job_description = st.text_area(
    "Paste the job description",
    height=300,
    placeholder="Paste the complete job description here..."
)

if st.button("Analyze Match", type="primary"):
    if resume_file is None:
        st.error("Please upload a PDF or DOCX resume.")
        st.stop()

    if not job_description.strip():
        st.error("Please paste a job description.")
        st.stop()

    try:
        resume_text = extract_text(
            resume_file,
            resume_file.name
        )

        with st.spinner("Analyzing your resume..."):
            result = analyze_match(
                resume_text,
                job_description
            )

        feedback = generate_feedback(result)

        st.success("Analysis complete!")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Overall Match",
            f"{result['final_score']:.1f}%"
        )

        col2.metric(
            "Semantic Match",
            f"{result['semantic_score']:.1f}%"
        )

        col3.metric(
            "Skill Match",
            f"{result['skill_score']:.1f}%"
        )


        st.subheader("Matched Skills")

        if result["matched_skills"]:
            st.write(", ".join(result["matched_skills"]))
        else:
            st.write("No matching skills detected.")

        st.subheader("Missing Skills")

        if result["missing_skills"]:
            st.write(", ".join(result["missing_skills"]))
        else:
            st.write("No missing skills detected from the current dictionary.")

        st.subheader("Extracted Profile Information")
        visible_labels = {
            "TITLE",
            "COMPANY",
            "DEGREE",
            "INSTITUTION",
            "CERT",
            "LANGUAGE",
        }
        def display_entities(title, entities):
            st.write(f"**{title}**")

            found = False

            for label in visible_labels:
                values = entities.get(label, [])

                if values:
                    found = True
                    unique_values = sorted(set(values))
                    st.write(
                        f"- **{label.title()}**: {', '.join(unique_values)}"
                    )

            if not found:
                st.write("No additional profile information detected.")


        with st.expander("View extracted resume information"):
            display_entities(
                "Resume entities",
                result["resume_entities"]
            )

        with st.expander("View extracted job requirements"):
            display_entities(
                "Job-description entities",
                result["job_entities"]
            )

        st.subheader("Feedback")

        for message in feedback:
            st.write(f"- {message}")

        st.info(
            "This tool provides an estimate to help tailor your resume. "
            "It is not a hiring decision."
        )

        st.subheader("How was this score calculated?")

        final_score = float(result["final_score"])

        st.progress(
            min(max(final_score / 100.0, 0.0), 1.0)
        )


        st.write(
            f"""
            The final score combines:

            - Semantic similarity: **60%**
            - Skill coverage: **40%**

            Semantic score: **{float(result["semantic_score"]):.1f}%**

            Skill score: **{float(result["skill_score"]):.1f}%**
            """
        )



    except Exception as error:
        st.error(f"Analysis failed: {error}")
