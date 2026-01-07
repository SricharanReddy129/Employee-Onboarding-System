from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from ..models.models import EmployeeExperience


class EmployeeExperienceDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------------------------------------------
    # GETTERS
    # ----------------------------------------------------

    async def get_experience_by_uuid(self, experience_uuid: str):
        result = await self.db.execute(
            select(EmployeeExperience).where(
                EmployeeExperience.experience_uuid == experience_uuid
            )
        )
        return result.scalar_one_or_none()

    async def get_experience_by_employee_uuid(self, employee_uuid: str):
        result = await self.db.execute(
            select(EmployeeExperience).where(
                EmployeeExperience.employee_uuid == employee_uuid
            )
        )
        return result.scalars().all()

    async def get_all_experience(self):
        result = await self.db.execute(select(EmployeeExperience))
        return result.scalars().all()

    # ----------------------------------------------------
    # CREATE
    # ----------------------------------------------------

    async def create_experience(
        self,
        request_data,
        experience_uuid: str,
        exp_certificate_path: str | None,
        payslip_path: str | None,
        internship_certificate_path: str | None,
        contract_aggrement_path: str | None,
    ):
        new_exp = EmployeeExperience(
            experience_uuid=experience_uuid,
            employee_uuid=request_data.employee_uuid,
            company_name=request_data.company_name,
            role_title=request_data.role_title,
            employment_type=request_data.employment_type.value,
            start_date=request_data.start_date,
            end_date=request_data.end_date,
            is_current=request_data.is_current,
            remarks=request_data.remarks,

            exp_certificate_path=exp_certificate_path,
            payslip_path=payslip_path,
            internship_certificate_path=internship_certificate_path,
            contract_aggrement_path=contract_aggrement_path,

            certificate_status="uploaded",
            uploaded_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(new_exp)
        await self.db.commit()
        await self.db.refresh(new_exp)

        return {
            "experience_uuid": experience_uuid,
            "message": "Experience record created successfully",
        }

    # ----------------------------------------------------
    # UPDATE
    # ----------------------------------------------------

    async def update_experience(self, experience_uuid: str, request_data):
        """
        request_data = ExperienceUpdateRequest
        Update only provided fields.
        """

        experience = await self.get_experience_by_uuid(experience_uuid)
        if not experience:
            return None

        update_fields = {}

        # Safe enum processing
        if request_data.employment_type is not None:
            employment_type = (
                request_data.employment_type.value
                if hasattr(request_data.employment_type, "value")
                else request_data.employment_type
            )

            VALID_EMPLOYMENT_TYPES = ["Full-Time", "Part-Time", "Intern", "Contract", "Freelance"]
            if employment_type not in VALID_EMPLOYMENT_TYPES:
                raise ValueError(f"Invalid employment_type '{employment_type}'")

            update_fields["employment_type"] = employment_type

        # Normal fields
        if request_data.company_name is not None:
            update_fields["company_name"] = request_data.company_name

        if request_data.start_date is not None:
            update_fields["start_date"] = request_data.start_date

        if request_data.end_date is not None:
            update_fields["end_date"] = request_data.end_date

        if request_data.role_title is not None:
            update_fields["role_title"] = request_data.role_title

        if request_data.is_current is not None:
            update_fields["is_current"] = request_data.is_current

        if request_data.remarks is not None:
            update_fields["remarks"] = request_data.remarks

        # Apply update
        for field, value in update_fields.items():
            setattr(experience, field, value)

        experience.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(experience)

        return experience

    # ----------------------------------------------------
    # DELETE
    # ----------------------------------------------------

    async def delete_experience(self, experience_uuid: str):
        experience = await self.get_experience_by_uuid(experience_uuid)
        if not experience:
            return None

        await self.db.delete(experience)
        await self.db.commit()

        return experience

    # ----------------------------------------------------
    # CERTIFICATE PATH UPDATE
    # ----------------------------------------------------

    async def update_experience_certificate(self, experience_uuid: str, file_path: str):

        experience = await self.get_experience_by_uuid(experience_uuid)
        if not experience:
            return None

        experience.exp_certificate_path = file_path
        experience.certificate_status = "uploaded"
        experience.uploaded_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(experience)

        return experience
    
    #----------------------------------------------------
    # DELETE CERTIFICATE PATH
    #----------------------------------------------------
    async def delete_experience_certificate(self, experience_uuid: str):
        experience = await self.get_experience_by_uuid(experience_uuid)
        if not experience:
            return None

        experience.exp_certificate_path = None
        experience.certificate_status = "pending"
        experience.uploaded_at = None
        await self.db.commit()
        await self.db.refresh(experience)
        return experience

