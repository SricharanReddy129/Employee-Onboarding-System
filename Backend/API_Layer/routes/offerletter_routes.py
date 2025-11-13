from fastapi import APIRouter, HTTPException, UploadFile, Request, File
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest, OfferCreateResponse
from ...Business_Layer.services.offerletter_services import OfferLetterService
from ...DAL.utils.database import get_db_session   # ✅ Use ContextVar getter
import pandas as pd

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

# route to create bulk offer letters
@router.post("/bulk_create", response_model=list[OfferCreateResponse])
def create_bulk_offer_letters(file: UploadFile = File(...)):
    try:
        print("In create_bulk_offer_letters route")

        db = get_db_session()               # ✅ fetch DB session from context
        offer_service = OfferLetterService(db)    # ✅ pass session into service

        content = file.read()
        df = pd.read_excel(content)

        required_columns = {'first_name', 'last_name', 'mail', 'country_code', 'contact_number', 'designation', 'package', 'currency'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise HTTPException(status_code=400, detail=f"Missing columns in Excel file: {', '.join(missing)}")
        return offer_service.create_bulk_offers(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/", response_model=list[OfferCreateRequest])

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
