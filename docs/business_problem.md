# Business Problem Summary

## The Problem

dLoan receives a high volume of loan applications daily. Credit officers manually review each application — checking documents, verifying eligibility, assessing risk, and making recommendations. This manual process has several problems:

1. **Slow turnaround** — Each application takes significant time to review, creating backlogs during peak periods.
2. **Inconsistent decisions** — Different officers may apply eligibility rules differently, leading to inconsistent outcomes.
3. **Repetitive verification** — Officers spend hours repeatedly checking the same required documents (ID card, salary slip, bank statement) across applications.
4. **Missing information delays** — Applications with incomplete data require back-and-forth communication, further slowing processing.
5. **Hard to summarize risk** — Quickly understanding an applicant's risk profile requires scanning multiple documents and data points.

## Why AI Assistance Helps

An AI-assisted screening system can:

- **Automate the repetitive parts** — Field validation, document checks, and rule application happen instantly, freeing officers for higher-value work.
- **Standardize decisions** — The same rules are applied consistently to every applicant, eliminating subjective variation.
- **Flag issues immediately** — Missing documents or hard rule violations are detected at the start, so officers don't waste time on incomplete applications.
- **Summarize risk clearly** — Risk flags, DTI ratios, and credit history are extracted and presented in a structured format.
- **Generate human-readable explanations** — Officers get plain-language reasoning they can use in communications with applicants and management.

## How It Works

The system uses 6 AI agents working in sequence:

1. **Intake Agent** — Checks that all required fields are present
2. **Document Agent** — Verifies required documents are uploaded
3. **Eligibility Agent** — Applies loan rules (age, income, employment, DTI)
4. **Risk Agent** — Detects risk signals (high DTI, bad credit)
5. **Recommendation Agent** — Classifies into one of 4 outcomes
6. **Explanation Agent** — Generates human-readable reasoning

All outputs include the disclaimer: *"Requires human review"* — the final decision always rests with the credit officer.

## Impact

| Before | After |
|---|---|
| Manual document checking per application | Automated document verification in seconds |
| Inconsistent rule application | Standardized eligibility checks |
| Slow identification of missing data | Immediate "Need More Info" feedback |
| Manual risk summary | Structured risk flags + DTI ratio |
| No audit trail of screening reasoning | AI-generated explanation for every decision |
