from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.dao.token_verification_dao import TokenVerificationDAO
from Backend.API_Layer.interfaces.token_verification_interfaces import TokenVerificationRequest, TokenVerificationResponse

class OnboardingVerifyLinkService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = TokenVerificationDAO(self.db)
    async def verify_token(self, request: TokenVerificationRequest) -> TokenVerificationResponse:
        """
        Business logic:
        - Hash the raw token
        - Query the DAO for a valid link
        - Return the result
        """

        print("📌 Business Layer: Verifying token")

        # ----------------------------
        # 1️⃣ Query DAO for valid link
        # ----------------------------
        valid_link = await self.dao.get_valid_link_by_token(request.raw_token)

        # ----------------------------
        # 2️⃣ Prepare response
        if valid_link:
            return TokenVerificationResponse(is_valid=True, message="Token is valid.")
        else:
            return TokenVerificationResponse(is_valid=False, message="Token is invalid or expired.")
        