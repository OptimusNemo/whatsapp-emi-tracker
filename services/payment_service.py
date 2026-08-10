from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models import EMI, Loan, Payment
from services.notification_service import send_whatsapp


def record_payment(
    db: Session,
    phone: str,
    amount: float,
    payment_mode: str = "Cash",
    remarks: str = ""
):
    """
    Record a payment received from either borrower or lender.
    """

    # ---------------------------------
    # Find Loan
    # ---------------------------------

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
        return {
            "success": False,
            "message": "❌ No loan found for this WhatsApp number."
        }

    # ---------------------------------
    # Allocate Payment Across EMIs
    # ---------------------------------

    remaining_amount = amount

    emis = (
        db.query(EMI)
        .filter(
            EMI.loan_id == loan.id,
            EMI.status != "Paid"
        )
        .order_by(EMI.emi_number)
        .all()
    )

    for emi in emis:

        if remaining_amount <= 0:
            break

        total_due = (
            emi.amount
            + emi.carry_forward
            - emi.paid_amount
        )

        pay = min(total_due, remaining_amount)

        payment = Payment(
            loan_id=loan.id,
            emi_id=emi.id,
            amount=pay,
            payment_mode=payment_mode,
            remarks=remarks
        )

        db.add(payment)

        emi.paid_amount += pay

        remaining_amount -= pay

        outstanding = (
            emi.amount
            + emi.carry_forward
            - emi.paid_amount
        )

        if outstanding <= 0:
            emi.status = "Paid"
            emi.paid_date = date.today()
        else:
            emi.status = "Partial"

    db.commit()

    # ---------------------------------
    # Calculate Updated Loan Status
    # ---------------------------------

    paid_amount = amount - remaining_amount

    all_emis = (
        db.query(EMI)
        .filter(EMI.loan_id == loan.id)
        .order_by(EMI.emi_number)
        .all()
    )

    paid_emis = sum(
        1 for emi in all_emis
        if emi.status == "Paid"
    )

    pending_emis = len(all_emis) - paid_emis

    outstanding = sum(
        (
            emi.amount
            + emi.carry_forward
            - emi.paid_amount
        )
        for emi in all_emis
        if emi.status != "Paid"
    )

    next_due = next(
        (
            emi.due_date
            for emi in all_emis
            if emi.status != "Paid"
        ),
        None
    )

    next_due_text = (
        next_due.strftime("%d-%b-%Y")
        if next_due
        else "Loan Closed 🎉"
    )

    # ---------------------------------
    # Build Notification
    # ---------------------------------

    if phone == loan.borrower_phone:

     sender = "Borrower"
     notify_phone = loan.lender_phone

    else:

     sender = "Lender"
     notify_phone = loan.borrower_phone

    notification = (
    f"💰 EMI PAYMENT UPDATE\n\n"
    f"{sender} has recorded a payment.\n\n"
    f"👤 Borrower : {loan.borrower_name}\n\n"
    f"💵 Amount Received : ₹{paid_amount:.2f}\n\n"
    f"💰 Outstanding : ₹{outstanding:.2f}\n\n"
    f"✔ Paid EMI : {paid_emis}/{loan.total_emi}\n\n"
    f"⌛ Pending EMI : {pending_emis}\n\n"
    f"📅 Next Due : {next_due_text}"
    )

    # ---------------------------------
# Notify only the OTHER participant
# ---------------------------------

    try:

     send_whatsapp(
        notify_phone,
        notification
     )

    except Exception as ex:

        print("=" * 60)
        print("Notification Error")
        print(ex)
        print("=" * 60)

    # ---------------------------------
    # Return Response to Webhook
    # ---------------------------------

    return {
        "success": True,
        "message": (
            f"✅ Payment Recorded\n\n"
            f"👤 Borrower : {loan.borrower_name}\n\n"
            f"💰 Received : ₹{paid_amount:.2f}\n\n"
            f"💵 Outstanding : ₹{outstanding:.2f}\n\n"
            f"✔ Paid EMI : {paid_emis}/{loan.total_emi}\n\n"
            f"⌛ Pending EMI : {pending_emis}\n\n"
            f"📅 Next Due : {next_due_text}"
        ),
        "paid": paid_amount,
        "remaining": outstanding,
        "paid_emis": paid_emis,
        "pending_emis": pending_emis,
        "next_due": next_due_text
    }