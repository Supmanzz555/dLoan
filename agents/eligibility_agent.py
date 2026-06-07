import json
from agents.llm_client import call_llm
from prompts import load_prompt

SYSTEM_PROMPT = load_prompt("eligibility")


def run(applicant: dict) -> dict:
    income = applicant.get("monthly_income", 0)
    debt = applicant.get("monthly_debt", 0)
    dti = round(debt / income, 4) if income > 0 else None
    payload = {**applicant, "calculated_dti": dti}

    prompt = SYSTEM_PROMPT
    if applicant.get("response_lang") == "th":
        prompt += "\n\nตอบกลับเป็นภาษาไทย"

    return call_llm([
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(payload, indent=2)},
    ])


if __name__ == "__main__":
    from data.applicants import APP001, APP005, APP007

    for app in [APP001, APP005, APP007]:
        try:
            result = run(app)
            print(f"{app['applicant_id']}: eligible={result['eligible']}")
            if result.get("issues"):
                print(f"  issues: {result['issues']}")
            print(f"  DTI: {result.get('dti_percentage', 'N/A')}, status: {result.get('eligibility_status', 'N/A')}")
        except Exception as e:
            print(f"{app['applicant_id']}: error — {e}")
