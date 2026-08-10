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

    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return send_monthly_reminders()