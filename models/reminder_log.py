from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint

from database import Base


class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True, index=True)

    loan_id = Column(Integer, nullable=False)

    reminder_date = Column(Date, nullable=False)

    status = Column(String, nullable=False, default="processing")

    created_at = Column(DateTime, default=datetime.utcnow)

    sent_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "loan_id",
            "reminder_date",
            name="uq_reminder_loan_date"
        ),
    )