from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


from Backend.API_Layer.interfaces.employee_experience_interfaces import ExperienceCreateRequest


from ...DAL.dao.employee_experience_dao import EmployeeExperienceDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.utils.storage_utils import S3StorageService, get_storage_service
from ..utils.uuid_generator import generate_uuid7



class EmployeeExperienceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeExperienceDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
        self.storage = S3StorageService
        

    # ------------------ CREATE EXPERIENCE ------------------

    async def create_experience(self, request_data: ExperienceCreateRequest, file):
        # 1️ Check if employee exists
        user_exists = await self.offerdao.get_offer_by_uuid(request_data.employee_uuid)
        if not user_exists:
            raise HTTPException(status_code=404, detail="Employee Not Found")

        # 2️ Validate dates
        start_date = request_data.start_date
        end_date = request_data.end_date
        if start_date and end_date and end_date < start_date:
            raise HTTPException(
                status_code=400,
                detail="end_date cannot be earlier than start_date"
            )

        # 3️ Generate UUID
        experience_uuid = generate_uuid7()
        blob_upload_service = S3StorageService()
        folder = "experience_documents"
        file_path = await blob_upload_service.upload_file(file, folder)

        # 4️ Call DAO to create record
        result = await self.dao.create_experience(request_data, experience_uuid, file_path)
        return result
                     

    # ------------------ GET EXPERIENCE ------------------
    async def get_all_experience(self):
        try:
            print("before dao call")
            result = await self.dao.get_all_experience()
            print("after dao call", result)
            if not result:
                raise HTTPException(status_code=404, detail="No Experience Records Found")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_experience_by_uuid(self, experience_uuid: str):
        result = await self.dao.get_experience_by_uuid(experience_uuid)
        if not result:
            raise HTTPException(status_code=404, detail="Experience details not found")
        return result

    async def get_experience_by_employee_uuid(self, employee_uuid: str):
        result = await self.dao.get_experience_by_employee_uuid(employee_uuid)
        if not result:
            raise HTTPException(status_code=404, detail="No Experience Found for this Employee")
        return result

    # ------------------ UPDATE EXPERIENCE ------------------
    async def update_experience(self, experience_uuid: str, request_data):
        existing = await self.dao.get_experience_by_uuid(experience_uuid)
        if not existing:
            raise HTTPException(status_code=404, detail="Experience Record Not Found")

        user_exists = await self.offerdao.get_offer_by_uuid(existing.employee_uuid)
        if not user_exists:
            raise HTTPException(status_code=404, detail="Employee Not Found")

        start_date = request_data.start_date
        end_date = request_data.end_date
        if start_date and end_date and end_date < start_date:
            raise HTTPException(
                status_code=400,
                detail="end_date cannot be earlier than start_date"
            )

        return await self.dao.update_experience(experience_uuid, request_data)

    # ------------------ DELETE EXPERIENCE ------------------
    async def delete_experience(self, experience_uuid: str):
        existing = await self.dao.get_experience_by_uuid(experience_uuid)
        if not existing:
            raise HTTPException(status_code=404, detail="Experience Not Found")

        if existing.exp_certificate_path:
            try:
                await self.storage.delete_file(existing.exp_certificate_path)
            except Exception:
                pass

        return await self.dao.delete_experience(experience_uuid)

    # ------------------Updated  CERTIFICATE  upload------------------

    async def update_experience_certificate(self, experience_uuid, file):
        existing = await self.dao.get_experience_by_uuid(experience_uuid)
        if not existing:
            raise HTTPException(status_code=404, detail="Experience Not Found")

        print("in service layer entering ", existing.exp_certificate_path)

        storage_service = S3StorageService()

        try:
            # Delete old certificate if exists
            if existing.exp_certificate_path:
                try:
                    await storage_service.delete_file(existing.exp_certificate_path)
                except Exception:
                    pass

            # Upload new certificate
            file_path = await storage_service.upload_file(file, folder="experience_documents")

            # Update DB record safely
            updated_record = await self.dao.update_experience_certificate(experience_uuid, file_path)

            return updated_record

        except Exception as e:
            # Rollback is handled inside DAO or session context
            raise HTTPException(status_code=500, detail=f"Failed to update certificate: {str(e)}")


    # ------------------ DELETE CERTIFICATE ONLY ------------------
    async def delete_certificate(self, experience_uuid: str):
      experience = await self.dao.get_experience_by_uuid(experience_uuid)
      if not experience:
        raise HTTPException(status_code=404, detail="Experience Not Found")

      print("Deleting:", experience.exp_certificate_path)

      storage = get_storage_service()  # ✅ singleton instance

      if experience.exp_certificate_path:
        await storage.delete_file(experience.exp_certificate_path)

      await self.dao.delete_experience_certificate(experience_uuid)

      return {"message": "Certificate deleted successfully"}