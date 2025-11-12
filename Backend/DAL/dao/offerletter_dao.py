# Backend/dal/dao/offer_dao.py

from sqlalchemy.orm import Session
from ...DAL.models.models import OfferLetterDetails
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest



class OfferDAO:
    def __init__(self, db: Session):
        self.db = db
    def create_offer(self, uuid: str, request_data: OfferCreateRequest, current_user_id: int) -> OfferLetterDetails:
        new_offer = OfferLetterDetails(
            user_uuid=uuid,
            first_name=request_data.first_name,
            last_name=request_data.last_name,
            mail=request_data.mail,
            country_code=request_data.country_code,
            created_by = current_user_id,
            contact_number=request_data.contact_number,
            designation=request_data.designation,
            package=request_data.package,
            currency=request_data.currency
        )
        print("Creating new offer in DAO:", new_offer)
        self.db.add(new_offer)
        self.db.commit()
        self.db.refresh(new_offer)
        return new_offer

    def get_offer_by_email(self, mail: str):
        return self.db.query(OfferLetterDetails).filter(OfferLetterDetails.mail == mail).first()
    
    def get_all_offers(self):
        offers = self.db.query(OfferLetterDetails).all()
        return offers
