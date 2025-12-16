import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.dao.otp_dao import OtpResponseDAO
from Backend.API_Layer.interfaces.otp_interfaces import OtpResponseStatus

class OtpResponseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OtpResponseDAO(self.db)

    async def verify_otp(self, email: str, otp: str) -> OtpResponseStatus:
        otp_record = await self.dao.get_otp_by_email(email)

        # ❌ No OTP found → nothing to delete
        if not otp_record:
            return OtpResponseStatus(
                status="FAILED",
                message="OTP not found"
            )

        try:
            # ⏰ OTP expired
            if datetime.datetime.utcnow() > otp_record.expirytime:
                return OtpResponseStatus(
                    status="FAILED",
                    message="OTP expired"
                )

            # ❌ Incorrect OTP
            if otp_record.otp != otp:
                return OtpResponseStatus(
                    status="FAILED",
                    message="Incorrect OTP"
                )

            # ✅ OTP verified
            return OtpResponseStatus(
                status="SUCCESS",
                message="OTP verified successfully"
            )

        finally:
            # 🔥 Safe delete (only if record exists)
            if otp_record:
                await self.dao.delete_otp(otp_record)
