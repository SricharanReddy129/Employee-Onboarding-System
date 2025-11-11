# Backend/dal/dao/offer_dao.py

from sqlalchemy.orm import Session
from ...DAL.models.models import OfferLetterDetails
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest


class OfferDAO:
    def __init__(self, db: Session):
        self.db = db
    def create_offer(self, request: OfferCreateRequest) -> OfferLetterDetails:
        new_offer = OfferLetterDetails(
            first_name=request.first_name,
            last_name=request.last_name,
            mail=request.mail,
            country_code=request.country_code,
            contact_number=request.contact_number,
            designation=request.designation,
            package=request.package
        )
        self.db.add(new_offer)
        self.db.commit()
        self.db.refresh(new_offer)
        return new_offer

    def get_offer_by_email(self, mail: str):
        return self.db.query(OfferLetterDetails).filter(OfferLetterDetails.mail == mail).first()
