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
    """Return unique skills mentioned, preserving the existing interface."""
    if not isinstance(text, str) or not text.strip():
        return []
    found = []
    seen = set()
    for name, pattern in _COMPILED:
        if pattern.search(text) and name.casefold() not in seen:
            found.append(name)
            seen.add(name.casefold())
    return found


def _sentence_for_span(text, start, end):
    """Return the local clause around a skill, not the whole sentence."""
    left = max(
        text.rfind(".", 0, start),
        text.rfind("!", 0, start),
        text.rfind("?", 0, start),
        text.rfind("\n", 0, start),
    ) + 1

    right_candidates = [
        pos for pos in (
            text.find(".", end),
            text.find("!", end),
            text.find("?", end),
            text.find("\n", end),
        ) if pos != -1
    ]
    right = min(right_candidates) if right_candidates else len(text)
    sentence = text[left:right]

    # Split clauses at punctuation and contrast markers.
    # Do not split on "and", so "Python and SQL are required" stays together.
    boundaries = list(re.finditer(
        r"[,;]|\b(?:but|however|whereas|although|while)\b",
        sentence,
        flags=re.I,
    ))
    cuts = [0] + [m.end() for m in boundaries] + [len(sentence)]
    starts = [0] + [m.start() for m in boundaries]

    relative_start = start - left
    relative_end = end - left

    for i in range(len(starts)):
        clause_start = starts[i]
        clause_end = cuts[i + 1]
        if clause_start <= relative_start and relative_end <= clause_end:
            return sentence[clause_start:clause_end].strip(" ,;")

    return sentence.strip()

def _classify_context(context):
    """Heuristic status label; always conservative when wording is unclear."""
    s = context.casefold()

    excluded = (
        r"\bnot\s+(?:explicitly\s+)?(?:required|needed|necessary|mandatory)\b",
        r"\bnot\s+a\s+requirement\b",
        r"\bno\s+need\s+for\b",
        r"\b(?:do\s+not|don't|doesn't|does\s+not)\s+need\b",
        r"\bnot\s+looking\s+for\b",
        r"\bexclude(?:d)?\b",
    )
    if any(re.search(p, s) for p in excluded):
        return "Not required / excluded"

    if re.search(
        r"\boptional\b|\bnice[- ]to[- ]have\b|\bnot essential\b",
        s,
    ):
        return "Optional"

    if re.search(
        r"\bpreferred\b|\bdesirable\b|\bideally\b|\ba plus\b|\bbonus\b",
        s,
    ):
        return "Preferred"

    if re.search(
        r"\b(?:required|mandatory|essential)\b"
        r"|\bmust[- ]have\b|\bmust have\b"
        r"|\brequired to\b|\bneed to have\b",
        s,
    ):
        return "Required"

    return "Mentioned — status unclear"


def classify_skill_mentions(text):
    """Return (skill, status) pairs based on the local sentence context."""
    if not isinstance(text, str) or not text.strip():
        return []

    results = []
    for name, pattern in _COMPILED:
        contexts = [
            _sentence_for_span(text, m.start(), m.end())
            for m in pattern.finditer(text)
        ]
        if not contexts:
            continue

        statuses = {_classify_context(c) for c in contexts}
        if len(statuses) == 1:
            status = next(iter(statuses))
        else:
            status = "Mixed signals — review"
        results.append((name, status))

    return results


st.header("Job description skill mentions")
st.write(
    "Find skills from a fixed vocabulary and estimate their requirement status "
    "using simple wording rules. Labels are heuristic and may be wrong; "
    "review the original job description before making decisions."
)

with st.form("job_description_form"):
    job_description = st.text_area(
        "Paste job description",
        height=180,
        placeholder="Paste the job description here...",
        key="skillgap_job_description",
    )
    detect_submitted = st.form_submit_button("Analyze skill mentions")

if detect_submitted:
    st.session_state["skillgap_classified_mentions"] = (
        classify_skill_mentions(job_description)
    )
    st.session_state["skillgap_description_submitted"] = True

if st.session_state.get("skillgap_description_submitted", False):
    classified = st.session_state.get("skillgap_classified_mentions", [])
    if classified:
        st.success(f"Analyzed {len(classified)} unique skill mentions.")
        st.dataframe(
            [{"Skill": skill, "Estimated status": status}
             for skill, status in classified],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Heuristic labels can misread complex sentences, "
            "negation, or conflicting requirements. Verify each label."
        )
    else:
        st.info("No skills from the supported vocabulary were detected.")
