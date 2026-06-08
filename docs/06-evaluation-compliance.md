# Evaluation & Compliance

## Evaluation Results

### Test Result Table

20 sample applicants tested against the real Groq LLM (all 6 agents, full pipeline).

| Test Case | Scenario | Expected | Actual | Result |
|-----------|----------|----------|--------|--------|
| APP001 | Fully eligible, all docs | Proceed | Proceed | ✅ Pass |
| APP002 | High income, senior employee | Proceed | Proceed | ✅ Pass |
| APP003 | Missing salary_slip | Need More Info | Need More Info | ✅ Pass |
| APP004 | Missing 2 documents | Need More Info | Need More Info | ✅ Pass |
| APP005 | Income below 20K minimum | Reject / Not Eligible | Reject / Not Eligible | ✅ Pass |
| APP006 | Age exceeds 60 | Reject / Not Eligible | Reject / Not Eligible | ✅ Pass |
| APP007 | High DTI ratio (70%) | High Risk Review | High Risk Review | ✅ Pass |
| APP008 | Severe default on credit | High Risk Review | High Risk Review | ✅ Pass |
| APP009 | Self-employed, stable income | Proceed | Proceed | ✅ Pass |
| APP010 | Business owner, high income | Proceed | Proceed | ✅ Pass |
| APP011 | Borderline DTI (63.6%) | High Risk Review | High Risk Review | ✅ Pass |
| APP012 | Age under 21 | Reject / Not Eligible | Reject / Not Eligible | ✅ Pass |
| APP013 | Invalid employment (unemployed) | Reject / Not Eligible | Reject / Not Eligible | ✅ Pass |
| APP014 | DTI at threshold (60%), meets criteria | Proceed | Proceed | ✅ Pass |
| APP015 | Default record + high DTI (62.8%) | High Risk Review | High Risk Review | ✅ Pass |
| APP016 | Extreme DTI 160%, income just at threshold | High Risk Review | High Risk Review | ✅ Pass |
| APP017 | Unemployed, low income, bad credit, no docs | Reject / Not Eligible | Reject / Not Eligible | ✅ Pass |
| APP018 | Age 80, otherwise excellent profile | Reject / Not Eligible | Reject / Not Eligible | ✅ Pass |
| APP019 | 5M loan on 40K income — extreme loan-to-income | High Risk Review | High Risk Review | ✅ Pass |
| APP020 | Zero income — DTI undefined | Reject / Not Eligible | Reject / Not Eligible | ✅ Pass |

**Overall: 20/20 (100%)**

---

## Evaluation Checklist

### 1. Rule Validation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Age rules applied correctly (21-60) | ✅ | APP006 (age 62) and APP018 (age 80) rejected; APP012 (age 19) rejected |
| Employment type validated | ✅ | APP013 (unemployed) and APP017 (unemployed) rejected |
| Minimum income enforced (20K THB) | ✅ | APP005 (income 15K) rejected |
| DTI ratio calculated and assessed | ✅ | APP007/011/015/016 flagged as high risk |
| Credit history evaluated | ✅ | APP008 (severe_default) flagged as high risk |

### 2. Missing Document Detection

| Criterion | Status | Evidence |
|-----------|--------|----------|
| id_card requirement checked | ✅ | APP004 flagged missing id_card |
| salary_slip requirement checked | ✅ | APP003/004 flagged missing salary_slip |
| bank_statement requirement checked | ✅ | APP004 flagged missing bank_statement |
| Short-circuit when documents missing | ✅ | Pipeline stops at Document Agent, returns "Need More Info" immediately |

### 3. Risk Detection

| Criterion | Status | Evidence |
|-----------|--------|----------|
| High DTI flagged | ✅ | APP007/011/015/016 flagged (DTI > 60%) |
| Bad credit flagged | ✅ | APP008/015 flagged (default/severe_default) |
| Risk flags returned as structured list | ✅ | All outputs include risk_flags array |

### 4. Consistency

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Same input produces same output | ✅ | Repeated runs give consistent results (temperature=0) |
| Priority order maintained | ✅ | Missing docs → Reject → High Risk → Proceed per specification |
| Output schema is uniform | ✅ | All outputs have identical field structure |

---

## Safety & Compliance

### Critical Safeguards

#### No Automated Loan Decisions

The system MUST NOT approve or reject loans without human review.

**How this is enforced:**
1. All recommendations are generated as suggestions, not final decisions
2. Every output includes the disclaimer: *"Requires human review: This screening is AI-generated and must be verified by a credit officer before any decision."*
3. The Streamlit UI presents results as guidance — there is no "auto-approve" or "auto-reject" action
4. The FastAPI endpoint returns only screening data; it does not execute any loan processing

#### No Protected Attributes

The system MUST NOT collect, store, or evaluate:

- Gender
- Religion
- Race or ethnicity
- Political opinion
- Disability
- Sexual orientation
- Marital status
- Any other protected characteristic

**How this is enforced:**
1. The `ApplicantInput` schema (10 fields) contains only financial and identity data required for screening
2. No prompts reference or request protected attributes
3. No data collection mechanisms exist beyond the defined input schema
4. The system has no access to external databases that could contain protected information

#### Data Privacy

- Applicant data is stored in a SQLite audit log (`screening_audit.db`) when a screening completes. This database is created automatically and should be included in backup/retention policies.
- All processing occurs server-side; no data is sent to third parties beyond the LLM API for inference
- API keys are stored in `.env` and excluded from version control via `.gitignore`

---

## Known Limitations

### Data & Integration

- **Synthetic data only** — All 20 test applicants are fabricated for development. Not validated with real applicant data or production loan workflows.
- **No real banking integration** — No connection to credit bureaus, income verification services, or banking APIs. All applicant data must be entered manually.
- **No OCR or document extraction** — Documents are represented as text labels (`id_card`, `salary_slip`, `bank_statement`). No PDF/image parsing is performed.
- **Audit log is basic** — Every screening is logged to SQLite with timestamps and full agent states, but there is no user authentication or officer identity tracking.

### Performance & Scalability

- **Sequential processing** — Each screening makes 6 sequential LLM calls (~20 seconds total). Batch or parallel processing would improve throughput.
- **Free-tier rate limits** — Groq free tier: 30 requests/minute and 100K tokens/day for `llama-3.3-70b-versatile`. A paid tier is needed for production-scale screening.

### Language

- **Thai support is basic** — LLM responses can be set to Thai via the response language selector, but dropdown data values (employment types, credit history, document names) remain in English. A full production-grade i18n system would need deeper localization.

### Accuracy

- **LLM risk flags may be noisy** — Even careful prompts occasionally produce false positive risk flags (e.g., normal credit flagged, income flagged below specified range). Rule-based filtering strips demonstrably wrong flags, but residual noise may remain in edge cases.
- **Borderline cases** — Applicants with DTI exactly at 60% or income exactly at 20,000 THB may be inconsistently classified. The rule engine defaults to passing these, but business policy may differ.

### Compliance

- **No user authentication** — The API and UI have no login system. Audit logs record screening data and timestamps but do not identify which officer performed the review.

---

## Best Practices for Deployment

| Practice | Recommendation |
|----------|---------------|
| Authentication | Add API key or OAuth before exposing the endpoint publicly |
| Rate limiting | Configure reverse proxy rate limits to prevent abuse |
| Audit logging | Log all screening requests, responses, and officer decisions |
| Human review | Always require a credit officer to confirm or override recommendations |
| Model oversight | Periodically review LLM outputs for drift or bias |
| Data retention | Define and enforce data retention policies for stored applications |
