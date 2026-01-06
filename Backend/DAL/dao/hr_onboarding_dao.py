from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...DAL.models.models import (
    OfferLetterDetails,
    PersonalDetails,
    Countries,
    Addresses,
    EmployeeIdentityDocument,
    CountryIdentityMapping,
    IdentityType,
    EmployeeEducationDocument,
    CountryEducationDocumentMapping,
    EducationLevel,
    EducationDocumentType,
    EmployeeExperience,
    OfferApprovalRequest,
    OfferApprovalAction,
)


class HrOnboardingDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------
    # OFFER / BASIC USER DETAILS
    # -------------------------------------------------
    async def get_offer_details_by_current_user_id(self, user_uuid: str, current_user_id: int):
        stmt = select(OfferLetterDetails).where(
            OfferLetterDetails.user_uuid == user_uuid
        ).where(
            OfferLetterDetails.created_by == current_user_id
        )
        res = await self.db.execute(stmt)
        offer = res.scalar_one_or_none()

        if not offer:
            return None

        return {
            "user_uuid": offer.user_uuid,
            "first_name": offer.first_name,
            "last_name": offer.last_name,
            "email": offer.mail,
            "contact_number": f"+{offer.country_code} {offer.contact_number}",
            "designation": offer.designation,
            "offer_status": offer.status,
            "created_at": offer.created_at,
            "updated_at": offer.updated_at,
        }

    # -------------------------------------------------
    # PERSONAL DETAILS
    # -------------------------------------------------
    async def get_personal_details(self, user_uuid: str):
        stmt = (
            select(
                PersonalDetails,
                Countries
            )
            .join(
                Countries,
                PersonalDetails.nationality_country_uuid == Countries.country_uuid,
                isouter=True
            )
            .where(PersonalDetails.user_uuid == user_uuid)
        )

        res = await self.db.execute(stmt)
        row = res.first()

        if not row:
            return None

        personal, nationality = row

        return {
            "date_of_birth": personal.date_of_birth,
            "gender": personal.gender,
            "marital_status": personal.marital_status,
            "blood_group": personal.blood_group,
            "nationality": nationality.country_name if nationality else None,
            "nationality_country_uuid": personal.nationality_country_uuid,
            "residence_country_uuid": personal.residence_country_uuid,
        }

    # -------------------------------------------------
    # ADDRESS DETAILS
    # -------------------------------------------------
    async def get_addresses(self, user_uuid: str):
        stmt = (
            select(Addresses, Countries)
            .join(
                Countries,
                Addresses.country_uuid == Countries.country_uuid
            )
            .where(Addresses.user_uuid == user_uuid)
        )

        res = await self.db.execute(stmt)
        rows = res.all()

        return [
            {
                "address_uuid": address.address_uuid,
                "address_type": address.address_type,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "city": address.city,
                "district_or_ward": address.district_or_ward,
                "state_or_region": address.state_or_region,
                "postal_code": address.postal_code,
                "country": country.country_name,
                "country_uuid": country.country_uuid,
            }
            for address, country in rows
        ]

    # -------------------------------------------------
    # IDENTITY DOCUMENTS
    # -------------------------------------------------
    async def get_identity_documents(self, user_uuid: str):
        stmt = (
            select(
                EmployeeIdentityDocument,
                IdentityType,
                Countries
            )
            .join(
                CountryIdentityMapping,
                EmployeeIdentityDocument.mapping_uuid
                == CountryIdentityMapping.mapping_uuid
            )
            .join(
                IdentityType,
                CountryIdentityMapping.identity_type_uuid
                == IdentityType.identity_type_uuid
            )
            .join(
                Countries,
                CountryIdentityMapping.country_uuid
                == Countries.country_uuid
            )
            .where(EmployeeIdentityDocument.user_uuid == user_uuid)
        )

        res = await self.db.execute(stmt)

        return [
            {
                "document_uuid": doc.document_uuid,
                "identity_type": identity.identity_type_name,
                "country": country.country_name,
                "file_path": doc.file_path,
                "expiry_date": doc.expiry_date,
                "status": doc.status,
                "remarks": doc.remarks,
                "uploaded_at": doc.uploaded_at,
                "verified_at": doc.verified_at,
            }
            for doc, identity, country in res.all()
        ]

    # -------------------------------------------------
    # EDUCATION DOCUMENTS
    # -------------------------------------------------
    async def get_education_documents(self, user_uuid: str):
        stmt = (
            select(
                EmployeeEducationDocument,
                EducationLevel,
                EducationDocumentType,
                CountryEducationDocumentMapping
            )
            .join(
                CountryEducationDocumentMapping,
                EmployeeEducationDocument.mapping_uuid
                == CountryEducationDocumentMapping.mapping_uuid
            )
            .join(
                EducationLevel,
                CountryEducationDocumentMapping.education_uuid
                == EducationLevel.education_uuid
            )
            .join(
                EducationDocumentType,
                CountryEducationDocumentMapping.education_document_uuid
                == EducationDocumentType.education_document_uuid
            )
            .where(EmployeeEducationDocument.user_uuid == user_uuid)
        )

        res = await self.db.execute(stmt)

        return [
            {
                "document_uuid": emp.document_uuid,
                "education_level": edu.education_name,
                "document_name": doc.document_name,
                "institution_name": emp.institution_name,
                "specialization": emp.specialization,
                "year_of_passing": emp.year_of_passing,
                "mandatory": bool(mapping.is_mandatory),
                "file_path": emp.file_path,
                "status": emp.status,
                "remarks": emp.remarks,
                "uploaded_at": emp.uploaded_at,
                "verified_at": emp.verified_at,
            }
            for emp, edu, doc, mapping in res.all()
        ]

    # -------------------------------------------------
    # EXPERIENCE DETAILS
    # -------------------------------------------------
    async def get_experience(self, user_uuid: str):
        stmt = select(EmployeeExperience).where(
            EmployeeExperience.employee_uuid == user_uuid
        )

        res = await self.db.execute(stmt)
        experiences = res.scalars().all()

        return [
            {
                "experience_uuid": exp.experience_uuid,
                "company_name": exp.company_name,
                "role_title": exp.role_title,
                "employment_type": exp.employment_type,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "is_current": bool(exp.is_current),
                "certificate_status": exp.certificate_status,
                "remarks": exp.remarks,
                "uploaded_at": exp.uploaded_at,
                "verified_at": exp.verified_at,
            }
            for exp in experiences
        ]

    # -------------------------------------------------
    # OFFER APPROVAL DETAILS
    # -------------------------------------------------
    async def get_approval_details(self, user_uuid: str):
        stmt = (
            select(
                OfferApprovalRequest,
                OfferApprovalAction
            )
            .join(
                OfferApprovalAction,
                OfferApprovalAction.request_id
                == OfferApprovalRequest.id,
                isouter=True
            )
            .where(OfferApprovalRequest.user_uuid == user_uuid)
        )

        res = await self.db.execute(stmt)
        rows = res.all()

        if not rows:
            return None

        request = rows[0][0]

        return {
            "request_id": request.id,
            "requested_by": request.request_by,
            "action_taker_id": request.action_taker_id,
            "request_time": request.request_time,
            "actions": [
                {
                    "action": action.action,
                    "comment": action.comment,
                    "action_time": action.action_time,
                }
                for _, action in rows if action
            ],
        }
