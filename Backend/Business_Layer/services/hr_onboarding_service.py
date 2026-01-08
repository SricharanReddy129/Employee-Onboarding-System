from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO
from ...Business_Layer.utils import send_hr_onboarding_submitted_email,send_candidate_onboarding_submitted_email

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
    
    from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO


class HrOnboardingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = HrOnboardingDAO(db)

    # =================================================
    # HR GET – FULL ONBOARDING DETAILS
    # =================================================
    async def get_full_onboarding_details(
        self, user_uuid: str, current_user_id: int
    ):
        offer = await self.dao.get_offer_details_by_current_user_id(
            user_uuid, current_user_id
        )
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
            ),
        }

    def _build_completion(self, personal, addresses, identity, education, experience):
        return {
            "personal_details": bool(personal),
            "address": len(addresses) > 0,
            "identity_documents": len(identity) > 0,
            "education_documents": len(education) > 0,
            "experience": len(experience) > 0,
        }

    # =================================================
    # FINAL SUBMIT – STORE ALL DETAILS (CANDIDATE)
    # =================================================
    async def final_submit_onboarding(self, payload):
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

