from pydantic import BaseModel
from typing import List

# Import existing interfaces (DO NOT DUPLICATE)
from .employee_details_interfaces import (
    PersonalDetailsRequest,
    CreateAddressRequest,
)

from .education_interfaces import EmployeEduDocDetails
from .employee_experience_interfaces import ExperienceCreateRequest


class IdentityDocumentSubmit(BaseModel):
    mapping_uuid: str
    file_path: str


class HrOnboardingSubmitRequest(BaseModel):
    user_uuid: str

    # # Personal
    # personal_details: PersonalDetailsRequest

    # # Address (current + permanent)
    # addresses: List[CreateAddressRequest]

    # # Education
    # education_details: List[EmployeEduDocDetails]

    # # Experience
    # experience_details: List[ExperienceCreateRequest]

    # # Identity proofs
    # identity_documents: List[IdentityDocumentSubmit]
