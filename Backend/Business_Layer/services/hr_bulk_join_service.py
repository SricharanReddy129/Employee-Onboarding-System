from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.hr_bulk_join_dao import HrBulkJoinDAO

class HrBulkJoinService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = HrBulkJoinDAO(self.db)

    async def process_bulk_join(self, payload, current_user_id: int):
        # 1. Basic validation
        if not payload.user_emails_list:
            raise HTTPException(status_code=400, detail="No users selected")

        # 2. Count how many VERIFIED users exist
        verified_count = await self.dao.count_verified_by_emails(
            payload.user_emails_list
        )

        if verified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No VERIFIED candidates found for Bulk Join"
            )

        # 3. Update ONLY VERIFIED users
        updated_rows = await self.dao.update_joining_date_for_verified(
            payload.user_emails_list,
            payload.joining_date
        )

        skipped = len(payload.user_emails_list) - updated_rows

        return {
            "message": "Bulk Join processed successfully",
            "joining_date": payload.joining_date,
            "updated_verified_users": updated_rows,
            "skipped_not_verified": skipped
        }
