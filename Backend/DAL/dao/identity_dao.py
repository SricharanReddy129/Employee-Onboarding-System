import dbm
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
    
    async def get_identity_type_by_name_and_status(self, name, is_active):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_name == name).where(IdentityType.is_active == is_active))
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
    
    # Country Identity Mapping DAO Methods
    async def get_country_identity_mapping(self, country_uuid, identity_type_uuid):
        result = await self.db.execute(select(CountryIdentityMapping).where(CountryIdentityMapping.country_uuid == country_uuid).where(
            CountryIdentityMapping.identity_type_uuid == identity_type_uuid
        ))
        return result.scalar_one_or_none()
    
    async def create_country_identity_mapping(self, request_data, uuid):
        country_identity_mapping = CountryIdentityMapping(
            mapping_uuid = uuid,
            country_uuid = request_data.country_uuid,
            identity_type_uuid = request_data.identity_type_uuid,
            is_mandatory = request_data.is_mandatory
        )
        self.db.add(country_identity_mapping)
        await self.db.commit()
        await self.db.refresh(country_identity_mapping)
        return country_identity_mapping
    async def get_country_identity_mapping_by_uuid(self, uuid):
        result = await self.db.execute(select(CountryIdentityMapping).where(CountryIdentityMapping.mapping_uuid == uuid))
        return result.scalar_one_or_none()
    
    async def get_all_country_identity_mappings(self):
        result = await self.db.execute(select(CountryIdentityMapping))
        return result.scalars().all()
    
    async def update_country_identity_mapping(self, uuid, request_data):
        result = await self.db.execute(select(CountryIdentityMapping).where(CountryIdentityMapping.mapping_uuid == uuid))
        mapping = result.scalar_one_or_none()
        mapping.country_uuid = request_data.country_uuid
        mapping.identity_type_uuid = request_data.identity_type_uuid
        mapping.is_mandatory = request_data.is_mandatory
        self.db.add(mapping)
        await self.db.commit()
        await self.db.refresh(mapping)
        return mapping
    
    async def delete_country_identity_mapping(self, uuid):
        result = await self.db.execute(select(CountryIdentityMapping).where(CountryIdentityMapping.mapping_uuid == uuid))
        mapping = result.scalar_one_or_none()
        await self.db.delete(mapping)
        await self.db.commit()
        return mapping
    
    async def get_identities_by_country_uuid(self, country_uuid: str):
        stmt = (
            select(
                IdentityType.identity_type_uuid,
                IdentityType.identity_type_name,
                CountryIdentityMapping.is_mandatory
            )
            .join(
                IdentityType,
                CountryIdentityMapping.identity_type_uuid
                == IdentityType.identity_type_uuid
            )
            .where(
                CountryIdentityMapping.country_uuid == country_uuid,
                CountryIdentityMapping.is_mandatory == True
            )
        )

        result = await self.db.execute(stmt)
        return result.all()
