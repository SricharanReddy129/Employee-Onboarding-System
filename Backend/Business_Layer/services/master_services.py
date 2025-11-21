from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.dao.master_dao import  CountryDAO, EducationDAO, ContactDAO
from ...DAL.dao.education_dao import EducationDocDAO
from ..utils.validation_utils import validate_alphabets_only, validate_country, validate_phone_number
from ..utils.uuid_generator import generate_uuid7
from ...API_Layer.interfaces.master_interfaces import CreateEducLevelRequest, EducLevelDetails


class CountryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = CountryDAO(self.db)
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
    async def get_all_countries(self):
        try:
            result = await self.dao.get_all_countries()
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class EducationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EducationDAO(self.db)
        self.educationdao = EducationDocDAO(self.db)
        self.countrydao = CountryDAO(self.db)
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
    
    async def get_all_education_levels(self):
        try:
            result = await self.dao.get_all_education_levels()
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_education_level_by_uuid(self, uuid: str):
        try:
            result = await self.dao.get_education_level_by_uuid(uuid)
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_education_level(self, request_data: EducLevelDetails, uuid: str):
        try:
            education_name = validate_alphabets_only(request_data.education_name)
            education_name = await self.dao.get_education_level_by_eduname_and_uuid(education_name, uuid)
            if education_name:
                raise HTTPException(status_code=404, detail = "Education Level Already Exist")
            return await self.dao.update_education_level(request_data, uuid)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def delete_education_level(self, uuid: str):
        try:
            result = await self.dao.get_education_level_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=404, detail = "Education Level Not Found")
            return await self.dao.delete_education_level(uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def create_education_country_mapping(self, educ_level_uuid, educ_doc_uuid, country_uuid):
        try:
            existing = await self.dao.get_education_level_by_uuid(educ_level_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Education Level Not Found")
            existing = await self.educationdao.get_education_document_by_uuid(educ_doc_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Education Document Not Found")
            existing = await self.countrydao.get_country_by_uuid(country_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Country Not Found")
            existing = await self.dao.check_education_country_mapping(educ_level_uuid, educ_doc_uuid, country_uuid)
            if existing:
                raise HTTPException(status_code=404, detail="Mapping Already Exists")
            uuid = generate_uuid7()
            result = await self.dao.create_education_country_mapping(educ_level_uuid, educ_doc_uuid, country_uuid, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def delete_education_country_mapping(self, mapping_uuid):
        try:
            result = await self.dao.get_education_country_mapping_by_uuid(mapping_uuid)
            if not result:
                raise HTTPException(status_code=404, detail="Mapping Not Found")
            return await self.dao.delete_education_country_mapping(mapping_uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_all_education_country_mapping(self):
        try:
            result = await self.dao.get_all_education_country_mapping()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class ContactService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = ContactDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
        self.countrydao = CountryDAO(self.db)

    async def create_contact(self, request_data):
        try:
            existing_user = await self.offerdao.get_offer_by_uuid(request_data.user_uuid)
            if not existing_user:
                raise ValueError("User Not Found")
            existing_country = await self.countrydao.get_country_by_uuid(request_data.country_uuid)
            if not existing_country:
                raise ValueError("Country Not Found")
            if existing_country.is_active == False:
                raise ValueError("Country is Inactive")
            
            calling_code = existing_country.calling_code
            validate_phone_number(calling_code, request_data.contact_number, "contact number")
            validate_phone_number(calling_code, request_data.emergency_contact, "emergency contact")
            # checking already exists or not 
            existing = await self.dao.get_contact_by_user_uuid_and_country_uuid(request_data.user_uuid, request_data.country_uuid)
            if existing:
                raise ValueError("Contact with this user_uuid and country_uuid already exists")
            

            uuid = generate_uuid7()
            return await self.dao.create_contact(request_data, uuid)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_all_contacts(self):
        try:
            result = await self.dao.get_all_contacts()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_contact_by_uuid(self, uuid):
        try:
            result = await self.dao.get_contact_by_uuid(uuid)
            if not result:
                raise ValueError("Contact Not Found")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

            
