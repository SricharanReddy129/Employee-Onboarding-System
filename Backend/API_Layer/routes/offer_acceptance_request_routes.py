from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.ext.asyncio import AsyncSession


from ...Business_Layer.services.offer_approval_service import OfferApprovalRequestService
from ...API_Layer.interfaces.offer_request_interfaces import OfferRequestCreateResponse

from ...DAL.utils.dependencies import get_db

router = APIRouter()

@router.post("/request")
async def create_offer_approval_requests(
    payload: list[OfferRequestCreateResponse],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HR sends offer approval request(s) to higher authority
    """
    service = OfferApprovalRequestService(db)

    current_user_id = int(request.state.user.get("user_id"))  # Access user info from request state
    print("current user id:", current_user_id)

    print("payload:", payload)

    updated_payload = []
    for item in payload:
        updated_payload.append(
            OfferRequestCreateResponse(
                user_uuid=item.user_uuid,
                request_by=current_user_id,   # 👈 HR id
                action_taker_id=item.action_taker_id
            )
        )

    print("updated payload:", updated_payload)

    result = await service.create_offer_approval_requests(updated_payload)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to create offer approval requests"
        )

    return result
