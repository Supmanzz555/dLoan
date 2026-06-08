# GenAI Output

## Output Schema

Every screening produces a structured JSON output with 9 fields:

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | `applicant_id` | string | Matches the input applicant ID |
| 2 | `recommendation` | string | One of 4 outcomes: `Proceed`, `Need More Info`, `Reject / Not Eligible`, `High Risk Review` |
| 3 | `confidence` | string | `Low`, `Medium`, or `High` |
| 4 | `eligibility_status` | string | Summary of rule check (e.g., "Eligible", "Income below minimum threshold") |
| 5 | `debt_to_income_ratio` | string | DTI as percentage (e.g., "68%"), `null` if income is zero |
| 6 | `risk_flags` | array[string] | Detected risk signals (empty array if none) |
| 7 | `missing_documents` | array[string] | Required docs not provided (empty array if all present) |
| 8 | `explanation` | string | Human-readable reasoning with "Requires human review" disclaimer |
| 9 | `next_action` | string | Suggested next step for the credit officer |

---

## Example Outputs

### APP001 — Proceed (Eligible, Clean)

```json
{
  "applicant_id": "APP001",
  "recommendation": "Proceed",
  "confidence": "high",
  "eligibility_status": "Eligible",
  "debt_to_income_ratio": "34.29%",
  "risk_flags": [],
  "missing_documents": [],
  "explanation": "The applicant, Somchai, is eligible for the loan with a low risk level. The debt-to-income ratio is 34.29%, which is within the acceptable range. All required fields and documents are present, and the applicant meets the eligibility criteria.\n\nRequires human review: This screening is AI-generated and must be verified by a credit officer before any decision.",
  "next_action": "Proceed to manual review by credit officer"
}
```

### APP003 — Need More Info (Missing Document)

```json
{
  "applicant_id": "APP003",
  "recommendation": "Need More Info",
  "confidence": "High",
  "eligibility_status": "Incomplete application",
  "debt_to_income_ratio": null,
  "risk_flags": [],
  "missing_documents": ["salary_slip"],
  "explanation": "Application is incomplete. Required information or documents are missing.",
  "next_action": "Contact applicant to provide missing information."
}
```

### APP005 — Reject / Not Eligible (Income Below Threshold)

```json
{
  "applicant_id": "APP005",
  "recommendation": "Reject / Not Eligible",
  "confidence": "high",
  "eligibility_status": "Income below minimum threshold",
  "debt_to_income_ratio": "33.33%",
  "risk_flags": [],
  "missing_documents": [],
  "explanation": "The applicant, Malee, is not eligible for the loan due to a monthly income of 15,000 THB, which is below the minimum threshold of 20,000 THB. All documents are present, but the hard income rule is not satisfied.\n\nRequires human review: This screening is AI-generated and must be verified by a credit officer before any decision.",
  "next_action": "Notify applicant that minimum income requirement is not met"
}
```

### APP007 — High Risk Review (High DTI)

```json
{
  "applicant_id": "APP007",
  "recommendation": "High Risk Review",
  "confidence": "high",
  "eligibility_status": "Eligible",
  "debt_to_income_ratio": "70%",
  "risk_flags": ["Debt-to-income ratio ABOVE 60%"],
  "missing_documents": [],
  "explanation": "The applicant, Thana, passes all hard eligibility rules (age 38, income 50,000 THB, employee) but has a high debt-to-income ratio of 70%. Credit history is normal. The elevated DTI warrants careful manual review by a senior credit officer.\n\nRequires human review: This screening is AI-generated and must be verified by a credit officer before any decision.",
  "next_action": "Assign to senior credit officer for manual review"
}
```

### APP008 — High Risk Review (Bad Credit)

```json
{
  "applicant_id": "APP008",
  "recommendation": "High Risk Review",
  "confidence": "high",
  "eligibility_status": "Passes all rules",
  "debt_to_income_ratio": "50%",
  "risk_flags": ["Credit history shows severe default"],
  "missing_documents": [],
  "explanation": "The applicant, Pichai, passes all hard eligibility rules (age 30, income 40,000 THB, employee, DTI 50%). However, a recent severe default on credit history is a significant risk signal requiring careful manual review by a senior credit officer.\n\nRequires human review: This screening is AI-generated and must be verified by a credit officer before any decision.",
  "next_action": "Assign to senior credit officer for manual review of credit history issues"
}
```

---

## Hallucination Prevention

### Why Hallucination Prevention Matters

LLMs can confidently output incorrect information — claiming an applicant is ineligible when they are eligible, inventing risk flags, or fabricating numbers. In loan screening, these hallucinations could lead to incorrect rejections or approvals. The system uses three defense layers:

### Layer 1 — Prompt Guards

Every agent prompt restricts the LLM to its specific scope and forbids assumptions:

| Agent | Guard |
|-------|-------|
| **Intake** | "Do NOT validate field content — only check presence. valid=false ONLY when fields are missing." |
| **Document** | "Check ONLY documents. Do NOT check age, income, employment, or credit." |
| **Eligibility** | Distinguishes HARD rules (must fail → Reject) from SOFT flags (note only). "Soft flags alone must NOT cause eligible=false." |
| **Risk** | "Do NOT flag DTI below 60%. Do NOT flag normal/good/fair credit." |
| **Recommendation** | Decision table enforces priority: missing docs → hard rules → risk → proceed. "Eligibility overrides risk when hard rules fail." |

All agents share: *"use only provided data, no assumptions."*

### Layer 2 — Post-LLM Rule Validation

After the 6-agent pipeline completes, `workflow/graph.py` runs deterministic Python rules (`utils/rules.py`) that compute hard eligibility facts. The results override the LLM when they conflict:

| LLM says | Rules say | Override |
|----------|-----------|----------|
| Eligible | Hard rule fails | Force `eligible=False` |
| Ineligible | No hard rule fails | Force `eligible=True` |
| Proceed/HighRisk | Hard rule fails | Force "Reject / Not Eligible" |
| Reject | No hard rules fail, DTI ≤ 60%, clean credit | Force "Proceed" |
| Reject/NeedInfo | No hard rules fail, has risk flags | Force "High Risk Review" |

**Real example:** APP008 (age 30, severe_default). The LLM hallucinated "Age below 21" and "Age above 60" — the rule engine overrode both, correctly finding no hard rule violated.

### Layer 3 — Human Review Disclaimer

Every output includes:

> *"Requires human review: This screening is AI-generated and must be verified by a credit officer before any decision."*

This ensures the credit officer always has the final say, catching any residual hallucination that passes the first two layers.

### Summary

```
LLM Output → Prompt Guards (Layer 1) → Rule Validation (Layer 2) → Disclaimer (Layer 3) → Officer
                 scope limits              deterministic overrides          human check
```

The rule engine always wins on hard, calculable facts (age, income, DTI). The LLM handles interpretation, risk detection, and explanation — areas where human language is needed and deterministic rules aren't sufficient.
