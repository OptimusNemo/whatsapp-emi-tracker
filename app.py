from fastapi import FastAPI

from database import Base
from database import engine

# Import all models so SQLAlchemy knows about them
from models import Loan
from models import EMI
from models import Payment

from routes.loan import router as loan_router
from routes.whatsapp import router as whatsapp_router
from routes.internal import router as internal_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp Loan Management API"
)

app.include_router(loan_router)
app.include_router(whatsapp_router)
app.include_router(internal_router)

@app.get("/")
def home():

    return {

        "message": "Loan Management API Running"

    }