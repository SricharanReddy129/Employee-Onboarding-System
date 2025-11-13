# Backend/DAL/dao/offer_dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import OfferLetterDetails
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest

class OfferDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_offer(self, uuid: str, request_data: OfferCreateRequest, current_user_id: int) -> OfferLetterDetails:
        new_offer = OfferLetterDetails(
            user_uuid=uuid,
            first_name=request_data.first_name,
            last_name=request_data.last_name,
            mail=request_data.mail,
            country_code=request_data.country_code,
            created_by=current_user_id,
            contact_number=request_data.contact_number,
            designation=request_data.designation,
            package=request_data.package,
            currency=request_data.currency,
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

