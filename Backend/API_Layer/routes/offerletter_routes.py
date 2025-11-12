from fastapi import APIRouter, HTTPException
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest, OfferCreateResponse
from ...Business_Layer.services.offerletter_services import OfferService
from ...DAL.utils.database import get_db_session   # ✅ Use ContextVar getter

router = APIRouter()

@router.post("/create", response_model=OfferCreateResponse)
def create_offer_letter(request: OfferCreateRequest):
    try:
        print("In create_offer_letter route", request)

        db = get_db_session()               # ✅ fetch DB session from context
        offer_service = OfferService(db)    # ✅ pass session into service

        offer_id = offer_service.create_offer(request)

        return OfferCreateResponse(
            message="Offer letter created successfully",
            offer_id=offer_id
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/", response_model=list[OfferCreateRequest])

def get_all_offers():
    try:
        db = get_db_session()               # ✅ fetch DB session from context
        offer_service = OfferService(db)    # ✅ pass session into service

        offers = offer_service.get_all_offers()

        return offers

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
