# Hallucination Prevention

The system uses three layers to prevent AI hallucination:

## Layer 1 — Prompt Guards

Every agent prompt is designed to restrict the LLM to its specific scope and forbid assumptions:

| Agent | Guard |
|---|---|
| Intake | "Do NOT validate field content — only check presence. valid=false ONLY when fields are missing." |
| Document | "Check ONLY documents. Do NOT check age, income, employment, or credit." |
| Eligibility | Distinguishes HARD rules (must fail → Reject) from SOFT flags (note only) |
| Risk | "Do NOT flag DTI below 60%. Do NOT flag normal/good/fair credit." |
| Recommendation | Decision table enforces priority: missing docs → hard rules → risk → proceed |

All agents share the common instruction: *"use only provided data, no assumptions."*

## Layer 2 — Post-LLM Rule Validation

After the 6-agent pipeline completes, `graph.py` runs `validate_applicant()` from `utils/rules.py` — deterministic Python code that computes hard eligibility facts. The results are compared:

| LLM says | Rules say | Override |
|---|---|---|
| Eligible | Hard rule fails | Force `eligible=False` |
| Ineligible | No hard rule fails | Force `eligible=True` |
| Proceed/HighRisk | Hard rule fails | Force `"Reject / Not Eligible"` |
| Reject | No hard rules fail, DTI ≤ 60%, clean credit | Force `"Proceed"` |
| Reject/NeedInfo | No hard rules fail, has risk flags | Force `"High Risk Review"` |

**Example:** APP008 (age 30, severe_default). The LLM hallucinated "Age below 21" and "Age above 60" — the rule engine overrode both, correctly finding no hard rule violated.

## Layer 3 — Human Review Disclaimer

Every output includes:

> *"Requires human review: This screening is AI-generated and must be verified by a credit officer before any decision."*

This ensures the credit officer always has the final say, catching any residual hallucination that passes the first two layers.
