from models.schemas import ApplicantInput

REQUIRED_DOCUMENTS = ["id_card", "salary_slip", "bank_statement"]

EMPLOYMENT_TYPES = {"employee", "self-employed", "business_owner"}

CREDIT_HISTORY_CLEAR = {"normal", "good", "fair"}
CREDIT_HISTORY_BAD = {"default", "severe_default", "bad"}


def check_age(age: int) -> bool:
    return 21 <= age <= 60


def check_employment(employment_type: str) -> bool:
    return employment_type.lower() in EMPLOYMENT_TYPES


def check_min_income(monthly_income: float) -> bool:
    return monthly_income >= 20000


def check_dti(monthly_debt: float, monthly_income: float) -> float | None:
    if monthly_income <= 0:
        return None
    return monthly_debt / monthly_income


def check_credit_history(credit_history: str) -> tuple[bool, str]:
    status = credit_history.lower().strip()
    if status in CREDIT_HISTORY_BAD:
        return False, "severe recent default detected"
    if status in CREDIT_HISTORY_CLEAR:
        return True, "clear"
    return True, "unknown"


def check_documents(uploaded: list[str]) -> list[str]:
    missing = []
    for doc in REQUIRED_DOCUMENTS:
        if doc not in uploaded:
            missing.append(doc)
    return missing


def validate_applicant(applicant: ApplicantInput) -> dict:
    issues = []
    dti_ratio = check_dti(applicant.monthly_debt, applicant.monthly_income)
    credit_ok, credit_note = check_credit_history(applicant.credit_history)

    if not check_age(applicant.age):
        issues.append(f"age {applicant.age} not in range 21-60")

    if not check_employment(applicant.employment_type):
        issues.append(f"employment type '{applicant.employment_type}' not allowed")

    if not check_min_income(applicant.monthly_income):
        issues.append(f"income {applicant.monthly_income} below minimum 20,000")

    if dti_ratio is not None and dti_ratio > 0.6:
        issues.append(f"DTI ratio {dti_ratio:.0%} exceeds 60%")

    if not credit_ok:
        issues.append(f"credit history: {credit_note}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "dti_ratio": round(dti_ratio, 4) if dti_ratio is not None else None,
        "credit_note": credit_note,
        "missing_docs": check_documents(applicant.uploaded_documents),
    }


if __name__ == "__main__":
    from data.applicants import APP001

    applicant = ApplicantInput(**APP001)
    result = validate_applicant(applicant)
    print(f"APP001 — Valid: {result['valid']}, Issues: {result['issues']}")
    print(f"  DTI: {result['dti_ratio']}, Credit: {result['credit_note']}")
    print(f"  Missing docs: {result['missing_docs']}")
