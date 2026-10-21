import pandas as pd
import streamlit as st

st.set_page_config(page_title="SkillGap AI", page_icon="🎯", layout="wide")

TARGET = 80.0

SKILLS = {
    "Python": {"self": 0.20, "test": 0.50, "project": 0.30},
    "SQL": {"self": 0.20, "test": 0.50, "project": 0.30},
    "Excel": {"self": 0.20, "test": 0.40, "project": 0.40},
    "Power BI": {"self": 0.20, "test": 0.40, "project": 0.40},
    "Statistics": {"self": 0.20, "test": 0.60, "project": 0.20},
    "Data Cleaning": {"self": 0.20, "test": 0.40, "project": 0.40},
}

st.title("🎯 SkillGap AI")
st.caption("Assess skills, identify gaps, and plan your learning.")

st.info(
    "Prototype: scores are manually entered. This dashboard does not "
    "automatically grade tests, verify project quality, or establish job readiness."
)

selected = st.multiselect(
    "Choose skills to assess",
    list(SKILLS),
    default=["Python", "SQL", "Excel", "Power BI"],
)

with st.form("assessment_form"):
    scores = {}
    for skill in selected:
        st.subheader(skill)
        c1, c2, c3 = st.columns(3)
        scores[skill] = {
            "self": c1.number_input(
                "Self-rating (0–100)", 0, 100, 50, key=f"{skill}_self"
            ),
            "test": c2.number_input(
                "Test score (0–100)", 0, 100, 50, key=f"{skill}_test"
            ),
            "project": c3.number_input(
                "Project score (0–100)", 0, 100, 50, key=f"{skill}_project"
            ),
        }

    submitted = st.form_submit_button("Calculate skill gaps")

if submitted:
    rows = []
    for skill, values in scores.items():
        weights = SKILLS[skill]
        proficiency = sum(
            values[k] * weights[k] for k in ("self", "test", "project")
        )
        gap = max(0.0, TARGET - proficiency)

        if proficiency < 40:
            level = "Beginner"
        elif proficiency < 70:
            level = "Developing"
        elif proficiency < 85:
            level = "Proficient"
        else:
            level = "Advanced"

        priority = "High" if gap >= 30 else (
            "Medium" if gap > 0 else "Maintain"
        )

        rows.append({
            "Skill": skill,
            "Self-rating": values["self"],
            "Test score": values["test"],
            "Project score": values["project"],
            "Proficiency": round(proficiency, 1),
            "Level": level,
            "Gap to target": round(gap, 1),
            "Priority": priority,
        })

    results = pd.DataFrame(rows)

    if results.empty:
        st.warning("Select at least one skill, then submit the assessment.")
    else:
        a, b, c = st.columns(3)
        a.metric("Skills assessed", len(results))
        b.metric("Below target", int((results["Gap to target"] > 0).sum()))
        c.metric("Target proficiency", f"{TARGET:.0f}/100")

        st.subheader("Assessment results")
        st.dataframe(results, use_container_width=True, hide_index=True)

        st.subheader("Proficiency by skill")
        st.bar_chart(results.set_index("Skill")[["Proficiency"]])

        st.subheader("Recommended next steps")
        for _, row in results.sort_values(
            "Gap to target", ascending=False
        ).iterrows():
            if row["Gap to target"] > 0:
                st.write(
                    f"**{row['Skill']} — {row['Priority']} priority:** "
                    f"gap of {row['Gap to target']:.1f} points. "
                    "Practice with a focused exercise and reassess."
                )
            else:
                st.write(
                    f"**{row['Skill']}:** maintain proficiency with regular practice."
                )

        st.download_button(
            "Download assessment CSV",
            data=results.to_csv(index=False).encode("utf-8"),
            file_name="skillgap_assessment.csv",
            mime="text/csv",
        )

# New feature: rule-based job-description skill mentions.
import re

SKILL_PATTERNS = {
    "Python": [r"python"],
    "SQL": [r"\bsql\b"],
    "Excel": [r"excel"],
    "Power BI": [r"power\s*bi"],
    "Tableau": [r"tableau"],
    "Java": [r"\bjava\b"],
    "JavaScript": [r"javascript"],
    "TypeScript": [r"typescript"],
    "C++": [r"c\+\+"],
    "C#": [r"c\#"],
    "HTML": [r"\bhtml\b"],
    "CSS": [r"\bcss\b"],
    "pandas": [r"\bpandas\b"],
    "NumPy": [r"numpy"],
    "scikit-learn": [r"scikit[\s-]*learn", r"\bsklearn\b"],
    "TensorFlow": [r"tensorflow"],
    "PyTorch": [r"pytorch"],
    "Machine Learning": [r"machine\s+learning"],
    "Deep Learning": [r"deep\s+learning"],
    "Natural Language Processing": [r"natural\s+language\s+processing", r"\bnlp\b"],
    "Computer Vision": [r"computer\s+vision"],
    "Statistics": [r"statistics"],
    "Data Visualization": [r"data\s+visualization"],
    "ETL": [r"\betl\b"],
    "ELT": [r"\belt\b"],
    "Apache Spark": [r"apache\s+spark"],
    "PySpark": [r"pyspark"],
    "Apache Airflow": [r"apache\s+airflow"],
    "AWS": [r"\baws\b", r"amazon web services"],
    "Microsoft Azure": [r"microsoft azure", r"\bazure\b"],
    "Google Cloud": [r"google cloud", r"\bgcp\b"],
    "Docker": [r"docker"],
    "Kubernetes": [r"kubernetes"],
    "Git": [r"\bgit\b", r"\bgithub\b"],
    "Linux": [r"linux"],
    "Snowflake": [r"snowflake"],
    "Databricks": [r"databricks"],
    "PostgreSQL": [r"postgres(?:ql)?"],
    "MySQL": [r"mysql"],
    "MongoDB": [r"mongodb"],
    "CI/CD": [r"\bci\s*/\s*cd\b", r"\bcontinuous integration\b"],
}

_COMPILED = [
    (name, re.compile(r"(?<!\w)(?:" + "|".join(patterns) + r")(?!\w)", re.I))
    for name, patterns in SKILL_PATTERNS.items()
]

def detect_skill_mentions(text):
    if not isinstance(text, str) or not text.strip():
        return []
    found = []
    seen = set()
    for name, pattern in _COMPILED:
        if pattern.search(text) and name.casefold() not in seen:
            found.append(name)
            seen.add(name.casefold())
    return found

st.header("Job description skill mentions")
st.write(
    "Paste a job description to find skills from a fixed vocabulary. "
    "This prototype matches mentions; it does not interpret whether a skill "
    "is required, optional, or explicitly not needed."
)

with st.form("job_description_form"):
    job_description = st.text_area(
        "Paste job description",
        height=180,
        placeholder="Paste the job description here...",
        key="skillgap_job_description",
    )
    detect_submitted = st.form_submit_button("Detect skill mentions")

if detect_submitted:
    st.session_state["skillgap_detected_skills"] = detect_skill_mentions(
        job_description
    )
    st.session_state["skillgap_description_submitted"] = True

if st.session_state.get("skillgap_description_submitted", False):
    detected = st.session_state.get("skillgap_detected_skills", [])
    if detected:
        st.success(f"Detected {len(detected)} unique skill mentions.")
        st.write(", ".join(detected))
    else:
        st.info("No skills from the supported vocabulary were detected.")
