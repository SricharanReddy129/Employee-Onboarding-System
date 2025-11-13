# Backend/API_Layer/routes/offerletter_routes.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest, OfferCreateResponse
from ...Business_Layer.services.offerletter_services import OfferLetterService
from ...DAL.utils.dependencies import get_db
import pandas as pd
from io import BytesIO

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


# ✅ Create bulk offer letters from Excel file
@router.post("/bulk_create", response_model=list[OfferCreateResponse])
async def create_bulk_offer_letters(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates multiple offer letters from an uploaded Excel file.
    """
    try:
        print("In create_bulk_offer_letters route")

        offer_service = OfferLetterService(db)

        # Read Excel content into pandas DataFrame
        content = await file.read()
        df = pd.read_excel(BytesIO(content))

        required_columns = {
            'first_name', 'last_name', 'mail', 'country_code',
            'contact_number', 'designation', 'package', 'currency'
        }

        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns in Excel file: {', '.join(missing)}"
            )

        return await offer_service.create_bulk_offers(df)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
