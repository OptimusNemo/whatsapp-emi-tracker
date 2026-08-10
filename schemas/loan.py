from datetime import date

from pydantic import BaseModel, Field


class LoanCreate(BaseModel):

    borrower_name: str = Field(..., min_length=2)

    borrower_phone: str

    lender_phone: str

    loan_amount: float

    monthly_emi: float

    start_date: date