import json
from agents.llm_client import call_llm
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("risk")


def run(applicant: dict, prior_context: dict | None = None) -> dict:
    payload = {"applicant": applicant}
    if prior_context:
        payload["prior_assessments"] = prior_context

    prompt = SYSTEM_PROMPT
    if applicant.get("response_lang") == "th":
        prompt += "\n\nตอบกลับเป็นภาษาไทย"

    return call_llm([
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(payload, indent=2)},
    ])


if __name__ == "__main__":
    from data.applicants import APP001, APP007, APP015

    for app in [APP001, APP007, APP015]:
        try:
            result = run(app)
            print(f"{app['applicant_id']}: risk_level={result['risk_level']}")
            if result.get("risk_flags"):
                print(f"  flags: {result['risk_flags']}")
        except Exception as e:
            print(f"{app['applicant_id']}: error — {e}")
