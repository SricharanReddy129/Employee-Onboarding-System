# Backend/API_Layer/routes/offerletter_routes.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest, OfferCreateResponse, BulkOfferCreateResponse, OfferLetterDetailsResponse
from ...Business_Layer.services.offerletter_services import OfferLetterService
from ...DAL.utils.dependencies import get_db
import pandas as pd
from io import BytesIO
from ...config import env_loader
import requests


router = APIRouter()

# ✅ Create single offer letter
@router.post("/create", response_model=OfferCreateResponse)
async def create_offer_letter(
    request_data: OfferCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a single offer letter.
    Uses FastAPI dependency injection to manage DB session.
    """
    try:
        print("In create_offer_letter route", request_data)
        print("current user", request.state.user.get("user_id"))  # Example of accessing user info from JWT
        current_user_id = int(request.state.user.get("user_id"))  # ✅ Access user info from request state

        offer_service = OfferLetterService(db)           # ✅ pass injected session
        offer_id = await offer_service.create_offer(request_data, current_user_id)

        return OfferCreateResponse(
            message="Offer letter created successfully",
            offer_id=offer_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Bulk create offer letters
@router.post("/bulk_create", response_model=BulkOfferCreateResponse)
async def create_bulk_offer_letters(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates multiple offer letters from an uploaded Excel file.
    Handles transaction commit/rollback at route level.
    """
    current_user_id = None
    try:
        # Validate file first
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Only .xlsx, .xls, .csv are allowed"
            )

        current_user_id = int(request.state.user.get("user_id"))
        
        # Read file into DataFrame
        content = await file.read()
        
        try:
            df = pd.read_excel(BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to read Excel file: {str(e)}"
            )

        # Service handles validation and data preparation
        offer_service = OfferLetterService(db)
        result = await offer_service.create_bulk_offers(df, current_user_id)
        
        # Route handles transaction commit
        await db.commit()
        
        return result

    except HTTPException:
        # HTTPException is already formatted properly
        if current_user_id:  # Only rollback if we had a valid session
            await db.rollback()
        raise
        
    except Exception as e:
        # Catch any unexpected errors
        if current_user_id:
            await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )


# ✅ Get all offers
@router.get("/", response_model=list[OfferCreateRequest])
async def get_all_offers(
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all offer letters.
    """
    try:
        offer_service = OfferLetterService(db)
        offers = await offer_service.get_all_offers()
        return offers

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get offer by offer uuid
@router.get("/{offer_uuid}", response_model=OfferLetterDetailsResponse)
async def get_offer_by_uuid(
    offer_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves an offer letter by its UUID.
    """
    try:
        offer_service = OfferLetterService(db)
        offer = await offer_service.get_offer_by_uuid(offer_uuid)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer letter not found")
        return offer

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ✅ Test Pandadoc API connection
PANDADOC_API_KEY = env_loader.get_env_var("PANDADOC_API_KEY")

@router.get("/pandadoc/test")
def test_pandadoc_connection():
    pandadoc_url = env_loader.get_env_var("PANDADOC_API_URL")
    headers = {
        "Authorization": f"API-Key {PANDADOC_API_KEY}",
    }

    response = requests.get(pandadoc_url, headers=headers)

    return {
        "status_code": response.status_code,
        "response": response.json() if response.content else None
    }