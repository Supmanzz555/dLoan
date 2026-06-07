# Known Limitations

## Data & Integration

- **Synthetic data only** — All 15 test applicants are fabricated for development. Not validated with real applicant data or production loan workflows.
- **No real banking integration** — No connection to credit bureaus, income verification services, or banking APIs. All applicant data must be entered manually.
- **No OCR or document extraction** — Documents are represented as text labels (`id_card`, `salary_slip`, `bank_statement`). No PDF/image parsing is performed.
- **Audit log is basic** — Every screening is logged to SQLite with timestamps and full agent states, but there is no user authentication or officer identity tracking.

## Performance & Scalability

- **Sequential processing** — Each screening makes 6 sequential LLM calls (~20 seconds total). Batch or parallel processing would improve throughput.
- **Free-tier rate limits** — Current Groq free tier: 30 requests/minute and 100K tokens/day for `llama-3.3-70b-versatile`. A paid tier is needed for production-scale screening.
- **Free-tier rate limits** — Current Groq free tier: 30 requests/minute and 100K tokens/day for `llama-3.3-70b-versatile`. A paid tier is needed for production-scale screening.

## Language

- **Thai support is basic** — LLM responses can be set to Thai via the response language selector, but dropdown data values (employment types, credit history, document names) remain in English. A full production-grade i18n system would need deeper localization.

## Accuracy

- **LLM risk flags may be noisy** — Even careful prompts occasionally produce false positive risk flags (e.g., normal credit flagged, income flagged below specified range). Rule-based filtering strips demonstrably wrong flags, but residual noise may remain in edge cases.
- **Borderline cases** — Applicants with DTI exactly at 60% or income exactly at 20,000 THB may be inconsistently classified. The rule engine defaults to passing these, but business policy may differ.

## Compliance

- **No user authentication** — The API and UI have no login system. Audit logs record screening data and timestamps but do not identify which officer performed the review.
