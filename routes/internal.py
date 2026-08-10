from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException

from config import INTERNAL_API_KEY
from services.reminder_service import send_monthly_reminders


router = APIRouter(
    prefix="/internal",
    tags=["Internal"]
)


@router.post("/send-reminders")
def send_reminders(x_api_key: str = Header(None)):
    return {
        "configured": INTERNAL_API_KEY,
        "received": x_api_key
    }

    # return send_monthly_reminders()