# Backend/api/routes/offerletter_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest, OfferCreateResponse
from ...Business_Layer.services.offerletter_services import OfferService


router = APIRouter()

@router.post("/create", response_model=OfferCreateResponse)
def create_offer_letter(request: OfferCreateRequest):
    try:
        offer_id = OfferService.create_offer(request)
        return OfferCreateResponse(
            message="Offer letter created successfully",
            offer_id=offer_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
