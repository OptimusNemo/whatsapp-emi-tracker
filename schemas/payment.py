from pydantic import BaseModel


class PaymentCreate(BaseModel):

    loan_id: int

    amount: float

    payment_mode: str = "Cash"

    remarks: str = ""