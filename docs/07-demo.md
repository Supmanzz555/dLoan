# Demo & Presentation

A 6-agent AI pipeline that screens loan applicants and produces structured recommendations — always leaving the final decision to a human credit officer.

## Demo Videos

- **English response:** [Watch on YouTube](https://youtu.be/G-pGU5vu2z0)
- **Thai response:** [Watch on YouTube](https://youtu.be/PRxpDzR5PCU)

## Results at a Glance

| Outcome | Example | What Happens |
|---------|---------|-------------|
| Proceed | APP001 — income 35K, DTI 34%, all docs | Cleared for manual review |
| Need More Info | APP003 — missing salary_slip | Pipeline stops, requests document |
| Reject / Not Eligible | APP005 — income 15K (below 20K minimum) | Hard rule violation |
| High Risk Review | APP007 — DTI 70% (above 60% threshold) | Flagged for senior officer |

## What the System Produces

Every screening returns 9 structured fields:

```
recommendation:      "Proceed"
confidence:          "High"
eligibility_status:  "Eligible"
debt_to_income_ratio: "34.29%"
risk_flags:          []
missing_documents:   []
explanation:         "...Requires human review..."
next_action:         "Proceed to manual review by credit officer"
```

## Demo GIFs

| Run with Docker | Run with script |
|----------------|-----------------|
| ![Docker](img/demo_Docker.gif) | ![Script](img/demo_noDocker.gif) |

## Coverage

- 20 test applicants across all scenarios
- 100% pass rate (expected vs actual)
- Supports both English and Thai responses
- REST API + Streamlit UI
- Docker-ready
