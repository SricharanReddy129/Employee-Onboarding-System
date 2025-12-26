from Backend.Business_Layer.utils.ums_users_list import fetch_admin_users_reformed
from fastapi import HTTPException
from Backend.API_Layer.interfaces.offer_approve_action_interfaces import OfferApproveActionRequest
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.dao.offer_approval_action_dao import OfferApprovalActionDAO
from Backend.API_Layer.interfaces.offer_request_interfaces import OfferRequestResponse

from Backend.DAL.dao.offer_approval_action_dao import OfferApprovalActionDAO
from Backend.API_Layer.interfaces.offer_request_interfaces import OfferRequestResponse

from Backend.DAL.dao.offerresponse_dao import OfferResponseDAO
from Backend.API_Layer.interfaces.OfferActionAdmin_interfaces import OfferActionAdminResponse



class OfferApprovalActionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferApprovalActionDAO(db)
        self.offer_response_dao = OfferResponseDAO(db)

    async def get_offer_status(self, user_uuid: str, auth_header: str) -> OfferRequestResponse:
        """
        Resolve offer approval status using business rules
        """

        request = await self.dao.get_request_with_actions(user_uuid)


        # ❌ No request exists
        if not request:
            return OfferRequestResponse(
                user_uuid=user_uuid,
                action_taker_id=0,
                action_taker_name="No user",
                status="No Request",
                comments="No Request."
            )
        
        user_details = await fetch_admin_users_reformed(token=auth_header)
        action_taker = next(
            (u for u in user_details if u["user_id"] == request.action_taker_id),
            None
        )

        if not action_taker:
            raise HTTPException(
                status_code=400,
                detail="Action taker not found in user list"
            )
        
        # ✅ Request exists but no action yet
        if not request.offer_approval_action:
            return OfferRequestResponse(
                user_uuid=user_uuid,
                action_taker_id=request.action_taker_id,
                action_taker_name=action_taker['name'],  # demo
                status="PENDING",
                comments="Awaiting approval"
            )

        # ✅ Request + action exists → take latest action
        latest_action = request.offer_approval_action[-1]


        return OfferRequestResponse(
            user_uuid=user_uuid,
            action_taker_id=request.action_taker_id,
            action_taker_name=action_taker['name'],  # demo
            status=latest_action.action,
            comments=latest_action.comment or ""
        )

    async def get_all_offer_statuses(self, auth_header: str) -> list[OfferRequestResponse]:
        """
        Resolve offer approval status for ALL users
        """

        user_details = await fetch_admin_users_reformed(token=auth_header)
        
        requests = await self.dao.get_all_requests_with_actions()

        response: list[OfferRequestResponse] = []

        for request in requests:

            action_taker = next(
                (u for u in user_details if u["user_id"] == request.action_taker_id),
                None
            )

            # ❌ Request exists but no action
            if not request.offer_approval_action:
                response.append(
                    OfferRequestResponse(
                        user_uuid=request.user_uuid,
                        action_taker_id=request.action_taker_id,
                        action_taker_name=action_taker['name'] if action_taker else "Unknown",
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
                    action_taker_name=action_taker['name'] if action_taker else "Unknown",
                    status=latest_action.action,
                    comments=latest_action.comment or ""
                )
            )

        return response
    
    async def create_offer_actions(
        self,
        payload: list[OfferApproveActionRequest],
        current_user_id: int
    ):
        if not payload:
            raise HTTPException(status_code=422, detail="Payload cannot be empty")

        created = []

        for item in payload:
            # 🔍 Validate request
            request = await self.dao.get_request_by_user_uuid(item.user_uuid)
            if not request:
                raise HTTPException(
                    status_code=404,
                    detail=f"No approval request found users"
                )
            
             # 🔐 VALIDATION: only assigned approver can act
            if request.action_taker_id != current_user_id:
                raise HTTPException(
                    status_code=401,
                    detail=(
                        f"You are not authorized to take action."
                    )
                )
            
             # ❌ NEW VALIDATION — already reviewed
            already_reviewed = await self.dao.has_action_for_request(request.id)
            if already_reviewed:
                raise HTTPException(
                    status_code=400,   # Conflict
                    detail="Action already taken for this user"
                )

            # ✅ Normalize action
            action = item.action.upper()
            if action not in {"APPROVED", "REJECTED", "ON_HOLD"}:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid action should be APPROVED / REJECTED / ON_HOLD"
                )
            

            result = await self.dao.create_action(
                request_id=request.id,
                action=action,
                comment=item.comments
            )

            if not result:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to insert action "
                )

            created.append({
                "user_uuid": item.user_uuid,
                "status": action,
                "comments": item.comments
            })

        return "Successfully created actions"
    
    async def update_offer_action(
    self,
    user_uuid: str,
    action: str,
    comments: str,
    current_user_id: int
):

        # 🔍 Fetch offer letter
        offer = await self.offer_response_dao.get_offer_by_uuid(user_uuid)
        if not offer:
            raise HTTPException(
                status_code=404,
                detail="Offer letter not found"
            )

        # ❌ Status must be Created
        if offer.status != "Created":
            raise HTTPException(
                status_code=400,
                detail="Offer already processed"
            )

        # 🔍 Fetch approval request
        request = await self.dao.get_request_by_user_uuid(user_uuid)
        if not request:
            raise HTTPException(
                status_code=404,
                detail="Approval request not found"
            )

        # 🔐 Action taker validation
        if request.action_taker_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to take action"
            )

        # ✅ Normalize & validate action
        action = action.upper()
        if action not in {"APPROVED", "REJECTED", "ON_HOLD"}:
            raise HTTPException(
                status_code=422,
                detail="Invalid action"
            )

        # 🔍 Fetch existing action (IMPORTANT)
        existing_action = await self.dao.get_action_by_request_id(request.id)
        if not existing_action:
            raise HTTPException(
                status_code=400,
                detail="No existing action found to update"
            )
        
        # ✅ Update action fields # 🔄 UPDATE action (NOT INSERT)
        await self.dao.update_action(
            action_id=existing_action.id,
            action=action,
            comment=comments
        )
        return {
            "message": "Offer action updated successfully"
        }
    
    async def get_admin_actions(
        self,
        current_user_id: int,
        auth_header: str
    ) -> list[OfferActionAdminResponse]:

        requests = await self.dao.get_requests_for_action_taker(current_user_id)

        response: list[OfferActionAdminResponse] = []

        for req in requests:

            user_details = await fetch_admin_users_reformed(token=auth_header)
            action_taker = next((u for u in user_details if u["user_id"] == req.request_by), None)

            offer = req.offer_letter_details

            # 🔍 Determine action status
            if req.offer_approval_action:
                latest_action = req.offer_approval_action[-1]
                action = latest_action.action
                message = latest_action.comment or "Action taken"
            else:
                action = "PENDING"
                message = "Awaiting approval"

            response.append(
                OfferActionAdminResponse(
                    user_uuid=offer.user_uuid,
                    user_first_name=offer.first_name,
                    user_last_name=offer.last_name,

                    # ✅ request_id = request_by (HR user id)
                    request_id=str(req.request_by),

                    # 🧪 Mock value for now
                    requested_name=action_taker['name'] if action_taker else "Unknown",

                    action=action,
                    message=message
                )
            )

        return response