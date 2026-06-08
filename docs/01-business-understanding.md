# Business Understanding

## Problem Statement

dLoan is a financial services company that receives many loan applications each day. Credit officers spend too much time reviewing documents, checking eligibility, summarizing risk, and deciding which applicants should move forward. The company wants a Gen AI agentic application to help filter applicants for a loan product.

### Current Pain Points

1. **Slow turnaround** — Each application takes significant time to review, creating backlogs during peak periods.
2. **Inconsistent decisions** — Different officers may apply eligibility rules differently, leading to inconsistent outcomes.
3. **Repetitive verification** — Officers spend hours repeatedly checking the same required documents (ID card, salary slip, bank statement) across applications.
4. **Missing information delays** — Applications with incomplete data require back-and-forth communication, further slowing processing.
5. **Hard to summarize risk** — Quickly understanding an applicant's risk profile requires scanning multiple documents and data points.

### How AI Assistance Helps

- **Automate the repetitive parts** — Field validation, document checks, and rule application happen instantly, freeing officers for higher-value work.
- **Standardize decisions** — The same rules are applied consistently to every applicant, eliminating subjective variation.
- **Flag issues immediately** — Missing documents or hard rule violations are detected at the start, so officers don't waste time on incomplete applications.
- **Summarize risk clearly** — Risk flags, DTI ratios, and credit history are extracted and presented in a structured format.
- **Generate human-readable explanations** — Officers get plain-language reasoning they can use in communications with applicants and management.

### Impact

| Before | After |
|--------|-------|
| Manual document checking per application | Automated document verification in seconds |
| Inconsistent rule application | Standardized eligibility checks |
| Slow identification of missing data | Immediate "Need More Info" feedback |
| Manual risk summary | Structured risk flags + DTI ratio |
| No audit trail of screening reasoning | AI-generated explanation for every decision |

---

## User Personas

### 1. Credit Officer

**Responsibilities:**
- Review loan applications manually
- Verify submitted documents
- Assess applicant risk and eligibility
- Approve or reject loans within authority limits
- Escalate high-risk cases to senior management

**Pain points:**
- Spends hours manually checking the same documents repeatedly
- Inconsistent decisions when rules are applied subjectively
- Difficult to quickly summarize applicant risk
- Missing information causes back-and-forth delays

**Goals:**
- Screen applicants faster with AI-assisted recommendations
- Reduce manual document checking overhead
- Get clear, consistent risk summaries per applicant
- Maintain final decision authority — system assists, not decides

### 2. Loan Operations Team

**Responsibilities:**
- Oversee the loan processing workflow
- Ensure compliance with lending policies
- Track application status and processing times
- Generate reports on application volume and outcomes

**Pain points:**
- No standardized summary of why decisions were made
- Hard to audit decisions after the fact
- Bottlenecks during high application volume

**Goals:**
- Improve processing efficiency without increasing headcount
- Maintain audit trail for every screening decision
- Identify recurring issues (e.g., frequent missing documents)

### 3. Sales Officer

**Responsibilities:**
- Generate loan applications through customer outreach
- Guide customers on required documents
- Follow up on pending applications

**Pain points:**
- Customers often submit incomplete applications
- Unclear why applications are delayed or rejected
- Hard to explain credit decisions to customers

**Goals:**
- Know exactly what documents a customer is missing
- Get clear rejection reasons to communicate to customers
- Reduce application drop-off from incomplete submissions

---

## Eligibility Rules

| Rule | Requirement |
|------|-------------|
| Age | 21–60 years old |
| Employment | Employed, self-employed, or business owner |
| Minimum monthly income | THB 20,000 |
| Existing debt burden | Preferably below 60% debt-to-income ratio |
| Credit history | No severe recent default |
| Required documents | ID card, income proof, bank statement |

---

## Workflow

```
Applicant Input (Streamlit form / API JSON)
↓
Intake Agent (Groq) — validate fields present
  ❌ missing fields → STOP → "Need More Info"
  ✅ continue
↓
Document Agent (Groq) — verify id_card, salary_slip, bank_statement
  ❌ missing docs → STOP → "Need More Info"
  ✅ continue
↓
Eligibility Agent (Groq) — check age, income, DTI, employment, credit
  ❌ fails rules → → → → → → → → → → → → ↓ (skip to recommendation)
  ✅ continue                                    ↓
↓                                               ↓
Risk Agent (Groq) — detect risk signals         ↓
↓                                               ↓
Recommendation Agent (Groq) — classify into 1 of 4 outcomes
  ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ┘
↓
Explanation Agent (Groq) — generate human-readable reasoning
↓
Human Credit Officer Review ⚠️
```
