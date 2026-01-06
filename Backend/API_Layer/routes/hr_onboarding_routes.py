

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...DAL.utils.dependencies import get_db
from ...Business_Layer.services.hr_onboarding_service import (HrOnboardingService)

router = APIRouter()

@router.get("/onboarding/{user_uuid}")
async def get_full_onboarding_details(user_uuid: str,request: Request, db: AsyncSession = Depends(get_db)):
    current_user_id = int(request.state.user.get("user_id"))
    service = HrOnboardingService(db)
    data = await service.get_full_onboarding_details(user_uuid, current_user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User onboarding data not found")

    return data
