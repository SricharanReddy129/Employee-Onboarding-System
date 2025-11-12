# Backend/business/services/offerletter_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest
from ...DAL.dao.offerletter_dao import OfferDAO
from ..utils.uuid_generator import generate_uuid7


class OfferService:

    def __init__(self, db: Session):
        self.db = db
        self.dao = OfferDAO(self.db)
    
    def create_offer(self, request):
        """
        Business logic for creating a new offer letter.
        """
        # Example of future business validation (e.g., duplicate check)
        print("Checking for existing offer with email:", request.mail)
        existing_offer = self.dao.get_offer_by_email(request.mail)
        if existing_offer:
            raise HTTPException(status_code=400, detail="Offer already exists for this email")

        # Proceed to create offer
        print("No existing offer found, creating new offer.")
        uuid = generate_uuid7()
        new_offer = self.dao.create_offer(uuid, request)
        return new_offer.user_id
    def get_all_offers(self):
        """
        Business logic for retrieving all offer letters.
        """
        offers = self.dao.get_all_offers()
        return offers
