from dateutil.relativedelta import relativedelta

from models import Loan
from models import EMI
from sqlalchemy import or_


def create_loan(db, data):

    print("=" * 60)
    print("CREATE LOAN STARTED")

    total_emi = int(data.loan_amount / data.monthly_emi)

    print("Total EMI:", total_emi)

    loan = Loan(
        borrower_name=data.borrower_name,
        borrower_phone=data.borrower_phone,
        lender_phone=data.lender_phone,
        loan_amount=data.loan_amount,
        monthly_emi=data.monthly_emi,
        total_emi=total_emi
    )

    db.add(loan)

    db.commit()

    db.refresh(loan)

    print("Loan ID:", loan.id)

    due_date = data.start_date

    for emi_number in range(1, total_emi + 1):

        print(f"Creating EMI {emi_number}")

        emi = EMI(
            loan_id=loan.id,
            emi_number=emi_number,
            amount=data.monthly_emi,
            due_date=due_date
        )

        db.add(emi)

        due_date += relativedelta(months=1)

    print("Committing EMI...")

    db.commit()

    print("EMI Commit Complete")

    count = db.query(EMI).filter(EMI.loan_id == loan.id).count()

    print("EMIs in DB:", count)

    print("=" * 60)

    return loan

def debug_loan(db, phone):

    loan = (
        db.query(Loan)
        .filter(
            or_(
                Loan.borrower_phone == phone,
                Loan.lender_phone == phone
            )
        )
        .first()
    )

    if loan is None:
        return "Loan not found."

    return f"""
 Loan ID : {loan.id}
Borrower : {loan.borrower_name}
Borrower Phone : {loan.borrower_phone}
Lender Phone : {loan.lender_phone}
Loan Amount : ₹{loan.loan_amount}
Monthly EMI : ₹{loan.monthly_emi}
Total EMI : {loan.total_emi}
 """