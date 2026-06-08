# Data Design

## Input Schema

| Field | Type | Description |
|-------|------|-------------|
| `applicant_id` | string | Unique identifier for the applicant (e.g., APP001) |
| `name` | string | Applicant's full name |
| `age` | integer | Applicant's age in years |
| `employment_type` | string | Type of employment: `employee`, `self-employed`, or `business_owner` |
| `monthly_income` | float | Monthly income in THB |
| `monthly_debt` | float | Monthly debt obligations in THB |
| `requested_loan_amount` | float | Requested loan amount in THB |
| `credit_history` | string | Credit history status: `normal`, `good`, `fair`, `default`, `severe_default`, `bad` |
| `uploaded_documents` | array[string] | List of uploaded document types: `id_card`, `salary_slip`, `bank_statement` |
| `notes` | string (optional) | Additional notes or context about the applicant |
| `response_lang` | string (optional) | Response language: `"en"` (default) or `"th"` |

## Output Schema

| Field | Type | Description |
|-------|------|-------------|
| `applicant_id` | string | Unique identifier referencing the screened applicant |
| `recommendation` | string | Screening outcome: `Proceed`, `Need More Info`, `Reject / Not Eligible`, or `High Risk Review` |
| `confidence` | string | Confidence level: `Low`, `Medium`, or `High` |
| `eligibility_status` | string | Summary of eligibility check result |
| `debt_to_income_ratio` | string | DTI ratio as percentage (e.g., "68%"), null if income is zero |
| `risk_flags` | array[string] | List of detected risk flags |
| `missing_documents` | array[string] | List of required documents not provided |
| `explanation` | string | Human-readable explanation of the screening decision |
| `next_action` | string | Suggested next step for the credit officer |

---

## Sample Applicants

20 sample applicants (APP001–APP020) covering all required scenario types.

### Eligible — Proceed

| ID | Name | Age | Employment | Income | Debt | Credit | Docs | Notes |
|----|------|-----|------------|--------|------|--------|------|-------|
| APP001 | Somchai | 32 | employee | 35,000 | 12,000 | normal | all 3 | Stable, meets all criteria |
| APP002 | Pricha | 45 | employee | 55,000 | 15,000 | good | all 3 | Senior employee, high income |
| APP009 | Chalerm | 38 | self-employed | 45,000 | 15,000 | good | all 3 | Stable self-employed |
| APP010 | Nithi | 42 | business_owner | 60,000 | 20,000 | good | all 3 | Business owner, high income |
| APP014 | Rung | 36 | employee | 40,000 | 24,000 | fair | all 3 | DTI at threshold (60%) |

### Missing Information — Need More Info

| ID | Name | Issue | Expected |
|----|------|-------|----------|
| APP003 | Nattapong | Missing salary_slip | Need More Info |
| APP004 | Somsak | Missing 2 documents | Need More Info |

### Rule Failure — Reject / Not Eligible

| ID | Name | Age | Employment | Income | Issue | Expected |
|----|------|-----|------------|--------|-------|----------|
| APP005 | Malee | 35 | employee | 15,000 | Income below 20K | Reject |
| APP006 | Sompong | 62 | employee | 50,000 | Age exceeds 60 | Reject |
| APP012 | Anon | 19 | employee | 25,000 | Age under 21 | Reject |
| APP013 | Wichai | 40 | unemployed | 30,000 | Invalid employment | Reject |
| APP017 | Kwan | 25 | unemployed | 0 | Unemployed, no income, bad credit, no docs | Reject |
| APP018 | Pramote | 80 | employee | 80,000 | Age exceeds 60 | Reject |
| APP020 | Sinjai | 35 | employee | 0 | Zero income | Reject |

### Risk Flags — High Risk Review

| ID | Name | Income | Debt | DTI | Credit | Issue | Expected |
|----|------|--------|------|-----|--------|-------|----------|
| APP007 | Thana | 50,000 | 35,000 | 70% | normal | High DTI | High Risk Review |
| APP008 | Pichai | 40,000 | 20,000 | 50% | severe_default | Bad credit | High Risk Review |
| APP011 | Mana | 55,000 | 35,000 | 63.6% | fair | Borderline DTI | High Risk Review |
| APP015 | Sommai | 43,000 | 27,000 | 62.8% | default | Default + high DTI | High Risk Review |
| APP016 | Thawatchai | 20,000 | 32,000 | 160% | normal | Extreme DTI | High Risk Review |
| APP019 | Preecha | 40,000 | 10,000 | 25% | normal | Extreme loan-to-income (5M on 40K) | High Risk Review |

---

## Required Documents

Three document types are checked by the system:

| Document | Description |
|----------|-------------|
| `id_card` | Government-issued identification card |
| `salary_slip` | Recent salary slip or income proof |
| `bank_statement` | Recent bank statement (usually 3-6 months) |

If any of these are missing from `uploaded_documents`, the pipeline short-circuits and returns "Need More Info".

---

## Data Dictionary

### Input Fields

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `applicant_id` | `str` | required | Unique identifier (e.g., APP001) |
| `name` | `str` | required | Applicant's full name |
| `age` | `int` | 0–150 | Applicant's age in years |
| `employment_type` | `str` | required | `employee`, `self-employed`, or `business_owner` |
| `monthly_income` | `float` | ≥ 0 | Monthly income in THB |
| `monthly_debt` | `float` | ≥ 0 | Monthly debt obligations in THB |
| `requested_loan_amount` | `float` | ≥ 0 | Requested loan amount in THB |
| `credit_history` | `str` | required | `normal`, `good`, `fair`, `default`, `severe_default` |
| `uploaded_documents` | `list[str]` | default `[]` | e.g., `["id_card", "salary_slip"]` |
| `notes` | `Optional[str]` | optional | Additional context |
| `response_lang` | `str` | optional, default `"en"` | `"en"` or `"th"` |

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `applicant_id` | `str` | Matches input applicant_id |
| `recommendation` | `str` | One of 4 outcomes (see classification table) |
| `confidence` | `str` | `Low`, `Medium`, `High` |
| `eligibility_status` | `str` | Summary of rule check: "Eligible", "Income below threshold", etc. |
| `debt_to_income_ratio` | `Optional[str]` | Percentage string or null (zero income) |
| `risk_flags` | `list[str]` | Detected risk signals (empty if none) |
| `missing_documents` | `list[str]` | Required docs not provided (empty if all present) |
| `explanation` | `str` | Human-readable reasoning |
| `next_action` | `str` | Suggested officer action |

---

## Classification Outcomes

| Outcome | Meaning |
|---------|---------|
| **Proceed** | Eligible for manual review |
| **Need More Info** | Missing or unclear information |
| **Reject / Not Eligible** | Fails basic eligibility rules |
| **High Risk Review** | Requires careful manual review |
