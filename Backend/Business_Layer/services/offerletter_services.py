# Backend/Business_Layer/services/offerletter_service.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest
from ...DAL.dao.offerletter_dao import OfferDAO
from ..utils.uuid_generator import generate_uuid7
from ..utils.validation_utils import (
    validate_name,
    validate_email,
    validate_country_code,
    validate_phone_number,
    validate_designation,
    validate_package,
    validate_currency
)


class OfferLetterService:

    def __init__(self, db: Session):
        self.db = db
        self.dao = OfferDAO(self.db)
    
    def create_offer(self, request_data: OfferCreateRequest, current_user_id: int):
        """
        Business logic for creating a new offer letter.
        Includes validation of all user input fields.
        """
        try:
            # --- VALIDATION SECTION ---
            first_name = validate_name(request_data.first_name)
            last_name = validate_name(request_data.last_name)
            mail = validate_email(request_data.mail)
            country_code = validate_country_code(request_data.country_code)
            contact_number = validate_phone_number(request_data.contact_number)
            designation = validate_designation(request_data.designation)
            package = validate_package(request_data.package)
            currency = validate_currency(request_data.currency)

            # --- DUPLICATE CHECK ---
            print("Checking for existing offer with email:", mail)
            existing_offer = self.dao.get_offer_by_email(mail)
            if existing_offer:
                raise HTTPException(status_code=400, detail="Offer already exists for this email")

            # --- CREATE OFFER ---
            print("No existing offer found, creating new offer.")
            uuid = generate_uuid7()
            new_offer = self.dao.create_offer(uuid, request_data, current_user_id)
            return new_offer.user_id

        except ValueError as ve:
            # catches validation-specific errors
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_all_offers(self):
        """
        Business logic for retrieving all offer letters.
        """
        offers = self.dao.get_all_offers()
        return offers
