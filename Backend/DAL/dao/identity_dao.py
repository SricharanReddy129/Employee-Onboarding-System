from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import IdentityType, CountryIdentityMapping, EmployeeIdentityDocument
from sqlalchemy import select

class IdentityDAO:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_identity_types(self):
        result = await self.db.execute(select(IdentityType))
        return result.scalars().all()
    
    async def get_identity_type_by_uuid(self, uuid):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_uuid == uuid))
        return result.scalar_one_or_none()
    
    async def get_identity_type_by_name(self, name):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_name == name))
        return result.scalar_one_or_none()
    
    async def create_identity_type(self, request_data, uuid):
        identity_type = IdentityType(
            identity_type_uuid = uuid,
            identity_type_name = request_data.identity_type_name,
            description = request_data.description,
            is_active = request_data.is_active
        )
        self.db.add(identity_type)
        await self.db.commit()
        await self.db.refresh(identity_type)
        return identity_type
    async def delete_identity_type(self, uuid):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_uuid == uuid))
        identity_type = result.scalar_one_or_none()
        await self.db.delete(identity_type)
        await self.db.commit()
        return identity_type
    async def update_identity_type(self, uuid, request_data):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_uuid == uuid))
        identity_type = result.scalar_one_or_none()
        identity_type.identity_type_name = request_data.identity_type_name
        identity_type.description = request_data.description
        identity_type.is_active = request_data.is_active
        self.db.add(identity_type)
        await self.db.commit()
        await self.db.refresh(identity_type)
        return identity_type