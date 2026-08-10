import os

from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------
# Database
# ----------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///data/emi.db"
)

# ----------------------------------------
# Twilio
# ----------------------------------------

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# ----------------------------------------
# Internal API
# ----------------------------------------

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")