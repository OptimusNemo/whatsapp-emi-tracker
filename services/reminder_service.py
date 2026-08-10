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

        # Reminder only on the 5th
        if today.day != 5:
            print("Today is not reminder day.")

            return {
                "status": "success",
                "processed_loans": 0,
                "messages_sent": 0,
                "message": "Today is not reminder day."
            }

        loans = db.query(Loan).all()

        print(f"Loans found: {len(loans)}")

        for loan in loans:

            try:
                next_emi = (
                    db.query(EMI)
                    .filter(
                        EMI.loan_id == loan.id,
                        EMI.status != "Paid"
                    )
                    .order_by(EMI.emi_number)
                    .first()
                )

                # Loan has no pending EMI
                if next_emi is None:
                    print(
                        f"Loan {loan.id} has no pending EMI. Skipping."
                    )
                    continue

                pending_emis = (
                    db.query(EMI)
                    .filter(
                        EMI.loan_id == loan.id,
                        EMI.status != "Paid"
                    )
                    .count()
                )

                pending_emi_list = (
                    db.query(EMI)
                    .filter(
                        EMI.loan_id == loan.id,
                        EMI.status != "Paid"
                    )
                    .order_by(EMI.emi_number)
                    .all()
                )

                outstanding = sum(
                    (
                        emi.amount
                        + emi.carry_forward
                        - emi.paid_amount
                    )
                    for emi in pending_emi_list
                )

                if next_emi.due_date:
                    next_due = next_emi.due_date.strftime(
                        "%d-%b-%Y"
                    )
                else:
                    next_due = "Not Available"

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

                print(
                    f"Sending reminder for Loan {loan.id}"
                )

                # Send to borrower
                send_whatsapp(
                    loan.borrower_phone,
                    message
                )

                # Send to lender
                send_whatsapp(
                    loan.lender_phone,
                    message
                )

                processed_loans += 1
                messages_sent += 2

                print(
                    f"Reminder sent successfully for Loan {loan.id}"
                )

            except Exception as ex:

                print("=" * 60)
                print(
                    f"Reminder failed for Loan {loan.id}"
                )
                print(f"Error: {ex}")
                print("=" * 60)

                # Continue with the next loan
                continue

        print("=" * 60)
        print("Monthly reminder completed.")
        print(
            f"Processed Loans : {processed_loans}"
        )
        print(
            f"Messages Sent   : {messages_sent}"
        )
        print("=" * 60)

        return {
            "status": "success",
            "processed_loans": processed_loans,
            "messages_sent": messages_sent
        }

    finally:
        db.close()