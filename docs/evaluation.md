# Evaluation Report

## Evaluation Result Table

| Test Case | Scenario | Expected | Actual | Result |
|---|---|---|---|---|
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

**Overall: 15/15 (100%)**

---

## Evaluation Checklist

### 1. Rule Validation

| Criterion | Status | Evidence |
|---|---|---|
| Age rules applied correctly (21-60) | ✅ | APP006 (age 62) rejected, APP012 (age 19) rejected |
| Employment type validated | ✅ | APP013 (unemployed) rejected |
| Minimum income enforced (20K THB) | ✅ | APP005 (income 15K) rejected |
| DTI ratio calculated and assessed | ✅ | APP007/011/015 flagged as high risk |
| Credit history evaluated | ✅ | APP008 (severe_default) flagged |

### 2. Missing Document Detection

| Criterion | Status | Evidence |
|---|---|---|
| id_card requirement checked | ✅ | APP004 flagged missing id_card |
| salary_slip requirement checked | ✅ | APP003/004 flagged missing salary_slip |
| bank_statement requirement checked | ✅ | APP004 flagged missing bank_statement |
| Short-circuit when documents missing | ✅ | Pipeline stops at Document Agent, returns Need More Info |

### 3. Risk Detection

| Criterion | Status | Evidence |
|---|---|---|
| High DTI flagged | ✅ | APP007/011/015 flagged (DTI > 60%) |
| Bad credit flagged | ✅ | APP008/015 flagged (default/severe_default) |
| Risk flags returned as structured list | ✅ | All outputs include risk_flags array |

### 4. Consistency

| Criterion | Status | Evidence |
|---|---|---|
| Same input produces same output | ✅ | Repeated runs give consistent results (temperature=0) |
| Priority order maintained | ✅ | Missing docs → Reject → High Risk → Proceed per spec |
| Output schema is uniform | ✅ | All 15 outputs have same 9 fields |

---

## Safety & Compliance

### No Automated Final Approval

The system **never** approves or rejects loans automatically. All outputs include:

> "Requires human review: This screening is AI-generated and must be verified by a credit officer before any decision."

The final decision always rests with the human credit officer.

### No Protected Attributes

The system does not collect or evaluate:

- Gender
- Religion
- Race or ethnicity
- Political opinion
- Disability
- Any other protected personal data

The 10 input fields are strictly limited to financial and identity data needed for screening.

---

## Hallucination Prevention

The system uses three layers to prevent hallucination:

1. **Prompt guards** — Every agent prompt instructs "use only provided data, no assumptions" and scopes the agent to its responsibility only (e.g., Document Agent: "Check ONLY documents")
2. **Post-LLM rule validation** — After the pipeline runs, deterministic Python rules (`utils/rules.py`) sanity-check all numeric outputs (DTI ratio, age range, income thresholds). If the LLM output contradicts the rules, the rules override.
3. **Disclaimer** — Every output requires human review, ensuring the credit officer is the final check against any hallucinated information.

---

## Known Limitations

- **Synthetic data only** — All 15 test applicants are fabricated for development. Not tested with real applicant data.
- **No real banking integration** — No connection to credit bureaus, income verification services, or banking APIs.
- **No OCR/document extraction** — Documents must be uploaded manually as text labels, not extracted from PDFs or images.
- **Free-tier rate limits** — Groq API restricts throughput: 30 requests/minute, 100K tokens/day for `llama-3.3-70b-versatile`. Large-scale screening requires a paid tier.
- **Free-tier rate limits** — Groq API restricts throughput: 30 requests/minute, 100K tokens/day for `llama-3.3-70b-versatile`. Large-scale screening requires a paid tier.
- **Thai support is basic** — LLM outputs can be set to Thai via the response language selector, but dropdown data values remain English and no full i18n framework is in place.
- **Sequential processing** — Each applicant takes ~20 seconds (6 sequential LLM calls). Parallel processing would improve throughput.
