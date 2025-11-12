# Backend/dal/dao/offer_dao.py

from sqlalchemy.orm import Session
from ...DAL.models.models import OfferLetterDetails
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest



class OfferDAO:
    def __init__(self, db: Session):
        self.db = db
    def create_offer(self, uuid: str, request: OfferCreateRequest) -> OfferLetterDetails:
        new_offer = OfferLetterDetails(
            user_uuid=uuid,
            first_name=request.first_name,
            last_name=request.last_name,
            mail=request.mail,
            country_code=request.country_code,
            created_by = 1,
            contact_number=request.contact_number,
            designation=request.designation,
            package=request.package,
            currency=request.currency
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
