from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.dao.offer_approval_request import OfferApprovalRequestDAO
from Backend.API_Layer.interfaces.offer_request_interfaces import OfferRequestCreateResponse


class OfferApprovalRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferApprovalRequestDAO(self.db)

    async def create_offer_approval_requests(
        self,
        request_list: list[OfferRequestCreateResponse]
    ):
        """
        Create multiple offer approval requests (bulk)
        """
        try:
            if not request_list:
                raise ValueError("Request list cannot be empty")

            for request in request_list:
                # 🔴 VALIDATION: Check duplicate request
                existing_request = await self.dao.check_request_exists_by_user_uuid(
                    request.user_uuid
                )
            
            if existing_request:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Approval request already exists for users"
                    )

            created_requests = []

            for request in request_list:
                result = await self.dao.create_approval_request(
                    user_uuid=request.user_uuid,
                    request_by=request.request_by,
                    action_taker_id=request.action_taker_id
                )

                if not result:
                    raise Exception(
                        f"Failed to create approval request for user_uuid: {request.user_uuid}"
                    )

                created_requests.append(result)

            return {
                "message": "Offer approval requests created successfully",
                "count": len(created_requests)
            }

        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
