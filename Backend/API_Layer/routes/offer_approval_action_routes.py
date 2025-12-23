from Backend.API_Layer.interfaces.offer_approve_action_interfaces import OfferApproveActionRequest
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...Business_Layer.services.offer_approval_action_service import (
    OfferApprovalActionService
)
from ...DAL.utils.dependencies import get_db
from ...API_Layer.interfaces.offer_request_interfaces import OfferRequestResponse

router = APIRouter()
@router.get(
    "/status/{user_uuid}",
    response_model=OfferRequestResponse
)
async def get_offer_approval_status(
    user_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get approval status for an offer using user_uuid
    """
    service = OfferApprovalActionService(db)
    return await service.get_offer_status(user_uuid)

@router.get("/all")
async def get_all_offer_statuses(
    db: AsyncSession = Depends(get_db)
):
    service = OfferApprovalActionService(db)
    return await service.get_all_offer_statuses()

@router.post("/action")
async def create_offer_approval_actions(
    payload: list[OfferApproveActionRequest],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Approver submits APPROVED / REJECTED / ON_HOLD actions (bulk)
    """
    current_user_id = int(request.state.user.get("user_id"))

    service = OfferApprovalActionService(db)
    return await service.create_offer_actions(payload, current_user_id)