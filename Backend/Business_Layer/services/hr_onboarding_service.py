from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO
# from ...Business_Layer.utils import send_hr_onboarding_submitted_email,send_candidate_onboarding_submitted_email
from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO
from fastapi import HTTPException
from Backend.DAL.utils.storage_utils import S3StorageService
from Backend.DAL.dao.offerletter_dao import OfferLetterDAO
import re
import asyncio
import time
# from fastapi_cache.decorator import cache
class HrOnboardingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = HrOnboardingDAO(db)
        self.offer_dao = OfferLetterDAO(db)

    async def get_full_onboarding_details(self, user_uuid: str, current_user_id: int):
        return await self.dao.get_full_onboarding_details(
            user_uuid, current_user_id
        )

    # =================================================
    # FINAL SUBMIT – STORE ALL DETAILS (CANDIDATE)
    # =================================================
    async def final_submit_onboarding(self, payload, current_user_id: int):
        """
        This method is called by:
        POST /hr/onboarding/submit

        - Stores ALL onboarding details
        - Uses ONE DB transaction
        - Rolls back if ANY step fails
        """

        async with self.db.begin():  # 🔥 ONE TRANSACTION

            # -------------------------
            # 1️⃣ PERSONAL DETAILS
            # -------------------------
            await self.dao.create_personal_details(
                payload.personal_details.dict()
            )

            # -------------------------
            # 2️⃣ ADDRESSES
            # -------------------------
            for address in payload.addresses:
                await self.dao.create_address(address.dict())

            # -------------------------
            # 3️⃣ IDENTITY DOCUMENTS
            # -------------------------
            for doc in payload.identity_documents:
                await self.dao.create_identity_document(
                    user_uuid=payload.user_uuid,
                    mapping_uuid=doc.mapping_uuid,
                    file_path=doc.file_path,
                )

            # -------------------------
            # 4️⃣ EDUCATION DOCUMENTS
            # -------------------------
            for edu in payload.education_details:
                await self.dao.create_education_document(edu.dict())

            # -------------------------
            # 5️⃣ EXPERIENCE DETAILS
            # -------------------------
            for exp in payload.experience_details:
                await self.dao.create_experience(exp.dict())

            await self.offer_dao.update_offerletter_status(
                user_uuid=payload.user_uuid, status="Submitted", current_user_id=current_user_id
            )

    async def view_onboarding_documents(self, file_path: str):
        try:
            print("File path in service:", file_path)
            pattern = r"^s3://[^/]+/(.+?/[0-9a-fA-F-]{36})"
            match = re.search(pattern, file_path)

            if not match:
                raise ValueError("Invalid S3 file path format")
            match = re.search(pattern, file_path).group(1)
            names = match.split('/')
            print("Names:", names)
            if len(names) == 2:
                print("Entering identity and education document check")
                table_name = names[0]
                existing  = await self.dao.identity_and_education_document_exists(table_name, file_path)
                if not existing:
                    print("Document not found in identity and education check")
                    raise HTTPException(status_code=404, detail="Document Not Found")
            elif len(names) == 3:
                print(names)
                table_name = names[0]
                col_name = names[1]
                existing = await self.dao.experience_document_exists(table_name, col_name, file_path)
                if not existing:    
                    raise HTTPException(status_code=404, detail="Document Not Found")
            else:
                raise ValueError("Invalid file path format")
            print("hello")
            blob_service = S3StorageService()
            document_url = await blob_service.get_presigned_url(file_path)
            return document_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =================================================
    # HR VERIFY / REJECT PROFILE
    # =================================================

    async def update_verification_status(
        self,
        user_uuid: str,
        status: str,
        current_user_id: int
    ):
        """
        status: VERIFIED | REJECTED
        """

        if status.upper() not in ["VERIFIED", "REJECTED"]:
            raise HTTPException(status_code=400, detail="Invalid verification status")

        updated = await self.offer_dao.update_offerletter_status(
            user_uuid=user_uuid,new_status=status,current_user_id=current_user_id
            )
        if not updated:
            raise HTTPException(status_code=404, detail="Offer letter not found for the given user UUID")
