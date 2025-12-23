from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.dao.offer_approval_action_dao import OfferApprovalActionDAO
from Backend.API_Layer.interfaces.offer_request_interfaces import OfferRequestResponse


class OfferApprovalActionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferApprovalActionDAO(db)

    async def get_offer_status(self, user_uuid: str) -> OfferRequestResponse:
        """
        Resolve offer approval status using business rules
        """

        request = await self.dao.get_request_with_actions(user_uuid)

        # ❌ No request exists
        if not request:
            return OfferRequestResponse(
                user_uuid=user_uuid,
                action_taker_id=None,
                action_taker_name="No user",
                status="No Request",
                comments="No Request."
            )

        # ✅ Request exists but no action yet
        if not request.offer_approval_action:
            return OfferRequestResponse(
                user_uuid=user_uuid,
                action_taker_id=request.action_taker_id,
                action_taker_name="Ajay",  # demo
                status="PENDING",
                comments="Awaiting approval"
            )

        # ✅ Request + action exists → take latest action
        latest_action = request.offer_approval_action[-1]

        return OfferRequestResponse(
            user_uuid=user_uuid,
            action_taker_id=request.action_taker_id,
            action_taker_name="Ajay",  # demo
            status=latest_action.action,
            comments=latest_action.comment or ""
        )
    
    async def get_all_offer_statuses(self) -> list[OfferRequestResponse]:
        """
        Resolve offer approval status for ALL users
        """
        requests = await self.dao.get_all_requests_with_actions()

        response: list[OfferRequestResponse] = []

        for request in requests:
            # ❌ Request exists but no action
            if not request.offer_approval_action:
                response.append(
                    OfferRequestResponse(
                        user_uuid=request.user_uuid,
                        action_taker_id=request.action_taker_id,
                        action_taker_name="Ajay",  # replace with user lookup later
                        status="PENDING",
                        comments="Awaiting approval"
                    )
                )
                continue

            # ✅ Take latest action
            latest_action = request.offer_approval_action[-1]

            response.append(
                OfferRequestResponse(
                    user_uuid=request.user_uuid,
                    action_taker_id=request.action_taker_id,
                    action_taker_name="Ajay",
                    status=latest_action.action,
                    comments=latest_action.comment or ""
                )
            )

        return response
