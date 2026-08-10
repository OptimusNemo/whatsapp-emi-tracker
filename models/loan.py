from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import relationship

from database import Base


class Loan(Base):

    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)

    borrower_name = Column(String, nullable=False)

    borrower_phone = Column(String, unique=True, nullable=False)

    lender_phone = Column(String, nullable=False)

    loan_amount = Column(Float, nullable=False)

    monthly_emi = Column(Float, nullable=False)

    total_emi = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    emis = relationship(
        "EMI",
        back_populates="loan",
        cascade="all, delete-orphan"
    )

    payments = relationship(
        "Payment",
        back_populates="loan",
        cascade="all, delete-orphan"
    )