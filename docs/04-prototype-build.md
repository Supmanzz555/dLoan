# Prototype Build

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit (port 8501) |
| API | FastAPI (port 8000) |
| Orchestration | LangGraph |
| LLM | Groq — llama-3.3-70b-versatile (default) |
| Fallback LLM | OpenAI — gpt-4o-mini (optional) |
| Schema | Pydantic |
| Validation | Deterministic Python rules |
| Database | SQLite (audit log) |
| Container | Docker + docker-compose |
| Package mgmt | uv (Python 3.12+) |
| Testing | pytest (real LLM integration) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/screen` | Submit applicant for screening (returns `job_id`) |
| `GET` | `/screen/{job_id}/status` | Poll screening progress and result |
| `POST` | `/screen/batch` | Submit multiple applicants |
| `POST` | `/feedback` | Record officer override + comment |
| `GET` | `/audit/{applicant_id}` | Screening history for an applicant |
| `GET` | `/audit/summary` | Dashboard stats (totals, outcomes, agreement, flags) |
| `GET` | `/audit` | Paginated list of all screenings |
| `GET` | `/health` | Health check |

Screening is **asynchronous**: `POST /screen` returns immediately with a `job_id`. The client polls `GET /screen/{job_id}/status` until the result is ready. Progress includes which agent is currently running.

### API Example

```bash
curl -X POST http://localhost:8000/screen \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP001",
    "name": "Somchai",
    "age": 32,
    "employment_type": "employee",
    "monthly_income": 35000,
    "monthly_debt": 12000,
    "requested_loan_amount": 200000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"]
  }'
```

### Response

```json
{
  "job_id": "abc123",
  "status": "queued"
}
```

Poll status:

```bash
curl http://localhost:8000/screen/abc123/status
```

```json
{
  "status": "done",
  "progress": ["Intake", "Document", "Eligibility", "Risk", "Recommendation", "Explanation"],
  "result": {
    "applicant_id": "APP001",
    "recommendation": "Proceed",
    "confidence": "High",
    "eligibility_status": "Eligible",
    "debt_to_income_ratio": "34.29%",
    "risk_flags": [],
    "missing_documents": [],
    "explanation": "...",
    "next_action": "Proceed to manual review by credit officer",
    "screening_id": 1
  }
}
```

---

## UI Features

The Streamlit UI provides:

- **Applicant form** — All input fields with validation
- **Sample dropdown** — Load any of APP001–APP020 to populate fields instantly
- **Progress bar** — Shows current agent as screening runs
- **Results panel** — Color-coded recommendation, all 9 output fields, risk flags, explanation
- **Agent Chain UI** — 6 expandable collapsible sections showing per-agent raw output:

    | Agent | Status Icon |
    |---|---|
    | Intake | ✅ / missing fields |
    | Document | ✅ / missing documents |
    | Eligibility | ✅ / ❌ if ineligible |
    | Risk | ⚠️ flags |
    | Recommendation | ✅ / override notice |
    | Explanation | 📝 full text |

- **Feedback form** — After screening, officers mark "Yes, correct" or "No, needs correction" with optional override recommendation and comment
- **Dashboard page** — Total screenings, agreement %, overrides count, outcome distribution chart, top risk flags, recent screenings, recent overrides
- **Error handling** — Groq 429 rate limit shows "API busy, try again"; other errors show friendly messages

---

## Project Structure

```
dLoan/
├── agents/          llm_client.py + 6 agents (intake, document, eligibility, risk, recommend, explain)
├── workflow/        LangGraph pipeline + post-LLM validation
├── api/             FastAPI (routes, async screening, audit, feedback)
├── ui/              app.py (screening form + agent chain) + pages/dashboard.py
├── prompts/         6 prompt templates (.txt, one per agent)
├── data/            20 sample applicants with expected outcomes
├── utils/           rules.py (deterministic eligibility) + audit.py (SQLite)
├── models/          Pydantic schemas (ApplicantInput, ScreeningResult)
├── docs/            Documentation (this site)
├── tests/           Integration test (FastAPI TestClient, real LLM)
├── Gif/             Demo GIFs
├── Dockerfile       Container build
├── docker-compose.yml        Multi-service (production)
├── docker-compose.override.yml  Dev mode (bind mounts + hot reload)
├── run.sh           One-command local startup
├── pyproject.toml   Project metadata and dependencies
└── mkdocs.yml       Documentation config
```

---

## Setup & Run

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- An API key — [Groq](https://console.groq.com) (free) or [OpenAI](https://platform.openai.com/api-keys)

### Local Setup

```bash
git clone <repo-url>
cd dLoan
uv venv && uv sync
cp .env.example .env
# Edit .env — set LLM_PROVIDER and your API key
```

### Run

```bash
# Both API (:8000) + UI (:8501) in one terminal
./run.sh

# Or via Docker
docker compose up

# Via Docker (production mode, no bind mounts)
docker compose -f docker-compose.yml up
```

### Test

```bash
# Full integration test (20 applicants, real LLM)
PYTHONPATH=. uv run pytest

# Per-agent self-tests (isolated, real LLM)
PYTHONPATH=. uv run python agents/intake_agent.py

# Pipeline smoke test
PYTHONPATH=. uv run python workflow/graph.py
```

---

## LLM Provider Configuration

Set one variable in `.env`:

```bash
LLM_PROVIDER=groq                    # or "openai"
GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=sk-your_key_here      # if provider=openai
```

| Provider | Default Model | Free Tier | Best For |
|----------|--------------|-----------|----------|
| **Groq** (default) | `llama-3.3-70b-versatile` | 100K TPD, 30 RPM | Testing, low volume |
| **OpenAI** | `gpt-4o-mini` | Paid | Higher throughput, production |

---

## Docker

```yaml
# docker-compose up → dev mode (bind mounts + hot reload)
# docker-compose -f docker-compose.yml up → production mode (copy only)

services:
  api:   FastAPI on :8000, uvicorn --reload in dev
  ui:    Streamlit on :8501, calls api:8000
```

Key design: the Dockerfile uses `UV_PROJECT_ENVIRONMENT=/opt/venv` to keep the container's virtual environment separate from the host's `.venv/`, ensuring Docker never creates root-owned files on the host via bind mounts.
