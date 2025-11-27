from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.employee_details_dao import EmployeeDetailsDAO, AddressDAO
from ...DAL.dao.master_dao import CountryDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ..utils.validation_utils import validate_date_of_birth, validate_blood_group
from ..utils.uuid_generator import generate_uuid7
from ..utils.postal_code_validator import validate_postal_code

class EmployeeDetailsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeDetailsDAO(self.db)
        self.countrydao = CountryDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
    
    async def create_personal_details(self, request_data):
        try:
            existing = await self.offerdao.get_offer_by_uuid(request_data.user_uuid)
            if not existing:
                raise ValueError("User Not Found")
            validate_blood_group(request_data.blood_group)
            validate_date_of_birth(request_data.date_of_birth)
            existing = await self.countrydao.get_country_by_uuid(request_data.nationality_country_uuid)
            if not existing:
                raise ValueError("Nationality Country Not Found")
            existing = await self.countrydao.get_country_by_uuid(request_data.residence_country_uuid)
            if not existing:
                raise ValueError("Residence Country Not Found")
            uuid = generate_uuid7()
            result = await self.dao.create_personal_details(request_data, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_all_personal_details(self):
        try:
            result = await self.dao.get_all_personal_details()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_personal_details_by_user_uuid(self, uuid):
        try:
            result = await self.dao.get_personal_details_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=200, detail="No Personal Details Found for this Employee")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def update_personal_details(self, uuid, request_data):
        try:
            existing = await self.dao.get_personal_details_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Personal Details Not Found")
            validate_blood_group(request_data.blood_group)
            validate_date_of_birth(request_data.date_of_birth)
            existing = await self.countrydao.get_country_by_uuid(request_data.nationality_country_uuid)
            if not existing:
                raise ValueError("Nationality Country Not Found")
            existing = await self.countrydao.get_country_by_uuid(request_data.residence_country_uuid)
            if not existing:
                raise ValueError("Residence Country Not Found")
            result = await self.dao.update_personal_details(uuid, request_data)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def delete_personal_details(self, uuid):
        try:
            existing = await self.dao.get_personal_details_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code = 404, detail= "Personal Details Not Found")
            result = await self.dao.delete_personal_details(uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Addresses Service
class AddressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = AddressDAO(self.db)
        self.countrydao = CountryDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
    async def create_address(self, request_data):
        try:
            existing = await self.offerdao.get_offer_by_uuid(request_data.user_uuid)
            if not existing:
                raise HTTPException(status_code = 404, detail = "User Not Found")
            country_existing = await self.countrydao.get_country_by_uuid(request_data.country_uuid)
            if not country_existing:
                raise HTTPException(status_code = 404, detail = "Country Not Found")
            existing = await self.dao.get_address_by_user_uuid_and_address_type(request_data.user_uuid, request_data.address_type)
            if existing:
                raise ValueError(f"{request_data.address_type} Address for this user already exists")
            calling_code = country_existing.calling_code
            validate_postal_code(calling_code, request_data.postal_code)
            uuid = generate_uuid7()
            result = await self.dao.create_address(request_data, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


            