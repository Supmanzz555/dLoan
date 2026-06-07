# Agentic Architecture

## Overview

The system uses a **sequential multi-agent pipeline** orchestrated by LangGraph. Each agent is a single-purpose AI component powered by a Groq LLM (`llama-3.3-70b-versatile`, temperature=0, JSON mode). Agents run one after another, passing accumulated context forward. The pipeline includes deterministic post-processing for safety.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Applicant Input                         │
│      (Streamlit form / FastAPI POST /screen)            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              1. Intake Agent (Groq)                      │
│   Validates all required fields are present              │
│   ❌ Missing fields → STOP → "Need More Info"           │
│   ✅ Continue                                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             2. Document Agent (Groq)                     │
│   Verifies id_card, salary_slip, bank_statement          │
│   ❌ Missing docs → STOP → "Need More Info"             │
│   ✅ Continue                                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│           3. Eligibility Agent (Groq)                    │
│   Applies hard rules (age, employment, income)           │
│   Notes soft flags (DTI, credit history)                 │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             4. Risk Agent (Groq)                         │
│   Detects risk signals: high DTI, bad credit, etc.      │
│   Returns risk_flags list + risk_level                  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         5. Recommendation Agent (Groq)                   │
│   Decision table priority:                               │
│   1. Hard rule fails → Reject / Not Eligible            │
│   2. Risk flags present → High Risk Review               │
│   3. All clear → Proceed                                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          6. Explanation Agent (Groq)                     │
│   Generates human-readable explanation + next action     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          Post-LLM Validation (Python Rules)              │
│   • validate_applicant() from utils/rules.py            │
│   • Overrides LLM on hard rule disagreements            │
│   • Appends "Requires human review" disclaimer          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              ScreeningResult Output                      │
│   8 fields: recommendation, confidence, eligibility,    │
│   DTI ratio, risk_flags, missing_docs, explanation,     │
│   next_action                                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Human Credit Officer Review ⚠️             │
│   Final decision always made by a human                 │
└─────────────────────────────────────────────────────────┘
```

## Agent Details

### 1. Intake Agent
- **File:** `agents/intake_agent.py`
- **Responsibility:** Check that all required fields exist with non-empty values
- **Scope:** Presence only — does not validate content
- **On failure:** Pipeline stops, returns "Need More Info"

### 2. Document Agent
- **File:** `agents/document_agent.py`
- **Responsibility:** Verify id_card, salary_slip, bank_statement are uploaded
- **Scope:** Documents only — does not check eligibility
- **On failure:** Pipeline stops, returns "Need More Info"

### 3. Eligibility Agent
- **File:** `agents/eligibility_agent.py`
- **Responsibility:** Apply hard rules (age 21-60, valid employment, income ≥ 20K) and note soft flags (DTI > 60%, bad credit)
- **Output:** `eligible: bool`, `issues: list`, `dti_percentage: str`, `credit_note: str`

### 4. Risk Agent
- **File:** `agents/risk_agent.py`
- **Responsibility:** Identify risk signals within defined thresholds
- **Output:** `risk_flags: list[str]`, `risk_level: str`, `risk_summary: str`

### 5. Recommendation Agent
- **File:** `agents/recommendation_agent.py`
- **Responsibility:** Classify into 1 of 4 outcomes using a priority decision table
- **Priority:** Hard rule fail → Reject. Risk flags → High Risk Review. All clear → Proceed. Missing data → Need More Info

### 6. Explanation Agent
- **File:** `agents/explanation_agent.py`
- **Responsibility:** Generate plain-language explanation and suggested next action

## Post-LLM Validation

After the 6-agent pipeline completes, deterministic Python rules (`utils/rules.py`) validate the LLM's output against hard-coded business rules. This catches hallucinations such as:
- LLM says eligible when a hard rule failed → corrected
- LLM claims age violations that don't exist → corrected
- LLM overrides correct recommendation with caution → corrected

The rule engine always wins on hard, calculable facts. The LLM handles interpretation, risk detection, and explanation.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit (port 8501) |
| API | FastAPI (port 8000) |
| Orchestration | LangGraph |
| LLM | Groq API — llama-3.3-70b-versatile |
| Validation | Deterministic Python rules |
| Schema | Pydantic |
| Container | Docker + docker-compose |
| Package mgmt | uv |
| Testing | pytest (integration, real Groq) |

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Agent flow | Sequential | Simpler to debug and trace than parallel |
| Short-circuit | Intake/Document only | Missing data is fatal; eligibility and risk are advisory |
| Agent context | Full accumulated | Each agent sees all prior outputs for informed decisions |
| State | Stateless | One request = one screening, no history needed |
| Model | 70B (llama-3.3-70b-versatile) | 100K TPD limit on free tier; post-LLM rules compensate for residual inaccuracy |
| Post-validation | Rule override | Safety net for LLM hallucinations on hard facts |
| Human review | Disclaimer + no auto-action | Compliance: system assists, does not decide |
