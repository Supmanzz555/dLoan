import json
from agents.llm_client import call_llm
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("intake")


def run(applicant: dict) -> dict:
    prompt = SYSTEM_PROMPT
    if applicant.get("response_lang") == "th":
        prompt += "\n\nตอบกลับเป็นภาษาไทย"
    return call_llm([
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(applicant, indent=2)},
    ])


if __name__ == "__main__":
    from data.applicants import APP001, APP003

    for app in [APP001, APP003]:
        try:
            result = run(app)
            print(f"{app['applicant_id']}: valid={result['valid']}")
            if result.get("missing_fields"):
                print(f"  missing: {result['missing_fields']}")
            if result.get("issues"):
                print(f"  issues: {result['issues']}")
        except Exception as e:
            print(f"{app['applicant_id']}: error — {e}")
