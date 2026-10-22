
## Requirement Status Classification

SkillGap includes a rule-based job-description analyzer that identifies supported skill mentions and estimates their requirement status.

Supported labels:

- **Required** — the description explicitly indicates a requirement.
- **Preferred** — the skill is desirable but not necessarily mandatory.
- **Optional** — the description indicates that the skill is optional.
- **Not required / excluded** — the description explicitly says the skill is not required.
- **Mentioned — status unclear** — a skill is detected without a clear requirement signal.
- **Mixed signals — review** — conflicting requirement signals are detected for the same skill.

These labels are heuristic estimates, not definitive interpretations of job requirements. Complex wording, negation, and context may cause incorrect classifications. Users should review the original job description before relying on the results.

## Example Test Cases

| Job description | Expected result |
|---|---|
| Python is required. SQL is preferred. | Python: Required; SQL: Preferred |
| Python is optional. SQL is required. | Python: Optional; SQL: Required |
| Python is not required for this role, but SQL is preferred. | Python: Not required / excluded; SQL: Preferred |
| Python is required. Python is optional. | Python: Mixed signals — review |

These examples demonstrate selected functional tests, not a comprehensive accuracy evaluation.

## Testing and Limitations

The application has been manually tested for skill-gap calculations, charts, recommendations, CSV downloads, supported skill extraction, score validation, missing assessment handling, and selected requirement-status edge cases.

Current limitations:

- Skill extraction uses a fixed vocabulary and may miss skills outside the configured patterns.
- Requirement-status classification uses heuristic rules rather than a separately trained classifier.
- Complex sentences and contextual language may produce incorrect labels.
- Detected skill mentions should not be treated as definitive job requirements.

## Privacy and Scope

The public deployment package contains the Streamlit application and its required dependencies, without the saved model checkpoints or credentials used during experimentation.

SkillGap is an educational self-assessment and career-planning tool. Its outputs are intended to support learning and skill-gap analysis, not automated hiring or candidate rejection.
