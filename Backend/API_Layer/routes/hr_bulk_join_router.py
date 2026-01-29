from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from  ...API_Layer.interfaces.bulk_join_request_interfaces import BulkJoinRequest
from ...Business_Layer.services.hr_bulk_join_service import HrBulkJoinService

router = APIRouter()

@router.post("/offerletters/bulk-join")
async def bulk_join(
    payload: BulkJoinRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        current_user_id = int(request.state.user.get("user_id"))

        service = HrBulkJoinService(db)
        result = await service.process_bulk_join(payload, current_user_id)

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
