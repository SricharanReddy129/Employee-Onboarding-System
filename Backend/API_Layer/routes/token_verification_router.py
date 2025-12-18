from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from Backend.API_Layer.interfaces.token_verification_interfaces import TokenVerificationRequest, TokenVerificationResponse
from Backend.Business_Layer.services.token_verification_service import OnboardingVerifyLinkService

router = APIRouter()
@router.post("/verify_token", response_model=TokenVerificationResponse)
async def verify_token(
    requestdata: TokenVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verifies the onboarding token sent to the user's email."""

    service = OnboardingVerifyLinkService(db)
    print(f"🔐 API: Verifying token...")

    result = await service.verify_token(requestdata)

    if not result.is_valid:
        raise HTTPException(
            status_code=400,
            detail=result.message
        )

    return result