# dLoan Fullstack — TODO

> Migration from FastAPI + Streamlit → Django REST + Vue.js + Vuetify
> Branch: `fullstack` (create from `main`)

---

## Phase 0 — Setup ✅

- [x] `git checkout -b fullstack`
- [x] `uv add django djangorestframework django-cors-headers PyJWT`
- [x] Remove `ui/` (Streamlit — replaced by Vue)
- [x] Remove `api/` (FastAPI — replaced by Django)
- [x] Remove `utils/audit.py` (replaced by Django ORM)
- [x] Remove `run.sh` (no longer applicable)
- [x] Keep everything else: `agents/`, `workflow/`, `prompts/`, `utils/rules.py`, `data/`, `models/`

---

## Phase 1 — Django Backend ✅

### 1.1 Project Setup ✅
- [x] Create `django_api/` directory with `manage.py`
- [x] Create `django_api/config/settings.py`, `urls.py`, `wsgi.py`
- [x] Configure settings: DB (SQLite), CORS, INSTALLED_APPS, REST framework
- [x] Set `PYTHONPATH` in Django to include root project (agents, workflow, models, utils)

### 1.2 Accounts App (User Auth) ✅
- [x] Create `django_api/accounts/` app
- [x] Define `User` model (extend AbstractUser or custom)
- [x] Serializers: RegisterSerializer, LoginSerializer, ProfileSerializer
- [x] Views: RegisterView, LoginView (JWT), ProfileView
- [x] URLs: `/api/auth/register`, `/api/auth/login`, `/api/auth/profile`
- [x] Add JWT token auth (PyJWT)

### 1.3 Screening App (Data Models) ✅
- [x] Create `django_api/screening/` app
- [x] Define `Applicant` model (mirrors ApplicantInput fields)
- [x] Define `Screening` model (job_id, status, result, agent_states, timestamp)
- [x] Define `Feedback` model (screening FK, correct, override, comment, timestamp)

### 1.4 Screening App (API Views) ✅
- [x] **Applicant CRUD**: ViewSet (create/list/detail/update/delete)
- [x] **Search/filter**: by name, ID, employment type
- [x] **POST /api/screen**: async screening (ThreadPoolExecutor + job_id)
- [x] **GET /api/screen/{job_id}/status**: poll result (tested with APP001 ✓)
- [x] **POST /api/feedback**: save officer override
- [x] **GET /api/screenings**: paginated audit history with search
- [x] **GET /api/dashboard/summary**: stats endpoint
- [x] **GET /api/screenings/export**: CSV download
- [x] **Seed data**: 20 applicants loaded from `data/applicants.py`

### 1.5 Wire Pipeline ✅
- [x] Import `screen_applicant()` from `workflow/graph.py` in Django view
- [x] Same async pattern: ThreadPoolExecutor + in-memory JOBS dict
- [x] Save result to Django ORM instead of raw SQLite

### 1.6 Docker
- [ ] Create `Dockerfile.django` (same uv base image, gunicorn entrypoint)
- [ ] Update `docker-compose.yml` with django service (port 8000)
- [ ] Add frontend service placeholder

---

## Phase 2 — Vue.js Frontend ✅

### 2.1 Project Setup ✅
- [x] Create `frontend/` with Vite + Vue 3 + Vuetify + Vue Router + Pinia
- [x] Configure Vite proxy for Django API
- [x] Create `plugins/vuetify.js` with theme config
- [x] Create `router/index.js` with route definitions + auth guard
- [x] Create `stores/auth.js` (Pinia) for user state + token

### 2.2 API Client ✅
- [x] Create `api/client.js` — Axios instance with JWT interceptor
- [x] Create `api/auth.js` — login, register, profile, refresh
- [x] Create `api/applicants.js` — CRUD endpoints
- [x] Create `api/screening.js` — POST screen, poll status, feedback
- [x] Create `api/dashboard.js` — stats, history, export

### 2.3 Auth Pages ✅
- [x] `LoginView.vue` — email/password form, token storage
- [x] `RegisterView.vue` — registration form with validation

### 2.4 Layout + Navigation ✅
- [x] `AppNav.vue` — sidebar with routes, user menu, theme toggle (rail)
- [x] `App.vue` / `LayoutView.vue` — layout wrapper with nav + router-view

### 2.5 Applicant CRUD Pages ✅
- [x] `ApplicantListView.vue` — data table with search, pagination
- [x] `ApplicantFormView.vue` — create/edit form
- [x] `ApplicantDetailView.vue` — detail card + screen-now button

### 2.6 Screening Pages ✅
- [x] `ScreenView.vue` — autocomplete + progress + result + agent chain + feedback
- [x] `ScreeningResult.vue` — color-coded result (Proceed=green, Refer/Decline=red)
- [x] `AgentChain.vue` — 6 expandable agent sections with JSON view
- [x] `FeedbackForm.vue` — correct/incorrect + override + comment

### 2.7 Dashboard + History ✅
- [x] `DashboardView.vue` — stats cards (total, agreement, overrides, feedback) + outcome breakdown + risk flags + recent
- [x] `HistoryView.vue` — all screenings table with search + status filter + CSV export

### 2.8 Docker
- [ ] `Dockerfile` for frontend (multi-stage: node build → nginx serve)
- [ ] `Dockerfile.dev` for hot-reload (Vite dev server)
- [ ] Add frontend service to `docker-compose.yml`
- [ ] Add dev overrides to `docker-compose.override.yml`

---

## Phase 3 — Integration + Polish

### 3.1 Testing
- [ ] Smoke test all Django endpoints
- [ ] Smoke test all Vue views
- [ ] Test async screening end-to-end (post → poll → result)
- [ ] Test applicant CRUD flow
- [ ] Test auth flow (register → login → protected routes)

### 3.2 Polish ✅
- [x] Dark/light mode toggle — Vuetify light/dark themes, persisted to localStorage, toggle in AppNav + mobile app bar
- [x] Loading states — skeleton loaders for tables, progress bars for screening, button loading states
- [x] Error handling — Axios interceptor for 401 auto-logout, catch blocks in all API calls, error alerts in views
- [x] Responsive layout — mobile drawer (temporary), desktop rail (permanent), auto-switch via useDisplay

### 3.3 Documentation
- [ ] Update README for fullstack version
- [ ] Document API endpoints
- [ ] Document setup instructions

---

## Reference

Full details in `plan/conversation.md`:
- Architecture: Section 3
- Django endpoints: Section 13
- Vue components: Section 13
- Effort breakdown: Section 13
- Original project features to replicate: Section 3 (Streamlit features)
