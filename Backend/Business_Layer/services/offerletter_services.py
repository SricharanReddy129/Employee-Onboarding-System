# Backend/business/services/offerletter_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest
from DAL.dao.offerletter_dao import OfferDAO

class OfferService:
    @staticmethod
    def create_offer(request: OfferCreateRequest, db: Session) -> int:
        """
        Business logic for creating a new offer letter.
        """
        # Example of future business validation (e.g., duplicate check)
        existing_offer = OfferDAO.get_offer_by_email(request.mail, db)
        if existing_offer:
            raise HTTPException(status_code=400, detail="Offer already exists for this email")

        # Proceed to create offer
        new_offer = OfferDAO.create_offer(request, db)
        return new_offer.user_id
