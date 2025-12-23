from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from Backend.DAL.models.models import OfferApprovalRequest, OfferApprovalAction


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
    async def get_request_by_user_uuid(self, user_uuid: str):
        stmt = select(OfferApprovalRequest).where(
            OfferApprovalRequest.user_uuid == user_uuid
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_action(
        self,
        request_id: int,
        action: str,
        comment: str | None
    ):
        new_action = OfferApprovalAction(
            request_id=request_id,
            action=action,
            comment=comment
        )

        try:
            self.db.add(new_action)
            await self.db.commit()
            await self.db.refresh(new_action)
            return new_action
        except Exception:
            await self.db.rollback()
            return None
        
    async def has_action_for_request(self, request_id: int) -> bool:
        stmt = select(OfferApprovalAction.id).where(
            OfferApprovalAction.request_id == request_id
        )
        result = await self.db.execute(stmt)
        return result.scalar() is not None