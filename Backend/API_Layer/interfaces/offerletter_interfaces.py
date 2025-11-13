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

class BulkOfferCreateResponse(BaseModel):
    total_rows: int
    processed_rows: int
    successful_count: int
    failed_count: int
    successful_offers: list[dict]
    failed_offers: list[dict]
    skipped_rows: int


class OfferLetterDetailsResponse(BaseModel):
    first_name: str
    last_name: str
    mail: EmailStr
    country_code: str
    contact_number: str
    designation: str
    package: str
    currency : str
    created_by: int
    status : str

    class Config:
        orm_mode = True