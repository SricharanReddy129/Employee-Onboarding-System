from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.education_dao import EducationDocDAO
from ...DAL.dao.master_dao import CountryDAO, EducationDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.utils.storage_utils import S3StorageService
from ..utils.validation_utils import validate_alphabets_only, validate_document_name, validate_numeric_value
from ..utils.uuid_generator import generate_uuid7
import time
class EducationDocService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EducationDocDAO(self.db)
        self.educationdao = EducationDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
        self.countrydao = CountryDAO(self.db)
    async def create_education_document(self, request_data):
        try:
            document_name = validate_alphabets_only(request_data.document_name)
            existing = await self.dao.get_document_by_name(document_name)
            if existing:
                raise HTTPException(status_code=404, detail="Document Already Exists")
            uuid = generate_uuid7()
            result = await self.dao.create_education_document(request_data, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_all_education_documents(self):
        
        try:
            result = await self.dao.get_all_education_documents()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_education_document_by_uuid(self, uuid):
        try:
            result = await self.dao.get_education_document_by_uuid(uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_education_document(self, uuid, request_data):
        try:
            existing = await self.dao.get_education_document_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Document Not Found")
            if request_data.document_name:
                document_name = validate_document_name(request_data.document_name)

                existing = await self.dao.get_document_by_name_and_uuid(document_name, uuid)
                if existing:
                    raise HTTPException(
                        status_code=409,
                        detail="Document name already exists"
                    )

            result = await self.dao.update_education_document(uuid, request_data)

            return result

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        
    async def delete_education_document_by_uuid(self, uuid):
        try:
            existing = await self.dao.get_education_document_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Document Not Found")
            return await self.dao.delete_education_document_by_uuid(uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
## Employee Education Documents ##
    async def create_employee_education_document(self, request_data, file):
        try:
            # checking mapping exists or not
            print("in service method")
            existing = await self.educationdao.get_education_country_mapping_by_uuid(request_data["mapping_uuid"])
            print("existing", existing)
            if not existing:
                raise HTTPException(status_code=404, detail="Mapping Not Found")
            
            # checking offer letter employee exists or not
            existing = await self.offerdao.get_offer_by_uuid(request_data["user_uuid"])
            if not existing:
                raise HTTPException(status_code=404, detail="Employee Not Found")
            validate_alphabets_only(request_data["institution_name"])
            validate_alphabets_only(request_data["specialization"])
            validate_numeric_value(str(request_data["percentage_cgpa"]))
            uuid = generate_uuid7()
            blob_upload_service = S3StorageService()
            folder = "education_documents"
            print("User uuid", request_data["user_uuid"])
            file_path = await blob_upload_service.upload_file(file, folder, original_filename=file.filename, employee_uuid=request_data["user_uuid"])
            result = await self.dao.create_employee_education_document(request_data, uuid, file_path)
            return file_path
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def update_employee_education_document(self, document_uuid, request_data, file):
        # 1️⃣ check document exists
        existing = await self.dao.get_document_by_uuid(document_uuid)
        if not existing:
            raise HTTPException(status_code=404, detail="Education document not found")

        # 2️⃣ validate
        validate_alphabets_only(request_data["institution_name"])
        validate_alphabets_only(request_data["specialization"])
        validate_numeric_value(str(request_data["percentage_cgpa"]))

        # 3️⃣ upload file only if provided
        file_path = existing.file_path
        if file:
            blob_upload_service = S3StorageService()
            folder = "education_documents"
            file_path = await blob_upload_service.upload_file(
                file,
                folder,
                original_filename=file.filename,
                employee_uuid=existing.user_uuid
            )

        # 4️⃣ update DB
        await self.dao.update_employee_education_document(
            document_uuid, request_data, file_path
        )

        return file_path
    
    # get all employee educational documents #
    async def get_all_employee_education_documents(self):
        try:
            print("entering service")
            result = await self.dao.get_all_employee_education_documents()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_employee_education_document_by_uuid(self, uuid):
        try:
            result = await self.dao.get_employee_education_document_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=200, detail="No Employee Education Document Found for this Employee")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def delete_employee_education_document_by_uuid(self, uuid):
        try:
            existing = await self.dao.get_employee_education_document_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Document Not Found")
            blob_upload_service = S3StorageService()
            await blob_upload_service.delete_file(existing.file_path)
            result = await self.dao.delete_employee_education_document_by_uuid(uuid)
            return existing.file_path
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    

    async def get_education_identity_mappings_by_country_uuid(self, country_uuid):
        t1 = time.perf_counter()
        existing = await self.countrydao.get_country_by_uuid(country_uuid)
        print("⏱ get_country_by_uuid:", time.perf_counter() - t1)

        if not existing:
            raise HTTPException(status_code=404, detail="Country Not Found")

        t2 = time.perf_counter()
        result = await self.dao.get_education_identity_mappings_by_country_uuid(country_uuid)
        print("⏱ mapping DAO:", time.perf_counter() - t2)

        return result

            
        