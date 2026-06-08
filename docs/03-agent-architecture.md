# Agent Architecture

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
│   9 fields: recommendation, confidence, eligibility,    │
│   DTI ratio, risk_flags, missing_docs, explanation,     │
│   next_action, screening_id                             │
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
- **Scope:** Presence only — explicitly instructed NOT to validate content
- **On failure:** Pipeline stops at Intake, returns "Need More Info"

```python
def run(applicant: dict) -> dict:
    prompt = load_prompt("intake")
    # Checks applicant_id, name, age, employment_type,
    # monthly_income, monthly_debt, requested_loan_amount,
    # credit_history, uploaded_documents
    return call_llm(messages)
```

### 2. Document Agent

- **File:** `agents/document_agent.py`
- **Responsibility:** Verify `id_card`, `salary_slip`, `bank_statement` are in `uploaded_documents`
- **Scope:** Documents only — instructed NOT to check eligibility
- **On failure:** Pipeline stops at Document, returns "Need More Info"

```python
def run(applicant: dict) -> dict:
    prompt = load_prompt("document")
    # Returns valid: bool, missing_documents: list, notes: str
    return call_llm(messages)
```

### 3. Eligibility Agent

- **File:** `agents/eligibility_agent.py`
- **Responsibility:** Apply hard rules (age 21-60, valid employment, income ≥ 20K THB) and note soft flags (DTI > 60%, bad credit)
- **Pre-computes DTI ratio** and passes `calculated_dti` to the LLM
- **Output:** `eligible: bool`, `issues: list`, `dti_percentage: str`, `credit_note: str`

```python
def run(applicant: dict) -> dict:
    prompt = load_prompt("eligibility")
    # Receives calculated_dti for accurate numeric comparison
    return call_llm(messages)
```

### 4. Risk Agent

- **File:** `agents/risk_agent.py`
- **Responsibility:** Identify genuine risk signals within defined thresholds
- **Context input:** Receives all prior agent results (intake, document, eligibility)
- **Output:** `risk_flags: list[str]`, `risk_level: str` (low/medium/high), `risk_summary: str`

```python
def run(applicant: dict, prior_context: dict | None = None) -> dict:
    prompt = load_prompt("risk")
    # Detects: high DTI, bad credit, borderline income,
    # high loan-to-income, other concerns
    return call_llm(messages)
```

### 5. Recommendation Agent

- **File:** `agents/recommendation_agent.py`
- **Responsibility:** Classify into one of 4 outcomes using a priority decision table
- **Priority order:**
  1. Missing fields/docs → "Need More Info"
  2. Hard rule failed → "Reject / Not Eligible"
  3. Risk flags present → "High Risk Review"
  4. Otherwise → "Proceed"

```python
def run(applicant: dict, prior_context: dict) -> dict:
    prompt = load_prompt("recommendation")
    # Returns recommendation, confidence, reasoning
    return call_llm(messages)
```

### 6. Explanation Agent

- **File:** `agents/explanation_agent.py`
- **Responsibility:** Generate plain-language explanation and suggested next action for the credit officer
- **Context input:** Full accumulated assessment from all prior agents

```python
def run(applicant: dict, prior_context: dict) -> dict:
    prompt = load_prompt("explanation")
    # Returns explanation: str, next_action: str
    return call_llm(messages)
```

---

## LLM Client

All agents use a shared LLM client (`agents/llm_client.py`) that:

- Reads `LLM_PROVIDER` env var (`groq` or `openai`)
- Initializes the corresponding SDK client
- Calls the model with `temperature=0` and `response_format="json_object"`
- Implements 3-retry exponential backoff for rate limits
- Returns parsed JSON dict

```python
def call_llm(messages: list[dict]) -> dict:
    # Retry with backoff for RateLimitError (429)
    # Uses Groq's llama-3.3-70b-versatile or OpenAI's gpt-4o-mini
    return response.choices[0].message.parsed
```

---

## Prompt Design

Each agent has a dedicated prompt template in `prompts/`:

| File | Purpose | Key Guard |
|------|---------|-----------|
| `intake.txt` | Check field presence only | "Do NOT validate field content" |
| `document.txt` | Check 3 required documents | "Check ONLY documents" |
| `eligibility.txt` | Apply hard rules + note soft flags | "Soft flags alone must NOT set eligible=false" |
| `risk.txt` | Detect genuine risk signals | "Do NOT flag DTI below 60% or normal/good/fair credit" |
| `recommendation.txt` | 4-outcome priority classification | "Eligibility overrides risk on hard rule failures" |
| `explanation.txt` | Generate human-readable reasoning | "Use only provided data, no assumptions" |

All prompts share the instruction: *"use only provided data, no assumptions."*

---

## LangGraph Pipeline

The pipeline is defined in `workflow/graph.py` using LangGraph's `StateGraph`:

```python
# AgentState TypedDict holds applicant + all 6 agent results
# 6 node functions, each calling the corresponding agent
# 2 conditional routing functions for short-circuit

def build_graph() -> StateGraph:
    # START → intake → document → eligibility → risk → recommendation → explanation → END
    # intake → route_after_intake (document or END)
    # document → route_after_document (eligibility or END)
    return graph
```

### Short-Circuit Logic

```
route_after_intake(state):
    if state["should_stop"]:
        return END  # Pipeline stops, returns "Need More Info"
    return "document"

route_after_document(state):
    if state["should_stop"]:
        return END  # Pipeline stops, returns "Need More Info"
    return "eligibility"
```

### Post-LLM Validation

After the pipeline, `screen_applicant()` runs deterministic overrides:

1. **`_build_risk_flags()`** — Merges LLM risk flags with deterministic checks, deduplicates, filters hallucinated flags
2. **`_override_recommendation()`** — Overrides LLM when hard rules contradict
3. **`_finalize_explanation()`** — Replaces hallucinated explanations with fact-based templates
4. Appends the mandatory disclaimer

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent flow | Sequential | Simpler to debug and trace than parallel |
| Short-circuit | Intake/Document only | Missing data is fatal; eligibility and risk are advisory |
| Agent context | Full accumulated | Each agent sees all prior outputs for informed decisions |
| State | Stateless | One request = one screening, no history needed |
| Model | 70B parameter | Balances quality and free tier limits (100K TPD) |
| Post-validation | Rule override | Safety net for LLM hallucinations on hard facts |
| Human review | Disclaimer + no auto-action | Compliance: system assists, does not decide |
