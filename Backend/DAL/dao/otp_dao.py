from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Backend.DAL.models.models import Otptable

class OtpResponseDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_otp_by_email(self, email: str):
        query = select(Otptable).where(Otptable.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()
