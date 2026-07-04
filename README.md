# dLoan — Fullstack (Django + Vue)

**Branch:** `Django-version`

An AI-assisted loan screening system with a LangGraph pipeline and full maker-checker workflow. This branch replaces the original FastAPI + Streamlit prototype with Django REST + Vue.js.

**Tech stack:** Python 3.12 + uv | Django + DRF | Vue 3 + Vuetify | LangGraph | Groq/OpenAI | SQLite

---

## Pipeline

```
Applicant → Intake → Document → Eligibility → Risk → Recommendation → Explanation → Officer
                                        ↕ (short-circuit: stops early if intake/doc fails)
```

## Workflow

```
Officer screens → AI completes → Officer submits feedback → status = pending_review
                                                              ↓
                                                Reviewer concurs → approved
                                                Reviewer sends back → sent_back (officer re-screens)
```

---

## Quick Start

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+ (for non-Docker)
- Docker + Docker Compose (for Docker)
- A [Groq](https://console.groq.com) API key (free)

### Run with Docker

```bash
cp .env.example .env
# Edit .env — set GROQ_API_KEY
docker compose up --build
```

Open `http://localhost:5173`. Login with `admin1` / `admin`.

### Run locally (no Docker)

```bash
# First time — install deps, migrate, seed data
./setup.sh

# Any time — start both services
./run.sh
```

Open `http://localhost:5173`. Login with `admin1` / `admin`.

### Run (manual without scripts)

```bash
# 1. Python deps
uv venv && uv sync

# 2. Frontend deps
cd frontend && npm install && cd ..

# 3. Create database tables
PYTHONPATH=. uv run python manage.py migrate

# 4. Seed 20 sample applicants
PYTHONPATH=. uv run python manage.py seed_data

# 5. Start both services
./run.sh
```

### Default Accounts

| Username | Password | Role |
|---|---|---|
| admin1 | admin | Super Admin (absolute) |
| admin | admin123 | Admin |

Register new accounts via the UI — they default to Officer role.

---

## API Endpoints

### Auth (`/api/auth/`)
| Endpoint | Method | Purpose |
|---|---|---|
| `/register/` | POST | Create officer account |
| `/login/` | POST | JWT login (returns access + refresh) |
| `/refresh/` | POST | Refresh access token |
| `/logout/` | POST | Logout (audit log) |
| `/profile/` | GET/PATCH | View/edit profile |
| `/change-password/` | POST | Change password |
| `/users/` | GET/POST | List/create users (admin) |
| `/users/{id}/` | PATCH/DELETE | Update/disable user (admin) |
| `/activity/` | GET | Activity log (admin) |

### Screening (`/api/`)
| Endpoint | Method | Purpose |
|---|---|---|
| `/applicants/` | GET/POST | List/create applicants |
| `/applicants/{id}/` | GET/PATCH/DELETE | Applicant CRUD |
| `/screen/` | POST | Start async screening |
| `/screen/{job_id}/status/` | GET | Poll screening result |
| `/feedback/` | GET/POST | List/submit feedback |
| `/screenings/{id}/review/` | POST | Concur or send back (reviewer) |
| `/screenings/` | GET | Paginated screening history |
| `/screenings/export/` | GET | CSV download |
| `/dashboard/summary/` | GET | Stats + recent screenings |

---

## Project Structure

```
dLoan/
├── agents/          LangGraph agents (intake, document, eligibility, risk, recommendation, explanation)
├── workflow/        LangGraph pipeline graph
├── prompts/         Agent prompt templates (.txt)
├── data/            Sample applicants + expected outcomes
├── models/          Pydantic schemas
├── utils/           Deterministic rules engine
├── django_api/
│   ├── config/      Django settings + urls + wsgi
│   ├── accounts/    User model, JWT auth, user management
│   └── screening/   Screening models, views, serializers, screening service
├── frontend/
│   ├── src/
│   │   ├── views/   12 Vue views (login, dashboard, screen, history, admin, etc.)
│   │   ├── components/  Reusable components (result, agent chain, review form, feedback)
│   │   ├── api/     Axios client with JWT auto-refresh
│   │   ├── stores/  Pinia stores (auth, screening)
│   │   └── router/  Vue Router with auth guards
│   └── package.json
└── manage.py        Django entry point
```

---

## Roles

| Role | Capabilities |
|---|---|
| **Officer** | Screen applicants, submit feedback, edit own profile |
| **Reviewer** | All officer powers + concur/send-back on screenings |
| **Admin** | All reviewer powers + user management |
| **Super Admin** | All admin powers + edit email/password, immune to other admins |

---

## Features

- **JWT auth** with 24h access + 7d refresh tokens, auto-refresh interceptor
- **Maker-Checker workflow** — officer screens → reviewer approves or sends back
- **Activity log** — every action logged with user, IP, timestamp
- **Dark/light mode** — persisted to localStorage
- **Thai language support** — set `response_lang: "th"` in screen request
- **CSV export** — filtered screening history
- **Responsive** — sidebar rail on desktop, drawer on mobile
