from email.mime import text
from sqlalchemy import text
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from Backend.API_Layer.interfaces.token_verification_interfaces import TokenVerificationRequest, TokenVerificationResponse
from Backend.Business_Layer.services.token_verification_service import OnboardingVerifyLinkService

router = APIRouter()
@router.post("/verify_token")
async def verify_token(
    requestdata: TokenVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verifies the onboarding token sent to the user's email."""

    service = OnboardingVerifyLinkService(db)
    print(f"🔐 API: Verifying token...")

    result = await service.verify_token(requestdata)

    return result

@router.get("/{raw_token}")
async def get_user_uuid_by_token(
    raw_token: str,
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingVerifyLinkService(db)
    user_uuid = await service.get_user_uuid_by_token(raw_token)

    result = await db.execute(
        text("SELECT 1 FROM offer_letter_details WHERE user_uuid = :user_uuid"),
        {"user_uuid": user_uuid}
    )

    if not result.first():
        await db.execute(
            text("INSERT INTO offer_letter_details (user_uuid) VALUES (:user_uuid)"),
            {"user_uuid": user_uuid}
        )
        await db.commit()

    return user_uuid

# @router.get("/{raw_token}")
# async def get_user_uuid_by_token(
#     raw_token: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     service = OnboardingVerifyLinkService(db)
#     user_uuid = await service.get_user_uuid_by_token(raw_token)

#     await db.execute(
#         text("""
#             INSERT INTO offer_letter_details (user_uuid)
#             VALUES (:user_uuid)
#             ON DUPLICATE KEY UPDATE user_uuid = user_uuid
#         """),
#         {"user_uuid": user_uuid}
#     )
#     await db.commit()
#     return user_uuid