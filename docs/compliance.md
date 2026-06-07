# Risk & Compliance Notes

## Critical Safeguards

### No Automated Loan Decisions

The system MUST NOT approve or reject loans without human review.

**How this is enforced:**
1. All recommendations are generated as suggestions, not final decisions
2. Every output includes the disclaimer: *"Requires human review: This screening is AI-generated and must be verified by a credit officer before any decision."*
3. The Streamlit UI presents results as guidance — there is no "auto-approve" or "auto-reject" action
4. The FastAPI endpoint returns only screening data; it does not execute any loan processing

### Protected Attributes

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

---

## Data Privacy

- Applicant data is stored in a SQLite audit log (`screening_audit.db`) when a screening completes. This database is created automatically and should be included in backup/retention policies.
- All processing occurs server-side; no data is sent to third parties beyond the Groq API for LLM inference
- API keys are stored in `.env` and excluded from version control via `.gitignore`

---

## Best Practices for Deployment

| Practice | Recommendation |
|---|---|
| Authentication | Add API key or OAuth before exposing the endpoint publicly |
| Rate limiting | Configure reverse proxy rate limits to prevent abuse |
| Audit logging | Log all screening requests, responses, and officer decisions |
| Human review | Always require a credit officer to confirm or override recommendations |
| Model oversight | Periodically review LLM outputs for drift or bias |
| Data retention | Define and enforce data retention policies for stored applications |
