# Backend/DAL/dao/offerletter_dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import OfferLetterDetails
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest

class OfferDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    async def create_offer(self, uuid: str, request_data: OfferCreateRequest, current_user_id: int) -> OfferLetterDetails:
        """
        Create a single offer with immediate commit.
        Use for single offer creation.
        """
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
        self.db.add(new_offer)
        await self.db.commit()
        await self.db.refresh(new_offer)
        return new_offer

    async def create_offer_no_commit(self, uuid: str, request_data: OfferCreateRequest, current_user_id: int) -> OfferLetterDetails:
        """
        Create a single offer WITHOUT committing.
        Use inside a transaction context for bulk operations.
        Caller is responsible for committing the transaction.
        """
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
        self.db.add(new_offer)
        # Don't commit - let the caller handle it
        return new_offer

    async def get_offer_by_email(self, mail: str):
        """
        Get a single offer by email.
        """
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.mail == mail)
        )
        return result.scalar_one_or_none()

    async def get_offers_by_emails(self, emails: list) -> list:
        """
        Get all offers matching any email in the list.
        Returns list of email addresses that already exist.
        """
        if not emails:
            return []
        
        result = await self.db.execute(
            select(OfferLetterDetails.mail).where(OfferLetterDetails.mail.in_(emails))
        )
        return result.scalars().all()

    async def get_all_offers(self):
        """
        Get all offers.
        """
        result = await self.db.execute(select(OfferLetterDetails))
        return result.scalars().all()
    
    async def get_offer_by_uuid(self, offer_uuid: str):
        """
        Get a single offer by UUID.
        """
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.user_uuid == offer_uuid)
        )
        return result.scalars().first()