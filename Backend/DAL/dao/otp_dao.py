from sqlalchemy.ext.asyncio import AsyncSession


class OtpResponseDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    