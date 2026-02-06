from datetime import date
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.master_dao import CountryDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.dao.employee_upload_dao import EmployeeUploadDAO
from ...DAL.dao.identity_dao import IdentityDAO
from ..utils.validation_utils import validate_date_of_birth, validate_blood_group
from ..utils.uuid_generator import generate_uuid7
from ..utils.postal_code_validator import validate_postal_code
from ...DAL.utils.storage_utils import S3StorageService
class EmployeeUploadService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeUploadDAO(self.db)
        self.countrydao = CountryDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
        self.identitydao = IdentityDAO(self.db)
        
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
    async def create_address(self, request_data):
     try:
        # check user exists
        existing_user = await self.offerdao.get_offer_by_uuid(request_data.user_uuid)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User Not Found")

        # check country exists
        country_existing = await self.countrydao.get_country_by_uuid(request_data.country_uuid)
        if not country_existing:
            raise HTTPException(status_code=404, detail="Country Not Found")

        # validate postal code
        calling_code = country_existing.calling_code
        validate_postal_code(calling_code, request_data.postal_code)

        # check if address already exists for this user + type
        existing = await self.dao.get_address_by_user_uuid_and_address_type(
            request_data.user_uuid,
            request_data.address_type
        )

        # 🟢 FIRST TIME → INSERT
        if not existing:
            uuid = generate_uuid7()
            return await self.dao.create_address(request_data, uuid)

        # 🔵 ALREADY EXISTS → UPDATE SAME ROW
        existing.address_line1 = request_data.address_line1
        existing.address_line2 = request_data.address_line2
        existing.city = request_data.city
        existing.district_or_ward = request_data.district_or_ward
        existing.state_or_region = request_data.state_or_region
        existing.country_uuid = request_data.country_uuid
        existing.postal_code = request_data.postal_code

        await self.db.commit()
        await self.db.refresh(existing)

        return existing

     except HTTPException as he:
        raise he
     except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        

    async def update_address(self, uuid, request_data):
        try:
            existing = await self.dao.get_address_by_address_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Address Not Found")
            existing_user = await self.offerdao.get_offer_by_uuid(request_data.user_uuid)
            if not existing_user:
                raise HTTPException(status_code = 404, detail = "User Not Found")
            country_existing = await self.countrydao.get_country_by_uuid(request_data.country_uuid)
            if not country_existing:
                raise HTTPException(status_code = 404, detail = "Country Not Found")
            
            calling_code = country_existing.calling_code
            validate_postal_code(calling_code, request_data.postal_code)
            result = await self.dao.update_address(uuid, request_data)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        



    async def create_employee_identity(self, mapping_uuid, user_uuid,identity_file_number, expiry_date, file):
        try:
            existing = await self.identitydao.get_country_identity_mapping_by_uuid(mapping_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Mapping Not Found")

            # checking offer letter employee exists or not
            existing = await self.dao.get_employee_identity_by_user_uuid_and_mapping_uuid(user_uuid, mapping_uuid)
            if existing:
                raise HTTPException(status_code=404, detail="Employee identity mapping Already Found")
            
           

            # checking identity already exists for employee
            
            blob_service = S3StorageService()
            folder = "identity_documents"
            file_path = await blob_service.upload_file(file, folder, original_filename=file.filename, employee_uuid=user_uuid)
            uuid = generate_uuid7()
            result = await self.dao.create_employee_identity(mapping_uuid, user_uuid,identity_file_number, expiry_date, file_path, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_employee_identity(
        self,
        identity_uuid: str,
        mapping_uuid: str,
        user_uuid: str,
        identity_file_number: str,
        expiry_date: Optional[date],
        file: Optional[UploadFile],
    ):
        # 1. Fetch existing record
        existing = await self.repo.get_identity_by_uuid(identity_uuid)
        if not existing:
            raise HTTPException(status_code=404, detail="Identity not found")

        # 2. If file is re-uploaded → replace it
        file_path = existing.file_path
        if file:
            # delete old file (if required)
            await self.file_manager.delete(existing.file_path)

            # save new file
            file_path = await self.file_manager.save(file)

        # 3. Update DB
        return await self.repo.update_identity(
            identity_uuid=identity_uuid,
            mapping_uuid=mapping_uuid,
            user_uuid=user_uuid,
            identity_file_number=identity_file_number,
            expiry_date=expiry_date,
            file_path=file_path,
        )
 