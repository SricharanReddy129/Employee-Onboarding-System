from fastapi import APIRouter, HTTPException, Request
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest, OfferCreateResponse, OfferLetterDetails
from ...Business_Layer.services.offerletter_services import OfferLetterService
from ...DAL.utils.database import get_db_session   # ✅ Use ContextVar getter

router = APIRouter()

@router.post("/create", response_model=OfferCreateResponse)
def create_offer_letter(request_data: OfferCreateRequest, request: Request):
    try:
        print("In create_offer_letter route", request_data)
        print("current user", request.state.user.get("user_id"))  # Example of accessing user info from JWT
        current_user_id = int(request.state.user.get("user_id"))  # ✅ Access user info from request state

        db = get_db_session()               # ✅ fetch DB session from context
        offer_service = OfferLetterService(db)    # ✅ pass session into service

        offer_id = offer_service.create_offer(request_data, current_user_id)

        return OfferCreateResponse(
            message="Offer letter created successfully",
            offer_id=offer_id
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/", response_model=list[OfferLetterDetails])

def get_all_offers():
    try:
        db = get_db_session()               # ✅ fetch DB session from context
        offer_service = OfferLetterService(db)    # ✅ pass session into service

        offers = offer_service.get_all_offers()

        return offers

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
