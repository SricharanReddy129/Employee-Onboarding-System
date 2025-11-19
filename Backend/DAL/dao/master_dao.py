# Backend/DAL/dao/master_dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import Countries, EducationLevel, CountryEducationDocumentMapping
from ...API_Layer.interfaces.master_interfaces import CreateEducLevelRequest, EducLevelDetails


class MasterDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management
    
    async def get_country_by_code(self, code : str):
        result = await self.db.execute(
            select(Countries).where(Countries.calling_code == code)
        )

        return result.scalar_one_or_none()
    async def create_country(self, uuid: str, calling_code: str, country_name: str):
        new_country = Countries(
            country_uuid = uuid,
            country_name = country_name,
            calling_code = calling_code
        )
        self.db.add(new_country)
        await self.db.commit()
        await self.db.refresh(new_country)
        return new_country
    async def get_country_by_uuid(self, country_uuid: str):
        result = await self.db.execute(
            select(Countries).where(Countries.country_uuid == country_uuid)
        )

        return result.scalar_one_or_none()
    async def update_country(self, country_uuid: str, is_active: bool):
        result = await self.db.execute(
            select(Countries).where(Countries.country_uuid == country_uuid)
        )
        
        country = result.scalar_one_or_none()
        if country is None:
            return None
        
        country.is_active = 1 if is_active else 0

        await self.db.commit()
        await self.db.refresh(country)

        return country
    async def get_all_countries(self):
        result = await self.db.execute(select(Countries))
        return result.scalars().all()

class EducationDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management
    async def get_education_level_by_eduname(self, education_name):
        result = await self.db.execute(
            select(EducationLevel).where(EducationLevel.education_name == education_name)
        )
        
        return result.scalar_one_or_none()
    async def create_education_level(self, request_data: CreateEducLevelRequest, uuid: str):
        new_edu_level = EducationLevel(
            education_uuid = uuid,
            education_name = request_data.education_name,
            description = request_data.description
        )
        self.db.add(new_edu_level)
        await self.db.commit()
        await self.db.refresh(new_edu_level)
        return new_edu_level

    async def get_all_education_levels(self):
        result = await self.db.execute(select(EducationLevel))
        return result.scalars().all()
    
    async def get_education_level_by_uuid(self, uuid: str):
        result = await self.db.execute(select(EducationLevel).where(EducationLevel.education_uuid == uuid))
        return result.scalar_one_or_none()
    
    async def get_education_level_by_eduname_and_uuid(self, education_name: str, education_uuid: str):
        result = await self.db.execute(select(EducationLevel).where(EducationLevel.education_name == education_name).where(EducationLevel.education_uuid != education_uuid))
        
        return result.scalar_one_or_none()

    async def update_education_level(self, request_data: EducLevelDetails, uuid: str):
        result = await self.db.execute(
            select(EducationLevel).where(EducationLevel.education_uuid == uuid)
        )
        
        edu_level = result.scalar_one_or_none()
        if edu_level is None:
            return None
        
        edu_level.education_name = request_data.education_name
        edu_level.description = request_data.description
        edu_level.is_active = request_data.is_active

        await self.db.commit()
        await self.db.refresh(edu_level)

        return edu_level
    
    async def delete_education_level(self, uuid: str):
        result = await self.db.execute(select(EducationLevel).where(EducationLevel.education_uuid == uuid))
        edu_level = result.scalar_one_or_none()
        if edu_level is None:
            return None
        await self.db.delete(edu_level)
        await self.db.commit()
        return edu_level
    async def create_education_country_mapping(self, educ_level_uuid, educ_doc_uuid, country_uuid, uuid):
        new_edu_country_mapping = CountryEducationDocumentMapping(
            mapping_uuid = uuid,
            education_uuid = educ_level_uuid,
            education_document_uuid = educ_doc_uuid,
            country_uuid = country_uuid
        )
        self.db.add(new_edu_country_mapping)
        await self.db.commit()
        await self.db.refresh(new_edu_country_mapping)
        return new_edu_country_mapping
    
    async def check_education_country_mapping(self, educ_level_uuid, educ_doc_uuid, country_uuid):
        result = await self.db.execute(select(CountryEducationDocumentMapping).where(
            CountryEducationDocumentMapping.education_document_uuid == educ_doc_uuid).where(
            CountryEducationDocumentMapping.country_uuid == country_uuid).where(
                CountryEducationDocumentMapping.education_uuid == educ_level_uuid))
        
        return result.scalar_one_or_none()
    
    async def get_education_country_mapping_by_uuid(self, mappng_uuid):
        result = await self.db.execute(select(CountryEducationDocumentMapping).where(CountryEducationDocumentMapping.mapping_uuid == mappng_uuid))
        return result.scalar_one_or_none()
    async def delete_education_country_mapping(self, mappng_uuid):
        result = await self.db.execute(select(CountryEducationDocumentMapping).where(CountryEducationDocumentMapping.mapping_uuid == mappng_uuid))
        edu_country_mapping = result.scalar_one_or_none()
        if edu_country_mapping is None:
            return None
        await self.db.delete(edu_country_mapping)
        await self.db.commit()
        return edu_country_mapping
    async def get_all_education_country_mapping(self):
        result = await self.db.execute(select(CountryEducationDocumentMapping))
        return result.scalars().all()
