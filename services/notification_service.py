from twilio.rest import Client

from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
)

client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
)


def send_whatsapp(phone: str, message: str):
    """
    Send WhatsApp message.
    """

    if not phone:
        return

    phone = phone.replace("+", "").strip()

    if not phone.startswith("91"):
        phone = "91" + phone

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:+{phone}",
        body=message
    )