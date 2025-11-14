from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ...DAL.dao.master_dao import  MasterDAO
from ...API_Layer.interfaces.master_interfaces import CreateCountryRequest
from ..utils.validation_utils import validate_country_code, validate_alphabets_only
from ..utils.uuid_generator import generate_uuid7


class CountryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = MasterDAO(self.db)
    async def create_country(self, request_data: CreateCountryRequest):
        try:
            country_name = validate_alphabets_only(request_data.country_name)
            country_code = validate_country_code(request_data.calling_code)
            existing = await self.dao.get_country_by_code(country_code)

            if existing:
                raise ValueError("Country Already Exists")
            uuid = generate_uuid7()
            country = await self.dao.create_country(uuid, request_data)
            return uuid
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
