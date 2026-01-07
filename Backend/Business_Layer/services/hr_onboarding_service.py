from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO

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
