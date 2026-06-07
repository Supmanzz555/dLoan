import json
from agents.llm_client import call_llm
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("explanation")


def run(applicant: dict, prior_context: dict) -> dict:
    payload = {"applicant": applicant, "full_assessment": prior_context}

    prompt = SYSTEM_PROMPT
    if applicant.get("response_lang") == "th":
        prompt += "\n\nตอบกลับเป็นภาษาไทย"

    return call_llm([
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(payload, indent=2)},
    ])


if __name__ == "__main__":
    from data.applicants import APP001

    context = {"eligibility_result": {"eligible": True, "eligibility_status": "Passes all rules"}}
    try:
        result = run(APP001, context)
        print(f"Explanation: {result['explanation']}")
        print(f"Next action: {result['next_action']}")
    except Exception as e:
        print(f"error — {e}")
