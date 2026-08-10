from sqlalchemy.orm import Session

from models import Loan
from models import EMI


def get_loan_status(db: Session, phone: str):

    loan = (
        db.query(Loan)
        .filter(Loan.borrower_phone == phone)
        .first()
    )

    if not loan:
        return None

    emis = (
        db.query(EMI)
        .filter(EMI.loan_id == loan.id)
        .order_by(EMI.emi_number)
        .all()
    )

    total_paid = sum(e.paid_amount for e in emis)

    remaining = loan.loan_amount - total_paid

    paid_emis = len([e for e in emis if e.status == "Paid"])

    partial_emis = len([e for e in emis if e.status == "Partial"])

    pending_emis = len([e for e in emis if e.status != "Paid"])

    next_due = None

    for emi in emis:
        if emi.status != "Paid":
            next_due = emi.due_date
            break

    return {

        "borrower": loan.borrower_name,

        "loan_amount": loan.loan_amount,

        "paid_amount": total_paid,

        "remaining_amount": remaining,

        "paid_emis": paid_emis,

        "partial_emis": partial_emis,

        "pending_emis": pending_emis,

        "next_due": next_due

    }