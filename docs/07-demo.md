# Demo & Presentation

## Demo Videos

- **English response:** [Watch on YouTube](https://youtu.be/G-pGU5vu2z0)
- **Thai response:** [Watch on YouTube](https://youtu.be/PRxpDzR5PCU)

## Demo Scenarios

| Scenario | Applicant | Outcome | Key Takeaway |
|----------|-----------|---------|--------------|
| Happy path | APP001 (Somchai) | Proceed | Clean applicant → instant proceed with all fields, docs, rules passing |
| Missing document | APP003 (Nattapong) | Need More Info | Pipeline short-circuits at Document Agent, no wasted LLM calls |
| Low income | APP005 (Malee) | Reject / Not Eligible | Hard rules enforced regardless of other factors |
| High DTI | APP007 (Thana) | High Risk Review | Borderline cases flagged for human judgment, not auto-rejected |
| Bad credit | APP008 (Pichai) | High Risk Review | Credit history risk flagged for senior officer review |
| Self-employed | APP009 (Chalerm) | Proceed | Non-employee types accepted with stable income |
| Extreme DTI | APP016 (Thawatchai) | High Risk Review | 160% DTI correctly flagged |
| Unemployed + no income | APP017 (Kwan) | Reject / Not Eligible | Multiple hard rule failures → reject |
| Extreme loan amount | APP019 (Preecha) | High Risk Review | 5M loan on 40K income flagged for review |
| API test | curl request | Proceed | REST API returns structured JSON, integrable with any system |

## Architecture Highlights

### 6 Agents

| Agent | Responsibility |
|-------|---------------|
| **Intake** | Check 9 fields are present |
| **Document** | Verify id_card, salary_slip, bank_statement |
| **Eligibility** | Apply hard rules (age 21-60, income ≥20K, employment type) |
| **Risk** | Detect risk signals (high DTI, bad credit, borderline income) |
| **Recommendation** | Classify into 1 of 4 outcomes |
| **Explanation** | Generate human-readable explanation + next action |

### Safety by Design

- **Post-LLM rule validation** — Deterministic Python overrides LLM on hard facts
- **Human review disclaimer** — Every output requires officer verification
- **No protected attributes** — Schema excludes gender, religion, race, etc.

### Pipeline Short-Circuit

Pipeline stops at Intake or Document agent if data is missing → returns "Need More Info" immediately. Saves up to 4 LLM calls per incomplete application.

## Test Results

20/20 applicants pass integration tests against real Groq LLM. All core requirements covered.

---

## Demo GIFs

| Run with Docker | Run with script |
|----------------|-----------------|
| ![Docker](img/demo_Docker.gif) | ![Script](img/demo_noDocker.gif) |
