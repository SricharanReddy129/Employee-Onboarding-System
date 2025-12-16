from Backend.DAL.dao.otp_dao import OtpResponseDAO
from sqlalchemy.ext.asyncio import AsyncSession

class OtpResponseService:
  def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OtpResponseDAO(self.db)

