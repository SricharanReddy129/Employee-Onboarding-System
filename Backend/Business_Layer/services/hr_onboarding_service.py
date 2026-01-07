from fastapi import HTTPException
from Backend.DAL.utils.storage_utils import S3StorageService
from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO
import re
class HrOnboardingService:
    def __init__(self, db):
        self.dao = HrOnboardingDAO(db)

    async def get_full_onboarding_details(self, user_uuid: str, current_user_id: int):
        offer = await self.dao.get_offer_details_by_current_user_id(user_uuid, current_user_id)
        if not offer:
            return None

        personal = await self.dao.get_personal_details(user_uuid)
        addresses = await self.dao.get_addresses(user_uuid)
        identity_docs = await self.dao.get_identity_documents(user_uuid)
        education_docs = await self.dao.get_education_documents(user_uuid)
        experience = await self.dao.get_experience(user_uuid)
        approval = await self.dao.get_approval_details(user_uuid)

        return {
            "user": offer,
            "personal_details": personal,
            "addresses": addresses,
            "identity_documents": identity_docs,
            "education_documents": education_docs,
            "experience": experience,
            "approval": approval,
            "completion_status": self._build_completion(
                personal, addresses, identity_docs, education_docs, experience
            )
        }

    def _build_completion(self, personal, addresses, identity, education, experience):
        return {
            "personal_details": bool(personal),
            "address": len(addresses) > 0,
            "identity_documents": len(identity) > 0,
            "education_documents": len(education) > 0,
            "experience": len(experience) > 0
        }
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