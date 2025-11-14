from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ...DAL.dao.master_dao import  MasterDAO, EducationDAO
from ..utils.validation_utils import validate_country_code, validate_alphabets_only, validate_country
from ..utils.uuid_generator import generate_uuid7
from ...API_Layer.interfaces.master_interfaces import CreateEducLevelRequest


class CountryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = MasterDAO(self.db)
    async def create_country(self, calling_code: str):
        try:
            country_name = validate_country(calling_code)
            existing = await self.dao.get_country_by_code(calling_code)

            if existing:
                raise ValueError("Country Already Exists")
            uuid = generate_uuid7()
            country = await self.dao.create_country(uuid, calling_code, country_name)
            return uuid
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_country_uuid(self, country_uuid: str):
        try:
            if not country_uuid:
                raise ValueError("Not Empty Country uuid")
            result = await self.dao.get_country_by_uuid(country_uuid)
            if not result:
                raise ValueError("Not Country Details Found")
            return result
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_country(self, country_uuid: str, is_active: bool):
        try:
            existing = await self.dao.get_country_by_uuid(country_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Country does not exist")

            updated = await self.dao.update_country(country_uuid, is_active)

            # Normalize boolean for consistent logic
            if is_active:
                return "Successfully Activated"
            else:
                return "Successfully Deactivated"

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class EducationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EducationDAO(self.db)
    async def create_education_level(self, request_data: CreateEducLevelRequest):
        try:
            education_name = validate_alphabets_only(request_data.education_name)
            education_name = await self.dao.get_education_level_by_eduname(education_name)
            uuid = generate_uuid7()
            if education_name:
                raise HTTPException(status_code=404, detail = "Education Level Already Exist")
            return await self.dao.create_education_level(request_data, uuid)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    



            
