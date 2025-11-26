from enum import Enum
from pydantic import BaseModel
from datetime import date, datetime
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"

class PersonalDetailsRequest(BaseModel):
    user_uuid: str
    date_of_birth: str
    gender: Gender
    marital_status: MaritalStatus
    blood_group: str
    nationality_country_uuid: str
    residence_country_uuid: str

class PersonalDetailsResponse(BaseModel):
    personal_uuid: str
    message: str
class PersonalDetails(BaseModel):
    personal_uuid: str
    user_uuid: str
    date_of_birth: date     # <-- accepts datetime.date automatically
    gender: str
    marital_status: str
    blood_group: str
    nationality_country_uuid: str
    residence_country_uuid: str
    created_at: datetime     # <-- accepts datetime.datetime
class UpdatePersonalRequest(BaseModel):
    date_of_birth: str
    gender: Gender
    marital_status: MaritalStatus
    blood_group: str
    nationality_country_uuid: str
    residence_country_uuid: str