from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime


from Backend.API_Layer.interfaces.employee_experience_interfaces import  EmploymentType, ExperienceCreateRequest, ExperienceCreateResponse, ExperienceUpdate 
from Backend.Business_Layer.utils.experience_document_rules import EMPLOYMENT_DOCUMENT_RULES

from ...DAL.dao.employee_experience_dao import EmployeeExperienceDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.utils.storage_utils import S3StorageService, get_storage_service
from ..utils.uuid_generator import generate_uuid7



class EmployeeExperienceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeExperienceDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
        self.storage = get_storage_service()
        

    # ------------------ CREATE EXPERIENCE ------------------

    async def create_experience(
        self,
        request_data: ExperienceCreateRequest,
        doc_types: list[str],
        files: list[UploadFile],
    ):
        # 1️⃣ Validate required docs
        rules = EMPLOYMENT_DOCUMENT_RULES[request_data.employment_type.value]
        if len(doc_types) == 1 and "," in doc_types[0]:
            doc_types = [d.strip() for d in doc_types[0].split(",")]


        missing = set(rules) - set(doc_types)
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required documents: {list(missing)}",
            )

        if len(doc_types) != len(files):
            raise HTTPException(
                status_code=400,
                detail="Each document must have a matching file",
            )

        # 2️⃣ Upload files to S3 (type-based folders)
        paths = {
            "exp_certificate_path": None,
            "payslip_path": None,
            "internship_certificate_path": None,
            "contract_aggrement_path": None,
        }

        for file, doc_type in zip(files, doc_types):
            folder = f"experience_documents/{doc_type}"
            file_path = await self.storage.upload_file(file, folder, original_filename=file.filename, employee_uuid=request_data.employee_uuid)
            print("service", file_path)
            paths[doc_type] = file_path

        # 3️⃣ Create DB record
        experience_uuid = generate_uuid7()

        return await self.dao.create_experience(
            request_data=request_data,
            experience_uuid=experience_uuid,
            exp_certificate_path=paths["exp_certificate_path"],
            payslip_path=paths["payslip_path"],
            internship_certificate_path=paths["internship_certificate_path"],
            contract_aggrement_path=paths["contract_aggrement_path"],
        )

                     

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
    async def update_experience_with_files(
        self,
        experience_uuid: str,
        company_name: str,
        role_title: str | None,
        employment_type: EmploymentType,
        start_date: date,
        end_date: date | None,
        is_current: int,
        remarks: str | None,
        doc_types: list[str],
        files: list[UploadFile] | None,
    ):
        experience = await self.dao.get_experience_by_uuid(experience_uuid)

        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        # 🔹 Validate docs based on employment type
        rules = EMPLOYMENT_DOCUMENT_RULES[employment_type.value]

        if doc_types and len(doc_types) == 1 and "," in doc_types[0]:
            doc_types = [d.strip() for d in doc_types[0].split(",")]

        if files and len(doc_types) != len(files):
            raise HTTPException(400, "Each document must match a file")

        # 🔹 Preserve old paths
        paths = {
            "exp_certificate_path": experience.exp_certificate_path,
            "payslip_path": experience.payslip_path,
            "internship_certificate_path": experience.internship_certificate_path,
            "contract_aggrement_path": experience.contract_aggrement_path,
        }

        # 🔹 Upload new files if provided
        if files and doc_types:
            for file, doc_type in zip(files, doc_types):

                if doc_type not in paths:
                    raise HTTPException(400, f"Invalid doc type: {doc_type}")

                folder = f"experience_documents/{doc_type}"

                file_path = await self.storage.upload_file(
                    file,
                    folder,
                    original_filename=file.filename,
                    employee_uuid=experience.employee_uuid,
                )

                paths[doc_type] = file_path

        # 🔹 Update DB fields
        return await self.dao.update_experience_full(
            experience,
            company_name,
            role_title,
            employment_type,
            start_date,
            end_date,
            is_current,
            remarks,
            paths,
        )

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