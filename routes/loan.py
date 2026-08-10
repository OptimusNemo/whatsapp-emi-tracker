from schemas import PaymentCreate
from services.payment_service import record_payment
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db

from schemas import LoanCreate

from services.loan_service import create_loan
from services.status_service import get_loan_status
import os
from database import DATABASE_URL



router = APIRouter(
    prefix="/loan",
    tags=["Loan"]
)

@router.get("/debug/db")
def debug_db():
    return {
        "database_url": DATABASE_URL,
        "cwd": os.getcwd()
    }


@router.post("/create")
def create_new_loan(
    data: LoanCreate,
    db: Session = Depends(get_db)
):

    loan = create_loan(db, data)

    return {

        "message": "Loan Created",

        "loan_id": loan.id

    }

@router.post("/payment")
def make_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db)
):

    result = record_payment(
        db,
        data.loan_id,
        data.amount,
        data.payment_mode,
        data.remarks
    )

    return result

@router.get("/emis/{loan_id}")
def get_emis(
    loan_id: int,
    db: Session = Depends(get_db)
):
    from models import EMI

    emis = (
        db.query(EMI)
        .filter(EMI.loan_id == loan_id)
        .order_by(EMI.emi_number)
        .all()
    )

    return [
        {
            "emi": e.emi_number,
            "amount": e.amount,
            "status": e.status,
            "paid_amount": e.paid_amount,
            "carry_forward": e.carry_forward
        }
        for e in emis
    ]

@router.get("/loans")
def get_loans(db: Session = Depends(get_db)):

    from models import Loan

    loans = db.query(Loan).all()

    return [
        {
            "id": l.id,
            "borrower": l.borrower_name,
            "phone": l.borrower_phone
        }
        for l in loans
    ]

@router.get("/status/{phone}")
def status(
    phone: str,
    db: Session = Depends(get_db)
):

    result = get_loan_status(db, phone)

    if result is None:

        return {

            "message":"Loan Not Found"

        }

    return result

@router.get("/debug/loans")
def debug_loans(db: Session = Depends(get_db)):
    from models import Loan

    loans = db.query(Loan).all()

    return [
        {
            "id": l.id,
            "borrower": l.borrower_name,
            "phone": l.borrower_phone
        }
        for l in loans
    ]