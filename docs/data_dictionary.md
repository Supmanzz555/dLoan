# Data Dictionary

## Input Fields

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

## Output Fields

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
