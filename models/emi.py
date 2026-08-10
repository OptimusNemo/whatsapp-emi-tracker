from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import relationship

from database import Base


class EMI(Base):

    __tablename__ = "emis"

    id = Column(Integer, primary_key=True, index=True)

    loan_id = Column(Integer, ForeignKey("loans.id"))

    emi_number = Column(Integer, nullable=False)

    amount = Column(Float, nullable=False)

    carry_forward = Column(Float, default=0)

    paid_amount = Column(Float, default=0)

    due_date = Column(Date)

    status = Column(String, default="Pending")

    reminder_count = Column(Integer, default=0)

    paid_date = Column(Date, nullable=True)

    loan = relationship(
        "Loan",
        back_populates="emis"
    )

    payments = relationship(
        "Payment",
        back_populates="emi"
    )