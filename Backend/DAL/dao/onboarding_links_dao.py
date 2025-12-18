from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from  sqlalchemy import select
from Backend.Business_Layer.utils.email_token_utils import generate_mixed_month_time_token, hash_token
from Backend.DAL.models.models import OnboardingLinks

class OnboardingLinkDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    async def create_onboarding_link(
        self,
        user_uuid: str,
        email: str,
        expires_in_hours: int = 24
    ) -> str:
            """
            Creates onboarding link entry and returns the RAW token
            (raw token should be sent via email).
            """

            raw_token = generate_mixed_month_time_token()
            token_hash = hash_token(raw_token)
            print("Token ", raw_token, " Hash ", token_hash)
            onboarding_link = OnboardingLinks(
                user_uuid=user_uuid,
                email=email,
                token_hash=token_hash,
                expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
            )

            try:
                self.db.add(onboarding_link)
                await self.db.commit()
                await self.db.refresh(onboarding_link)
                return raw_token

            except IntegrityError:
                # Safety net for race conditions
                await self.db.rollback()