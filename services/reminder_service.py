from datetime import date

from sqlalchemy.orm import Session

from database import SessionLocal
from models import Loan, EMI
from services.notification_service import send_whatsapp


def send_monthly_reminders():

    processed_loans = 0
    messages_sent = 0

    db: Session = SessionLocal()

    try:

        today = date.today()

        print("=" * 60)
        print("TODAY :", today)
        print("DAY   :", today.day)
        print("=" * 60)

        # Reminder only on the 10th
        if today.day != 10:
            print("Today is not reminder day.")
            return

        loans = db.query(Loan).all()

        for loan in loans:

            next_emi  = (
                db.query(EMI)
                .filter(
                    EMI.loan_id == loan.id,
                    EMI.status != "Paid"
                )
                .order_by(EMI.emi_number)
                .first()
            )

            if next_emi is None:
                continue

            pending_emis = (
              db.query(EMI)
              .filter(
                EMI.loan_id == loan.id,
                EMI.status != "Paid"
              ).count()
            )

            outstanding = sum(
                (
                    emi.amount
                    + emi.carry_forward
                    - emi.paid_amount
                )
                for emi in (
                    db.query(EMI)
                    .filter(
                        EMI.loan_id == loan.id,
                        EMI.status != "Paid"
                    )
                    .all()
                )
            )            

            next_due = next_emi.due_date.strftime("%d-%b-%Y")

            message = (
                f"🔔 EMI REMINDER\n\n"
                f"👤 Borrower : {loan.borrower_name}\n\n"
                f"💰 Monthly EMI : ₹{loan.monthly_emi:.2f}\n\n"
                f"💵 Outstanding : ₹{outstanding:.2f}\n\n"
                f"⌛ Pending EMI : {pending_emis}\n\n"
                f"📅 Next Due : {next_due}\n\n"
                f"Reply with:\n"
                f"PAY {int(loan.monthly_emi)}\n"
                f"after payment is completed."
            )

            print(f"Sending reminder for Loan {loan.id}")

        try:
            send_whatsapp(
                loan.borrower_phone,
                message
            )

            send_whatsapp(
                loan.lender_phone,
                message
            )

            processed_loans += 1
            messages_sent += 2
            print(f"Reminder sent for Loan {loan.id}")

        except Exception as ex:

            print(f"Reminder failed for Loan {loan.id}")
            print(ex)    

        print("Monthly reminder completed.")

    finally:

        db.close()

    return {
    "status": "success",
    "processed_loans": processed_loans,
    "messages_sent": messages_sent
    }    