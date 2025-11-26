from ..models.models import PersonalDetails, PermanentAddresses, CurrentAddresses
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
class EmployeeDetailsDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_personal_details_by_user_uuid(self, user_uuid):
        result = await self.db.execute(select(PersonalDetails).where(PersonalDetails.user_uuid == user_uuid))
        return result.scalar_one_or_none()
    async def get_personal_details_by_uuid(self, uuid):
        result = await self.db.execute(select(PersonalDetails).where(PersonalDetails.personal_uuid == uuid))
        return result.scalar_one_or_none()
    async def get_all_personal_details(self):
        result = await self.db.execute(select(PersonalDetails))
        return result.scalars().all()
    async def create_personal_details(self, request_data, uuid):
        personal_details = PersonalDetails(
            personal_uuid = uuid,
            user_uuid = request_data.user_uuid,
            date_of_birth = request_data.date_of_birth,
            gender = request_data.gender,
            marital_status = request_data.marital_status,
            blood_group = request_data.blood_group,
            nationality_country_uuid = request_data.nationality_country_uuid,
            residence_country_uuid = request_data.residence_country_uuid

        )
        self.db.add(personal_details)
        await self.db.commit()
        await self.db.refresh(personal_details)
        return personal_details
    async def update_personal_details(self, personal_uuid, request_data):
        result = await self.db.execute(select(PersonalDetails).where(PersonalDetails.personal_uuid == personal_uuid))
        personal_details = result.scalar_one_or_none()
        if not personal_details:
            return None
        personal_details.date_of_birth = request_data.date_of_birth
        personal_details.gender = request_data.gender
        personal_details.marital_status = request_data.marital_status
        personal_details.blood_group = request_data.blood_group
        personal_details.nationality_country_uuid = request_data.nationality_country_uuid
        personal_details.residence_country_uuid = request_data.residence_country_uuid
        await self.db.commit()
        await self.db.refresh(personal_details)
        return personal_details
    async def delete_personal_details(self, personal_uuid):
        result = await self.db.execute(select(PersonalDetails).where(PersonalDetails.personal_uuid == personal_uuid))
        personal_details = result.scalar_one_or_none()
        self.db.delete(personal_details)
        await self.db.commit()
        return personal_details