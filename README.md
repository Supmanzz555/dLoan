# dLoan — Agentic Loan Applicant Screening

An AI-assisted loan screening system with 6 LangGraph agents that helps credit officers evaluate loan applications. Validates completeness, checks eligibility, detects risk signals, and generates recommendations — always leaving the final decision to a human.

**Tech stack:** Python 3.12 + uv | FastAPI | Streamlit | LangGraph | Groq/OpenAI | Pydantic | SQLite

---

## Pipeline

```
Applicant → Intake → Document → Eligibility → Risk → Recommendation → Explanation → Officer
                                        ↕ (short-circuit: stops early if intake/doc fails)
```

Short-circuit: if intake finds missing fields or document finds missing documents, the pipeline stops immediately and returns "Need More Info" — saving 4 unnecessary LLM calls.

## Classification Outcomes

| Outcome | Meaning |
|---------|---------|
| **Proceed** | Eligible, no significant risk flags → manual review |
| **Need More Info** | Missing required fields or documents |
| **Reject / Not Eligible** | Hard rule failure (age, income, employment) |
| **High Risk Review** | Risk signals detected (DTI > 60%, bad credit, etc.) |

---

## Quick Start

### 1. Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- An API key — [Groq](https://console.groq.com) (free) or [OpenAI](https://platform.openai.com/api-keys)

### 2. Setup

```bash
git clone <repo-url>
cd dLoan
uv venv && uv sync
cp .env.example .env
# Edit .env — set LLM_PROVIDER and your API key
```

### 3. Run

```bash
# Both API (:8000) + UI (:8501) in one terminal
./run.sh

# Or via Docker
docker compose up
```

### 4. Test

```bash
PYTHONPATH=. uv run pytest                     # 20 applicants, real LLM
PYTHONPATH=. uv run python workflow/graph.py   # pipeline smoke test
```

## LLM Provider Configuration

Set one variable in `.env`. No code changes needed.

```bash
LLM_PROVIDER=groq                    # or "openai"
GROQ_API_KEY=gsk_your_key_here       # https://console.groq.com
OPENAI_API_KEY=sk-your_key_here      # https://platform.openai.com (if provider=openai)
```

| Provider | Default Model | Free Tier | Best For |
|----------|--------------|-----------|----------|
| **Groq** (default) | `llama-3.3-70b-versatile` | 100K TPD, 30 RPM | Testing, low volume |
| **OpenAI** | `gpt-4o-mini` | Paid | Higher throughput, production |

The `chat.completions.create()` interface is identical between both SDKs. The file `agents/llm_client.py` handles the switch. No other code changes needed.

---

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/screen` | POST | Submit applicant → returns `job_id` |
| `/screen/{id}/status` | GET | Poll result (progress + per-agent outputs + final result) |
| `/screen/batch` | POST | Submit multiple applicants |
| `/feedback` | POST | Officer override + comment |
| `/audit/{id}` | GET | Screening history for an applicant |
| `/audit/summary` | GET | Dashboard stats (totals, outcomes, agreement, flags) |
| `/health` | GET | Health check |

Set `response_lang: "th"` in the request body for Thai-language explanations and risk flags.

---

## Project Structure

```
dLoan/
├── agents/          llm_client.py + 6 agents (intake, document, eligibility, risk, recommend, explain)
├── workflow/        LangGraph pipeline + post-LLM validation
├── api/             FastAPI (routes, async screening, audit, feedback)
├── ui/              app.py (screening form + result + agent chain) + pages/dashboard.py
├── prompts/         6 prompt templates (.txt, one per agent)
├── data/            20 sample applicants with expected outcomes
├── utils/           rules.py (deterministic eligibility) + audit.py (SQLite)
├── models/          Pydantic schemas (ApplicantInput, ScreeningResult)
├── docs/            Business problem, architecture, evaluation, safety, limitations, demo script
└── tests/           Integration test (FastAPI TestClient, real LLM)
```

---

## Key Features

### Hallucination Prevention (4 Layers)

| Layer | What It Does |
|-------|-------------|
| 1. Eligibility correction | If LLM says "ineligible" but rules pass → force eligible. If LLM says "eligible" but hard rules fail → force ineligible. |
| 2. Flag filtering | Strips LLM risk flags that contradict deterministic checks (e.g., DTI 37% flagged as "exceeds 60%" → removed). |
| 3. Recommendation override | Python rules determine final 4-class outcome (DTI > 60% → High Risk, hard rules fail → Reject, etc.). |
| 4. Explanation template | When recommendation is corrected, replaces hallucinated LLM explanation with fact-based text. |

### Agent Chain UI

After each screening, expand 6 collapsible sections showing per-agent raw output with status icons:
- **Intake** — ✅ / missing fields
- **Document** — ✅ / missing documents
- **Eligibility** — ✅ / ❌ if ineligible
- **Risk** — ⚠️ flags
- **Recommendation** — ✅ / override if rules corrected
- **Explanation** — 📝 full text

### Audit Log + Feedback

- Every screening logged to SQLite with: input data, result, and all 6 agent states
- Officers mark results correct/incorrect with override recommendation + optional comment
- Dashboard shows: agreement rate, outcome breakdown, top risk flags, recent screenings, and recent officer overrides

### Thai Language

Set `response_lang: "th"` → LLM generates Thai explanations, risk flags, and next action. Classification fields (recommendation, confidence, eligibility, DTI) remain English — they're set by deterministic Python rules, not the LLM.

### Short-Circuit

Missing intake fields or required documents → pipeline stops at Document agent, returns "Need More Info." No eligibility, risk, recommendation, or explanation calls are made. Saves ~4 LLM calls per incomplete application.

---

## Safety

- **No automated decisions:** Every output includes *"Requires human review: This screening is AI-generated and must be verified by a credit officer before any decision."*
- **No protected attributes:** Schema excludes gender, religion, race, ethnicity, politics, disability, or irrelevant personal data.
- **Post-LLM validation:** Four layers of deterministic overrides ensure classification correctness regardless of LLM output.
- **Audit trail:** SQLite logs every screening with full agent states. Officer feedback tracked for compliance.

---

## Testing

```bash
# Full integration test (20 applicants, real LLM)
PYTHONPATH=. uv run pytest

# Per-agent self-tests (isolated, real LLM)
PYTHONPATH=. uv run python agents/intake_agent.py
PYTHONPATH=. uv run python agents/document_agent.py
PYTHONPATH=. uv run python agents/eligibility_agent.py
PYTHONPATH=. uv run python agents/risk_agent.py
PYTHONPATH=. uv run python agents/recommendation_agent.py
PYTHONPATH=. uv run python agents/explanation_agent.py
# Pipeline smoke test
PYTHONPATH=. uv run python workflow/graph.py
```
