from datetime import date, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Loan, EMI, ReminderLog
from services.notification_service import send_whatsapp


def send_monthly_reminders(force=False):
    processed_loans = 0
    messages_sent = 0

    db: Session = SessionLocal()

    try:
        today = date.today()

        print("=" * 60)
        print("TODAY :", today)
        print("DAY   :", today.day)
        print("=" * 60)

        # Reminder only on the 10th unless force=True
        if today.day != 10 and not force:
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
                # -----------------------------------------
                # IDEMPOTENCY CHECK
                # -----------------------------------------

                existing_log = (
                    db.query(ReminderLog)
                    .filter(
                        ReminderLog.loan_id == loan.id,
                        ReminderLog.reminder_date == today
                    )
                    .first()
                )

                if existing_log:

                    if existing_log.status == "sent":
                        print(
                            f"Reminder already sent for Loan "
                            f"{loan.id} on {today}. Skipping."
                        )
                        continue

                    # Retry stale processing records
                    if (
                        existing_log.status == "processing"
                        and existing_log.created_at
                        and datetime.utcnow() - existing_log.created_at
                        < timedelta(minutes=10)
                    ):
                        print(
                            f"Reminder currently processing for "
                            f"Loan {loan.id}. Skipping."
                        )
                        continue

                    # Failed/stale processing → retry
                    existing_log.status = "processing"
                    existing_log.created_at = datetime.utcnow()
                    db.commit()

                else:

                    reminder_log = ReminderLog(
                        loan_id=loan.id,
                        reminder_date=today,
                        status="processing"
                    )

                    db.add(reminder_log)

                    try:
                        db.commit()
                    except IntegrityError:
                        db.rollback()

                        print(
                            f"Reminder claim already exists for "
                            f"Loan {loan.id}. Skipping."
                        )
                        continue

                    existing_log = reminder_log

                # -----------------------------------------
                # FIND NEXT EMI
                # -----------------------------------------

                next_emi = (
                    db.query(EMI)
                    .filter(
                        EMI.loan_id == loan.id,
                        EMI.status != "Paid"
                    )
                    .order_by(EMI.emi_number)
                    .first()
                )

                if next_emi is None:
                    print(
                        f"Loan {loan.id} has no pending EMI. Skipping."
                    )

                    existing_log.status = "sent"
                    existing_log.sent_at = datetime.utcnow()
                    db.commit()

                    continue

                # -----------------------------------------
                # CALCULATE STATUS
                # -----------------------------------------

                pending_emi_list = (
                    db.query(EMI)
                    .filter(
                        EMI.loan_id == loan.id,
                        EMI.status != "Paid"
                    )
                    .order_by(EMI.emi_number)
                    .all()
                )

                pending_emis = len(pending_emi_list)

                outstanding = sum(
                    emi.amount
                    + emi.carry_forward
                    - emi.paid_amount
                    for emi in pending_emi_list
                )

                next_due = (
                    next_emi.due_date.strftime("%d-%b-%Y")
                    if next_emi.due_date
                    else "Not Available"
                )

                # -----------------------------------------
                # MESSAGE
                # -----------------------------------------

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

                # -----------------------------------------
                # SEND BORROWER
                # -----------------------------------------

                send_whatsapp(
                    loan.borrower_phone,
                    message
                )

                # -----------------------------------------
                # SEND LENDER
                # -----------------------------------------

                send_whatsapp(
                    loan.lender_phone,
                    message
                )

                # -----------------------------------------
                # MARK AS SENT
                # -----------------------------------------

                existing_log.status = "sent"
                existing_log.sent_at = datetime.utcnow()

                db.commit()

                processed_loans += 1
                messages_sent += 2

                print(
                    f"Reminder sent successfully for Loan {loan.id}"
                )

            except Exception as ex:

                print("=" * 60)
                print(f"Reminder failed for Loan {loan.id}")
                print(f"Error: {ex}")
                print("=" * 60)

                try:
                    db.rollback()

                    failed_log = (
                        db.query(ReminderLog)
                        .filter(
                            ReminderLog.loan_id == loan.id,
                            ReminderLog.reminder_date == today
                        )
                        .first()
                    )

                    if failed_log:
                        failed_log.status = "failed"
                        db.commit()

                except Exception as log_error:
                    print(
                        f"Could not update reminder log: {log_error}"
                    )

                continue

        print("=" * 60)
        print("Monthly reminder completed.")
        print(f"Processed Loans : {processed_loans}")
        print(f"Messages Sent   : {messages_sent}")
        print("=" * 60)

        return {
            "status": "success",
            "processed_loans": processed_loans,
            "messages_sent": messages_sent
        }

    finally:
        db.close()