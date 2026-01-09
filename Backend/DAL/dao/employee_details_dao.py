from ..models.models import PersonalDetails, Addresses, EmployeeIdentityDocument
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import date
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

# Adresses DAO
class AddressDAO:
    def __init__(self, db: AsyncSession):
        self.db = db
    async def get_address_by_user_uuid_and_address_type(self, user_uuid, address_type):
        result = await self.db.execute(select(Addresses).where(Addresses.user_uuid == user_uuid).where(Addresses.address_type == address_type))
        return result.scalar_one_or_none()
    async def get_address_by_address_uuid(self, address_uuid):
        result = await self.db.execute(select(Addresses).where(Addresses.address_uuid == address_uuid))
        return result.scalar_one_or_none()
    async def get_all_addresses(self):
        result = await self.db.execute(select(Addresses))
        return result.scalars().all()
    async def create_address(self, request_data, uuid):
        permanent_address = Addresses(
            address_uuid = uuid,
            user_uuid = request_data.user_uuid,
            address_type = request_data.address_type,
            address_line1 = request_data.address_line1,
            address_line2 = request_data.address_line2,
            city = request_data.city,
            district_or_ward = request_data.district_or_ward,
            state_or_region = request_data.state_or_region,
            country_uuid = request_data.country_uuid,
            postal_code = request_data.postal_code
        )
        self.db.add(permanent_address)
        await self.db.commit()
        await self.db.refresh(permanent_address)
        return permanent_address
    async def update_address(self, uuid, request_data):
        result = await self.db.execute(select(Addresses).where(Addresses.address_uuid == uuid))
        permanent_address = result.scalar_one_or_none()
        if not permanent_address:
            return None
        permanent_address.user_uuid = request_data.user_uuid
        permanent_address.address_type = request_data.address_type
        permanent_address.address_line1 = request_data.address_line1
        permanent_address.address_line2 = request_data.address_line2
        permanent_address.city = request_data.city
        permanent_address.district_or_ward = request_data.district_or_ward
        permanent_address.state_or_region = request_data.state_or_region
        permanent_address.country_uuid = request_data.country_uuid
        permanent_address.postal_code = request_data.postal_code
        await self.db.commit()
        await self.db.refresh(permanent_address)
        return permanent_address
    async def delete_address(self, uuid):
        result = await self.db.execute(select(Addresses).where(Addresses.address_uuid == uuid))
        address = result.scalar_one_or_none()
        await self.db.delete(address)
        await self.db.commit()
        return address
    
class EmployeeIdentityDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employee_identity_by_user_uuid_and_mapping_uuid(self, user_uuid, mapping_uuid):
        result = await self.db.execute(select(EmployeeIdentityDocument).where(EmployeeIdentityDocument.user_uuid == user_uuid).
                                       where(EmployeeIdentityDocument.mapping_uuid == mapping_uuid))
        return result.scalar_one_or_none()
    async def create_employee_identity(
        self,
        mapping_uuid: str,
        user_uuid: str,
        identity_file_number: Optional[str],
        expiry_date: Optional[date],
        file_path: str,
        uuid: str
    ):

        employee_identity = EmployeeIdentityDocument(
            document_uuid=uuid,
            mapping_uuid=mapping_uuid,
            user_uuid=user_uuid,
            identity_file_number=identity_file_number,
            expiry_date=expiry_date,
            file_path=file_path,
            status="uploaded"
        )

        self.db.add(employee_identity)
        await self.db.commit()
        await self.db.refresh(employee_identity)

        return employee_identity