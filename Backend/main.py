# Backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from DAL.utils.database import get_db
from DAL.models.models import OfferLetterDetails

# Backend/main.py

from fastapi import FastAPI
from API_Layer.routes.offerletter_routes import router as offer_router

app = FastAPI(title="Employee Onboarding System")

# Include all routes
app.include_router(offer_router, prefix="/offer", tags=["Offer Letter"])

@app.get("/")
def root():
    return {"message": "🚀 Employee Onboarding System API is running!"}