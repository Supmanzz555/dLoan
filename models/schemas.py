from pydantic import BaseModel, Field
from typing import Optional


class ApplicantInput(BaseModel):
    applicant_id: str
    name: str
    age: int = Field(ge=0, le=150)
    employment_type: str
    monthly_income: float = Field(ge=0)
    monthly_debt: float = Field(ge=0)
    requested_loan_amount: float = Field(ge=0)
    credit_history: str
    uploaded_documents: list[str] = []
    notes: Optional[str] = None
    response_lang: str = "en"


class ScreeningResult(BaseModel):
    applicant_id: str
    recommendation: str
    confidence: str
    eligibility_status: str
    debt_to_income_ratio: Optional[str] = None
    risk_flags: list[str] = []
    missing_documents: list[str] = []
    explanation: str
    next_action: str
    screening_id: Optional[int] = None
