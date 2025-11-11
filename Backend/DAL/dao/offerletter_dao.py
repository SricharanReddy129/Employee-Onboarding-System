# Backend/dal/dao/offer_dao.py

from sqlalchemy.orm import Session
from DAL.models.models import OfferLetterDetails
from API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest

class OfferDAO:
    @staticmethod
    def create_offer(request: OfferCreateRequest, db: Session) -> OfferLetterDetails:
        new_offer = OfferLetterDetails(
            first_name=request.first_name,
            last_name=request.last_name,
            mail=request.mail,
            country_code=request.country_code,
            contact_number=request.contact_number,
            designation=request.designation,
            package=request.package
        )
        db.add(new_offer)
        db.commit()
        db.refresh(new_offer)
        return new_offer

    @staticmethod
    def get_offer_by_email(mail: str, db: Session):
        return db.query(OfferLetterDetails).filter(OfferLetterDetails.mail == mail).first()
