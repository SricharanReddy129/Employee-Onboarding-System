from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ...DAL.models.models import OfferLetterDetails

class HrBulkJoinDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_verified_by_emails(self, email_list):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.mail.in_(email_list),
            OfferLetterDetails.status == "Verified"
        )

        result = await self.db.execute(query)
        rows = result.scalars().all()

        return len(rows)

    async def update_joining_date_for_verified(self, email_list, joining_date):
        stmt = (
            update(OfferLetterDetails)
            .where(
                OfferLetterDetails.mail.in_(email_list),
                OfferLetterDetails.status == "Verified"
            )
            .values(
                joining_date=joining_date
            )
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        # result.rowcount = number of updated rows
        return result.rowcount
