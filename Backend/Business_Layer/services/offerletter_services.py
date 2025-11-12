# Backend/Business_Layer/services/offerletter_service.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest
from ...DAL.dao.offerletter_dao import OfferDAO
from ..utils.uuid_generator import generate_uuid7

class OfferService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferDAO(self.db)

    async def create_offer(self, request: OfferCreateRequest):
        print("Checking for existing offer with email:", request.mail)
        existing_offer = await self.dao.get_offer_by_email(request.mail)
        if existing_offer:
            raise HTTPException(status_code=400, detail="Offer already exists for this email")

        uuid = generate_uuid7()
        new_offer = await self.dao.create_offer(uuid, request)
        return new_offer.user_id

    async def get_all_offers(self):
        return await self.dao.get_all_offers()
