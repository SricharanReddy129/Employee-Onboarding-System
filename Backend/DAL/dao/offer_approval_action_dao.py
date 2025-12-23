from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from Backend.DAL.models.models import OfferApprovalRequest


class OfferApprovalActionDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_request_with_actions(self, user_uuid: str):
        """
        Fetch offer approval request with actions (if any)
        """
        stmt = (
            select(OfferApprovalRequest)
            .where(OfferApprovalRequest.user_uuid == user_uuid)
            .options(selectinload(OfferApprovalRequest.offer_approval_action))
        )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_all_requests_with_actions(self):
        stmt = (
            select(OfferApprovalRequest)
            .options(selectinload(OfferApprovalRequest.offer_approval_action))
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()