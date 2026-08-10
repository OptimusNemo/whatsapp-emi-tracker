from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import relationship

from database import Base


class Payment(Base):

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    loan_id = Column(Integer, ForeignKey("loans.id"))

    emi_id = Column(Integer, ForeignKey("emis.id"))

    amount = Column(Float, nullable=False)

    payment_mode = Column(String, default="Cash")

    remarks = Column(String, nullable=True)

    payment_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    loan = relationship(
        "Loan",
        back_populates="payments"
    )

    emi = relationship(
        "EMI",
        back_populates="payments"
    )