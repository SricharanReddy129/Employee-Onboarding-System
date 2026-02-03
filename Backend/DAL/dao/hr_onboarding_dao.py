from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import aliased
from sqlalchemy import update
from datetime import datetime
import time
import asyncio
from ...DAL.utils.database import AsyncSessionLocal

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
from sqlalchemy.orm import noload

class HrOnboardingDAO:
    def __init__(self, db: AsyncSession):
        self.db = db



        
    # =================================================
    # =============== CREATE METHODS ==================
    # =================================================

    async def create_personal_details(self, data: dict):
        stmt = insert(PersonalDetails).values(**data)
        await self.db.execute(stmt)

    async def create_address(self, data: dict):
        stmt = insert(Addresses).values(**data)
        await self.db.execute(stmt)

    async def create_identity_document(
        self,
        user_uuid: str,
        mapping_uuid: str,
        file_path: str,
        expiry_date=None,
        status="uploaded",
        remarks=None,
    ):
        stmt = insert(EmployeeIdentityDocument).values(
            user_uuid=user_uuid,
            mapping_uuid=mapping_uuid,
            file_path=file_path,
            expiry_date=expiry_date,
            status=status,
            remarks=remarks,
        )
        await self.db.execute(stmt)

    async def create_education_document(self, data: dict):
        stmt = insert(EmployeeEducationDocument).values(**data)
        await self.db.execute(stmt)

    async def create_experience(self, data: dict):
        stmt = insert(EmployeeExperience).values(**data)
        await self.db.execute(stmt)

    async def create_offer_approval_request(
        self,
        user_uuid: str,
        requested_by: int,
        action_taker_id: int,
    ):
        stmt = insert(OfferApprovalRequest).values(
            user_uuid=user_uuid,
            request_by=requested_by,
            action_taker_id=action_taker_id,
        )
        await self.db.execute(stmt)

# -------------------------------------------
    # helper: run query in its own DB connection
    # -------------------------------------------
    async def _fetch(self, stmt):
        async with AsyncSessionLocal() as s:
            res = await s.execute(stmt)
            return res
    # -------------------------------------------------
    # OFFER / BASIC USER DETAILS
    # -------------------------------------------------
    

    async def get_full_onboarding_details(self, user_uuid: str, current_user_id: int):

        TOTAL_START = time.time()

        # ==================================================
        # Q0: OFFER + PERSONAL
        # ==================================================
        t = time.time()
        async with AsyncSessionLocal() as s:
            res = await s.execute(
                select(OfferLetterDetails, PersonalDetails)
                .options(noload("*"))
                .join(
                    PersonalDetails,
                    PersonalDetails.user_uuid == OfferLetterDetails.user_uuid,
                    isouter=True
                )
                .where(
                    OfferLetterDetails.user_uuid == user_uuid,
                    OfferLetterDetails.created_by == current_user_id
                )
            )
            row = res.first()

        print("Q0 offer+personal:", round(time.time() - t, 3), "s")

        if not row:
            return None

        offer_row, personal_row = row

        # ==================================================
        # Q1–Q4: PARALLEL FETCH (SAFE)
        # ==================================================
        t = time.time()

        async def fetch_addresses():
            async with AsyncSessionLocal() as s:
                r = await s.execute(
                    select(Addresses)
                    .options(noload("*"))
                    .where(Addresses.user_uuid == user_uuid)
                )
                return r.scalars().all()

        async def fetch_identity():
            async with AsyncSessionLocal() as s:
                r = await s.execute(
                    select(EmployeeIdentityDocument)
                    .options(noload("*"))
                    .where(EmployeeIdentityDocument.user_uuid == user_uuid)
                )
                return r.scalars().all()

        async def fetch_education():
            async with AsyncSessionLocal() as s:
                r = await s.execute(
                    select(EmployeeEducationDocument)
                    .options(noload("*"))
                    .where(EmployeeEducationDocument.user_uuid == user_uuid)
                )
                return r.scalars().all()

        async def fetch_experience():
            async with AsyncSessionLocal() as s:
                r = await s.execute(
                    select(EmployeeExperience)
                    .options(noload("*"))
                    .where(EmployeeExperience.employee_uuid == user_uuid)
                )
                return r.scalars().all()

        address_rows, identity_rows, education_rows, experience_rows = await asyncio.gather(
            fetch_addresses(),
            fetch_identity(),
            fetch_education(),
            fetch_experience()
        )

        print("Q1–Q4 parallel:", round(time.time() - t, 3), "s")

        # ==================================================
        # Q5: LOOKUPS
        # ==================================================
        t = time.time()
        async with AsyncSessionLocal() as s:

            # -------- countries --------
            country_uuids = set()
            if personal_row:
                country_uuids.add(personal_row.nationality_country_uuid)
                country_uuids.add(personal_row.residence_country_uuid)

            for a in address_rows:
                if a.country_uuid:
                    country_uuids.add(a.country_uuid)

            countries = {}
            if country_uuids:
                r = await s.execute(
                    select(Countries)
                    .options(noload("*"))
                    .where(Countries.country_uuid.in_(country_uuids))
                )
                countries = {c.country_uuid: c.country_name for c in r.scalars().all()}

            # -------- identity mapping --------
            identity_map = {}
            identity_ids = [i.mapping_uuid for i in identity_rows if i.mapping_uuid]

            if identity_ids:
                r = await s.execute(
                    select(CountryIdentityMapping, IdentityType, Countries)
                    .options(noload("*"))
                    .join(
                        IdentityType,
                        IdentityType.identity_type_uuid == CountryIdentityMapping.identity_type_uuid
                    )
                    .join(
                        Countries,
                        Countries.country_uuid == CountryIdentityMapping.country_uuid
                    )
                    .where(CountryIdentityMapping.mapping_uuid.in_(identity_ids))
                )
                for m, it, c in r.all():
                    identity_map[m.mapping_uuid] = {
                        "identity_type": it.identity_type_name,
                        "country": c.country_name
                    }

            # -------- education mapping --------
            edu_map = {}
            edu_ids = [e.mapping_uuid for e in education_rows if e.mapping_uuid]

            if edu_ids:
                r = await s.execute(
                    select(
                        CountryEducationDocumentMapping,
                        EducationLevel,
                        EducationDocumentType
                    )
                    .options(noload("*"))
                    .join(
                        EducationLevel,
                        EducationLevel.education_uuid == CountryEducationDocumentMapping.education_uuid
                    )
                    .join(
                        EducationDocumentType,
                        EducationDocumentType.education_document_uuid
                        == CountryEducationDocumentMapping.education_document_uuid
                    )
                    .where(CountryEducationDocumentMapping.mapping_uuid.in_(edu_ids))
                )
                for m, lvl, doc in r.all():
                    edu_map[m.mapping_uuid] = {
                        "education_level": lvl.education_name,
                        "document_name": doc.document_name,
                        "mandatory": bool(m.is_mandatory)
                    }

        print("Q5 lookups:", round(time.time() - t, 3), "s")

        # ==================================================
        # BUILD RESPONSE
        # ==================================================
        t = time.time()

        offer = {
            "user_uuid": offer_row.user_uuid,
            "first_name": offer_row.first_name,
            "last_name": offer_row.last_name,
            "email": offer_row.mail,
            "contact_number": f"+{offer_row.country_code} {offer_row.contact_number}",
            "designation": offer_row.designation,
            "offer_status": offer_row.status,
            "created_at": offer_row.created_at,
            "updated_at": offer_row.updated_at,
        }

        personal = None
        if personal_row:
            personal = {
                "date_of_birth": personal_row.date_of_birth,
                "gender": personal_row.gender,
                "marital_status": personal_row.marital_status,
                "blood_group": personal_row.blood_group,
                "nationality_country_uuid": personal_row.nationality_country_uuid,
                "residence_country_uuid": personal_row.residence_country_uuid,
                "nationality": countries.get(personal_row.nationality_country_uuid),
                "residence": countries.get(personal_row.residence_country_uuid),
            }

        addresses = [
            {
                "address_uuid": a.address_uuid,
                "address_type": a.address_type,
                "address_line1": a.address_line1,
                "address_line2": a.address_line2,
                "city": a.city,
                "district_or_ward": a.district_or_ward,
                "state_or_region": a.state_or_region,
                "postal_code": a.postal_code,
                "country_uuid": a.country_uuid,
                "country": countries.get(a.country_uuid)
            }
            for a in address_rows
        ]

        identity_docs = [
            {
                "document_uuid": d.document_uuid,
                "identity_type": identity_map.get(d.mapping_uuid, {}).get("identity_type"),
                "country": identity_map.get(d.mapping_uuid, {}).get("country"),
                "file_path": d.file_path,
                "expiry_date": d.expiry_date,
                "status": d.status,
                "remarks": d.remarks,
                "uploaded_at": d.uploaded_at,
                "verified_at": d.verified_at,
            }
            for d in identity_rows
        ]

        education_docs = [
            {
                "document_uuid": d.document_uuid,
                "education_level": edu_map.get(d.mapping_uuid, {}).get("education_level"),
                "document_name": edu_map.get(d.mapping_uuid, {}).get("document_name"),
                "mandatory": edu_map.get(d.mapping_uuid, {}).get("mandatory"),
                "institution_name": d.institution_name,
                "specialization": d.specialization,
                "year_of_passing": d.year_of_passing,
                "file_path": d.file_path,
                "status": d.status,
                "remarks": d.remarks,
                "uploaded_at": d.uploaded_at,
                "verified_at": d.verified_at,
            }
            for d in education_rows
        ]

        experience = [
            {
                "experience_uuid": e.experience_uuid,
                "company_name": e.company_name,
                "role_title": e.role_title,
                "employment_type": e.employment_type,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "is_current": bool(e.is_current),
                "certificate_status": e.certificate_status,
                "remarks": e.remarks,
                "uploaded_at": e.uploaded_at,
                "verified_at": e.verified_at,
            }
            for e in experience_rows
        ]

        print("BUILD:", round(time.time() - t, 3), "s")
        print("TOTAL DAO:", round(time.time() - TOTAL_START, 3), "s")

        return {
            "offer": offer,
            "personal_details": personal,
            "addresses": addresses,
            "identity_documents": identity_docs,
            "education_documents": education_docs,
            "experience": experience,
        }

    async def identity_and_education_document_exists(self, table_name, file_path):
        if table_name == "identity_documents":
            print("Checking identity document existence in DAO")
            stmt = select(EmployeeIdentityDocument).where(
                EmployeeIdentityDocument.file_path == file_path
            )
            res = await self.db.execute(stmt)
            document = res.scalar_one_or_none()
            print("Document found:", document)
            return document is not None
        elif table_name == "education_documents":
            stmt = select(EmployeeEducationDocument).where(
                EmployeeEducationDocument.file_path == file_path
            )
            res = await self.db.execute(stmt)
            document = res.scalar_one_or_none()
            return document is not None
        else:
            return False
    
    async def experience_document_exists(self, table_name, col_name, filepath):
        if table_name == "experience_documents":
            stmt = select(EmployeeExperience).where(getattr(EmployeeExperience, col_name) == filepath)
            
            res = await self.db.execute(stmt)
            document = res.scalar_one_or_none()
            return document is not None
        else:
            return False
        

    # =================================================
    # HR VERIFY / REJECT PROFILE
    # =================================================
    async def update_hr_verification_status(
        self,
        user_uuid: str,
        status: str,
        verified_by: int
    ) -> bool:
        """
        Update HR verification status for an employee
        """

        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.user_uuid == user_uuid)
            .values(
                hr_verification_status=status,
                verified_by=verified_by,
                verified_at=datetime.utcnow()
            )
        )

        result = await self.db.execute(stmt)

        return result.rowcount > 0
    
    async def final_submit_onboarding(self, user_uuid):
        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.user_uuid == user_uuid)
            .values(
                status="Submitted"
            )
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
    
    async def get_personal_details_by_uuid(self, user_uuid):
        stmt = select(PersonalDetails.user_uuid).where(PersonalDetails.user_uuid == user_uuid)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_address_details_by_uuid(self, user_uuid):
        stmt = select(Addresses.user_uuid).where(Addresses.user_uuid == user_uuid)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_identity_details_by_uuid(self, user_uuid):
        stmt = select(EmployeeIdentityDocument.user_uuid).where(EmployeeIdentityDocument.user_uuid == user_uuid)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_education_details_by_uuid(self, user_uuid):
        stmt = select(EmployeeEducationDocument.user_uuid).where(EmployeeEducationDocument.user_uuid == user_uuid)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_experience_details_by_uuid(self, user_uuid):
        stmt = select(EmployeeExperience.employee_uuid).where(EmployeeExperience.employee_uuid == user_uuid)
        result = await self.db.execute(stmt)
        return result.scalars().first()