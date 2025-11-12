# Backend/DAL/dao/offer_dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import OfferLetterDetails
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest

class OfferDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_offer(self, uuid: str, request: OfferCreateRequest) -> OfferLetterDetails:
        new_offer = OfferLetterDetails(
            user_uuid=uuid,
            first_name=request.first_name,
            last_name=request.last_name,
            mail=request.mail,
            country_code=request.country_code,
            created_by=1,
            contact_number=request.contact_number,
            designation=request.designation,
            package=request.package,
            currency=request.currency,
        )
        print("Creating new offer in DAO:", new_offer)
        self.db.add(new_offer)
        await self.db.commit()
        await self.db.refresh(new_offer)
        return new_offer

    async def get_offer_by_email(self, mail: str):
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.mail == mail)
        )
        return result.scalar_one_or_none()

    async def get_all_offers(self):
        result = await self.db.execute(select(OfferLetterDetails))
        return result.scalars().all()
