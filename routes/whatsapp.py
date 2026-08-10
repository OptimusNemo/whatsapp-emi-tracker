from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

from database import get_db
from services.status_service import get_loan_status
from services.payment_service import record_payment

router = APIRouter(tags=["WhatsApp"])


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    db: Session = Depends(get_db)
):
    print("REQUEST PATH:", request.url.path)

    phone = (
        From.replace("whatsapp:", "")
            .replace("+", "")
            .strip()
    )

    message = Body.strip().lower()

    print("=" * 50)
    print("Incoming From :", From)
    print("Parsed Phone  :", phone)
    print("Message       :", message)
    print("=" * 50)

    reply = MessagingResponse()

    # ==========================
    # STATUS COMMAND
    # ==========================
    if message == "status":

        print("Searching for phone:", repr(phone))
        print("=" * 80)
        print("Searching phone :", repr(phone))

        status = get_loan_status(db, phone)

        print("Status returned :", status)
        print("=" * 80)

        if status is None:

            reply.message(
                "❌ No loan found for this WhatsApp number."
            )

            return Response(
                str(reply),
                media_type="application/xml"
            )

        text = f"""
🏦 EMI STATUS

👤 Borrower : {status['borrower']}

💰 Loan Amount : ₹{status['loan_amount']}

✅ Paid : ₹{status['paid_amount']}

💵 Outstanding : ₹{status['remaining_amount']}

✔ Paid EMI : {status['paid_emis']}

⌛ Pending EMI : {status['pending_emis']}

📅 Next Due : {status['next_due']}
"""

        reply.message(text)

    # ==========================
    # PAY COMMAND
    # ==========================
    elif message.startswith("pay"):

        parts = message.split()

        if len(parts) != 2:

            reply.message(
                "Usage:\n\nPAY <amount>\n\nExample:\nPAY 3000"
            )

        else:

            try:

                amount = float(parts[1])

                result = record_payment(
                    db=db,
                    phone=phone,
                    amount=amount
                )

                if result["success"]:
                 reply.message(
                 "✅ Payment recorded successfully.\n\n"
                 "The other party has been notified.")
                else:
                 reply.message(result["message"])

            except ValueError:

                reply.message(
                    "Invalid amount.\n\nExample:\nPAY 3000"
                )
    elif message == "debug loan":
        from services.loan_service import debug_loan
        result = debug_loan(db, phone)
        reply.message(result)            

    # ==========================
    # UNKNOWN COMMAND
    # ==========================
    else:

        reply.message(
            "Unknown command.\n\nAvailable commands:\nstatus\npay <amount>"
        )

    return Response(
        str(reply),
        media_type="application/xml"
    )