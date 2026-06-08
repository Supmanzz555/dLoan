# Demo & Presentation

dLoan is a 6-agent AI system that screens loan applicants and recommends one of 4 outcomes: Proceed, Need More Info, Reject, or High Risk Review. The final decision always rests with a human credit officer.

## Demo Videos

- **English response:** [Watch on YouTube](https://youtu.be/G-pGU5vu2z0)
- **Thai response:** [Watch on YouTube](https://youtu.be/PRxpDzR5PCU)

Both videos show the complete workflow — submitting an applicant, running the agent pipeline, and reviewing the structured output.

## Quick Walkthrough

1. **Input** — Enter applicant data via Streamlit form or REST API
2. **Screen** — 6 agents run sequentially: Intake → Document → Eligibility → Risk → Recommendation → Explanation
3. **Output** — Structured result with recommendation, risk flags, DTI ratio, and human-readable explanation
4. **Review** — Credit officer reviews the AI output and makes the final decision

### Edge Cases Covered

- Missing documents → short-circuit at Document agent
- Low income / age out of range → hard rule reject
- High DTI / bad credit → flagged for senior officer review
- Self-employed / business owner → accepted with stable income

## Demo GIFs

| Run with Docker | Run with script |
|----------------|-----------------|
| ![Docker](img/demo_Docker.gif) | ![Script](img/demo_noDocker.gif) |
