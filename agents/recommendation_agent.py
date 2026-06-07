import json
from agents.llm_client import call_llm
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("recommendation")


def run(applicant: dict, prior_context: dict) -> dict:
    payload = {"applicant": applicant, "prior_assessments": prior_context}

    prompt = SYSTEM_PROMPT
    if applicant.get("response_lang") == "th":
        prompt += "\n\nตอบกลับเป็นภาษาไทย"

    return call_llm([
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(payload, indent=2)},
    ])


if __name__ == "__main__":
    from data.applicants import APP001, APP005, APP008

    for app in [APP001, APP005, APP008]:
        try:
            result = run(app, {})
            print(f"{app['applicant_id']}: {result['recommendation']} (confidence: {result['confidence']})")
        except Exception as e:
            print(f"{app['applicant_id']}: error — {e}")
