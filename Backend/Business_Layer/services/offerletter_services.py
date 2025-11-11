# Backend/business/services/offerletter_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest
from ...DAL.dao.offerletter_dao import OfferDAO


class OfferService:

    def __init__(self, db: Session):
        self.db = db
        self.dao = OfferDAO(self.db)
    
    def create_offer(self, request: OfferCreateRequest) -> int:
        """
        Business logic for creating a new offer letter.
        """
        # Example of future business validation (e.g., duplicate check)
        existing_offer = OfferDAO.get_offer_by_email(request.mail)
        if existing_offer:
            raise HTTPException(status_code=400, detail="Offer already exists for this email")

        # Proceed to create offer
        new_offer = self.dao.create_offer(request)
        return new_offer.user_id
