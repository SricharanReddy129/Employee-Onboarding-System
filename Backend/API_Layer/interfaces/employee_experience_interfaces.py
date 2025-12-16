# interfaces/employee_experience_interfaces.py

from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
import re


# ---------------------------------------------------------
# ENUMS (MATCH DB ENUMS EXACTLY)
# ---------------------------------------------------------

class EmploymentType(str, Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    INTERN = "Intern"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"


class CertificateStatus(str, Enum):
    UPLOADED = "uploaded"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


# ---------------------------------------------------------
# BASE VALIDATION UTILS
# ---------------------------------------------------------

def clean_text(value: Optional[str]) -> Optional[str]:
    """
    Normalize user input:
    - Strip leading/trailing spaces
    - Replace newlines & tabs safely
    NOTE: JSON must already be valid before this runs
    """
    if value is None:
        return value
    return (
        value
        .replace("\n", " ")
        .replace("\t", " ")
        .strip()
    )


# ---------------------------------------------------------
# REQUEST MODELS (CREATE / UPDATE)
# ---------------------------------------------------------


class ExperienceCreateRequest(BaseModel):
    employee_uuid: str
    company_name: str 
    start_date: date
    end_date: Optional[date] = None
    role_title: Optional[str] = Field(None, max_length=100)
    employment_type: EmploymentType
    is_current: Optional[int] = Field(0, ge=0, le=1)
    remarks: Optional[str] = Field(None, max_length=255)

    # -------- VALIDATORS --------

    @validator("company_name")
    def validate_company_name(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9\s\&\-\.\,']+$", v):
            raise ValueError("Company name contains invalid characters")
        return v.strip()

    @validator("remarks", "role_title", pre=True)
    def sanitize_text_fields(cls, v):
        return clean_text(v)


class ExperienceUpdateRequest(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=150)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    role_title: Optional[str] = Field(None, max_length=100)
    employment_type: Optional[EmploymentType] = None
    is_current: Optional[int] = Field(None, ge=0, le=1)
    remarks: Optional[str] = Field(None, max_length=255)

    # -------- VALIDATORS --------

    @validator("company_name")
    def validate_company_name(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[A-Za-z0-9\s\&\-\.\,']+$", v):
            raise ValueError("Company name contains invalid characters")
        return v.strip() if v else v

    @validator("remarks", "role_title", pre=True)
    def sanitize_text_fields(cls, v):
        return clean_text(v)


# ---------------------------------------------------------
# RESPONSE MODELS
# ---------------------------------------------------------

class ExperienceResponse(BaseModel):
    experience_uuid: str
    employee_uuid: str
    company_name: str
    start_date: date
    end_date: Optional[date]
    role_title: Optional[str]
    employment_type: Optional[str]
    is_current: Optional[int]
    exp_certificate_path: Optional[str]
    certificate_status: Optional[str]
    uploaded_at: Optional[datetime]
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    remarks: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]




class GenericMessageResponse(BaseModel):
    experience_uuid: str
    message: str


class ExperienceCreateResponse(BaseModel):
    experience_uuid: str
    message: str
