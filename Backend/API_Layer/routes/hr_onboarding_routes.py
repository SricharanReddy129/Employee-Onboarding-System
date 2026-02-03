

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import unquote
from ...DAL.utils.dependencies import get_db
from ...Business_Layer.services.hr_onboarding_service import (HrOnboardingService)
from ...API_Layer.interfaces.candidate_submit_forms_interfaces import HrOnboardingSubmitRequest
from ...API_Layer.interfaces.hr_onboarding_interfaces import HRVerificationRequest
from ..utils.role_based import require_roles

router = APIRouter()


@router.get("/hr/{user_uuid}", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_full_onboarding_details(user_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user_id = int(request.state.user.get("user_id"))
    service = HrOnboardingService(db)
    data = await service.get_full_onboarding_details(user_uuid, current_user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User onboarding data not found")
    return data



@router.post("/candidate/submit", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def submit_onboarding(
    user_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    service = HrOnboardingService(db)

    await service.final_submit_onboarding(user_uuid)
    return {"message": "Onboarding submitted successfully"}


@router.get("/view_documents", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def view_onboarding_documents(file_path: str, db: AsyncSession = Depends(get_db)):
    try:
        file_path = unquote(file_path)
        print("route file path:", file_path)
        service = HrOnboardingService(db)
        document_url = await service.view_onboarding_documents(file_path)
        return  document_url
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
          
@router.post("/verify-profile", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def verify_employee_profile(
    payload: HRVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HR verifies or rejects an employee profile
    """
    current_user_id = int(request.state.user.get("user_id"))

    service = HrOnboardingService(db)

    await service.update_verification_status(
        user_uuid=payload.user_uuid,
        status=payload.status,
        current_user_id=current_user_id
    )

    return {
        "message": "Verification status updated successfully"
    }
