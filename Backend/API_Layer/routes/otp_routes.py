from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.API_Layer.interfaces.otp_interfaces import OtpRequestBody, OtpResponseStatus
from Backend.Business_Layer.services.otp_service import OtpResponseService
from ...DAL.utils.dependencies import get_db

router = APIRouter()

@router.post("/verifyOtp", response_model=OtpResponseStatus)
async def verify_otp(
    requestdata: OtpRequestBody,
    db: AsyncSession = Depends(get_db)
):
    """Verifies the OTP sent to the user's email."""
    service = OtpResponseService(db)
    return await service.verify_otp(requestdata.email, requestdata.otp)