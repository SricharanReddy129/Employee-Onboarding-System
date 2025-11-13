# Backend/api/interfaces/offerletter_interfaces.py

from pydantic import BaseModel, EmailStr

class OfferCreateRequest(BaseModel):
    first_name: str
    last_name: str
    mail: EmailStr
    country_code: str
    contact_number: str
    designation: str
    package: str
    currency : str

class OfferCreateResponse(BaseModel):
    message: str
    offer_id: str

class OfferLetterDetails(BaseModel):
    first_name: str
    last_name: str
    mail: EmailStr
    country_code: str
    contact_number: str
    designation: str
    package: str
    currency : str
    created_by: str
    status : str