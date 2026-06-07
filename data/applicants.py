"""
20 sample loan applicants covering all required scenario types.

Expected outcomes serve as baseline for integration test assertions.
The LLM determines the final outcome — these are reference expectations
based on eligibility rules, not ground truth.
"""

APP001 = {
    "applicant_id": "APP001",
    "name": "Somchai",
    "age": 32,
    "employment_type": "employee",
    "monthly_income": 35000,
    "monthly_debt": 12000,
    "requested_loan_amount": 200000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Stable employment, meets all criteria",
}
# Expected: Proceed

APP002 = {
    "applicant_id": "APP002",
    "name": "Pricha",
    "age": 45,
    "employment_type": "employee",
    "monthly_income": 55000,
    "monthly_debt": 15000,
    "requested_loan_amount": 500000,
    "credit_history": "good",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Senior employee, high income",
}
# Expected: Proceed

APP003 = {
    "applicant_id": "APP003",
    "name": "Nattapong",
    "age": 28,
    "employment_type": "employee",
    "monthly_income": 25000,
    "monthly_debt": 5000,
    "requested_loan_amount": 100000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "bank_statement"],
    "notes": "Missing salary_slip document",
}
# Expected: Need More Info (missing salary_slip)

APP004 = {
    "applicant_id": "APP004",
    "name": "Somsak",
    "age": 35,
    "employment_type": "employee",
    "monthly_income": 30000,
    "monthly_debt": 10000,
    "requested_loan_amount": 150000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card"],
    "notes": "Missing salary_slip and bank_statement",
}
# Expected: Need More Info (missing 2 docs)

APP005 = {
    "applicant_id": "APP005",
    "name": "Malee",
    "age": 41,
    "employment_type": "employee",
    "monthly_income": 15000,
    "monthly_debt": 5000,
    "requested_loan_amount": 50000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Income below minimum threshold of 20,000",
}
# Expected: Reject / Not Eligible (low income)

APP006 = {
    "applicant_id": "APP006",
    "name": "Preeda",
    "age": 62,
    "employment_type": "employee",
    "monthly_income": 40000,
    "monthly_debt": 10000,
    "requested_loan_amount": 300000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Age exceeds maximum of 60",
}
# Expected: Reject / Not Eligible (age out of range)

APP007 = {
    "applicant_id": "APP007",
    "name": "Thana",
    "age": 38,
    "employment_type": "employee",
    "monthly_income": 50000,
    "monthly_debt": 35000,
    "requested_loan_amount": 400000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "High DTI ratio exceeds 60%",
}
# Expected: High Risk Review (DTI 70%)

APP008 = {
    "applicant_id": "APP008",
    "name": "Pichai",
    "age": 30,
    "employment_type": "employee",
    "monthly_income": 40000,
    "monthly_debt": 20000,
    "requested_loan_amount": 250000,
    "credit_history": "severe_default",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Recent severe default on credit history",
}
# Expected: High Risk Review (bad credit history)

APP009 = {
    "applicant_id": "APP009",
    "name": "Siriporn",
    "age": 36,
    "employment_type": "self-employed",
    "monthly_income": 45000,
    "monthly_debt": 15000,
    "requested_loan_amount": 300000,
    "credit_history": "good",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Self-employed with stable income and good credit",
}
# Expected: Proceed

APP010 = {
    "applicant_id": "APP010",
    "name": "Wichai",
    "age": 50,
    "employment_type": "business_owner",
    "monthly_income": 80000,
    "monthly_debt": 30000,
    "requested_loan_amount": 600000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Business owner, high income, meets all criteria",
}
# Expected: Proceed

APP011 = {
    "applicant_id": "APP011",
    "name": "Anong",
    "age": 25,
    "employment_type": "employee",
    "monthly_income": 22000,
    "monthly_debt": 14000,
    "requested_loan_amount": 80000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Borderline DTI ~63.6%, just above threshold",
}
# Expected: High Risk Review (DTI borderline)

APP012 = {
    "applicant_id": "APP012",
    "name": "Samorn",
    "age": 19,
    "employment_type": "employee",
    "monthly_income": 25000,
    "monthly_debt": 5000,
    "requested_loan_amount": 50000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Underage, below minimum age of 21",
}
# Expected: Reject / Not Eligible (age under 21)

APP013 = {
    "applicant_id": "APP013",
    "name": "Kriangkrai",
    "age": 33,
    "employment_type": "unemployed",
    "monthly_income": 30000,
    "monthly_debt": 8000,
    "requested_loan_amount": 100000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Employment type 'unemployed' not allowed",
}
# Expected: Reject / Not Eligible (invalid employment)

APP014 = {
    "applicant_id": "APP014",
    "name": "Rungnapa",
    "age": 29,
    "employment_type": "employee",
    "monthly_income": 20000,
    "monthly_debt": 12000,
    "requested_loan_amount": 100000,
    "credit_history": "fair",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Barely meets minimum income, DTI 60% at threshold",
}
# Expected: Proceed (meets all criteria, borderline DTI at 60%)

APP015 = {
    "applicant_id": "APP015",
    "name": "Boonlert",
    "age": 40,
    "employment_type": "employee",
    "monthly_income": 35000,
    "monthly_debt": 22000,
    "requested_loan_amount": 200000,
    "credit_history": "default",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Default on record AND high DTI ~62.8%",
}
# Expected: High Risk Review (bad credit + high DTI)

APP016 = {
    "applicant_id": "APP016",
    "name": "Chaloem",
    "age": 35,
    "employment_type": "employee",
    "monthly_income": 20000,
    "monthly_debt": 32000,
    "requested_loan_amount": 200000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Extreme DTI 160%, monthly debt far exceeds income",
}
# Expected: High Risk Review (extreme DTI)

APP017 = {
    "applicant_id": "APP017",
    "name": "Chaiwat",
    "age": 45,
    "employment_type": "unemployed",
    "monthly_income": 15000,
    "monthly_debt": 10000,
    "requested_loan_amount": 100000,
    "credit_history": "severe_default",
    "uploaded_documents": [],
    "notes": "Multiple failures: unemployed, low income, bad credit, no docs",
}
# Expected: Reject / Not Eligible (hard rule: employment + income)

APP018 = {
    "applicant_id": "APP018",
    "name": "Prayong",
    "age": 80,
    "employment_type": "employee",
    "monthly_income": 80000,
    "monthly_debt": 20000,
    "requested_loan_amount": 500000,
    "credit_history": "good",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Age far above 60, but otherwise excellent profile",
}
# Expected: Reject / Not Eligible (age hard rule)

APP019 = {
    "applicant_id": "APP019",
    "name": "Thongchai",
    "age": 30,
    "employment_type": "employee",
    "monthly_income": 40000,
    "monthly_debt": 15000,
    "requested_loan_amount": 5000000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Requesting 5M loan on 40K income — extreme loan-to-income ratio",
}
# Expected: High Risk Review (extreme loan amount)

APP020 = {
    "applicant_id": "APP020",
    "name": "Udom",
    "age": 28,
    "employment_type": "employee",
    "monthly_income": 0,
    "monthly_debt": 5000,
    "requested_loan_amount": 50000,
    "credit_history": "normal",
    "uploaded_documents": ["id_card", "salary_slip", "bank_statement"],
    "notes": "Zero income — tests division by zero in DTI calculation",
}
# Expected: Reject / Not Eligible (income below 20K, DTI undefined)

ALL_APPLICANTS = [
    APP001, APP002, APP003, APP004, APP005,
    APP006, APP007, APP008, APP009, APP010,
    APP011, APP012, APP013, APP014, APP015,
    APP016, APP017, APP018, APP019, APP020,
]

APPLICANT_MAP = {a["applicant_id"]: a for a in ALL_APPLICANTS}

EXPECTED_OUTCOMES = {
    "APP001": "Proceed",
    "APP002": "Proceed",
    "APP003": "Need More Info",
    "APP004": "Need More Info",
    "APP005": "Reject / Not Eligible",
    "APP006": "Reject / Not Eligible",
    "APP007": "High Risk Review",
    "APP008": "High Risk Review",
    "APP009": "Proceed",
    "APP010": "Proceed",
    "APP011": "High Risk Review",
    "APP012": "Reject / Not Eligible",
    "APP013": "Reject / Not Eligible",
    "APP014": "Proceed",
    "APP015": "High Risk Review",
    "APP016": "High Risk Review",
    "APP017": "Reject / Not Eligible",
    "APP018": "Reject / Not Eligible",
    "APP019": "High Risk Review",
    "APP020": "Reject / Not Eligible",
}


if __name__ == "__main__":
    print(f"Loaded {len(ALL_APPLICANTS)} applicants:")
    for app in ALL_APPLICANTS:
        exp = EXPECTED_OUTCOMES[app["applicant_id"]]
        print(f"  {app['applicant_id']} — {app['name']:12s} ({app['employment_type']:15s}) "
              f"age {app['age']:2d} income {app['monthly_income']:5.0f} "
              f"→ expected: {exp}")
