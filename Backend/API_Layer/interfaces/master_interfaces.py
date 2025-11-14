from pydantic import BaseModel


class CreateCountryResponse(BaseModel):
    message: str
    country_uuid: str
class CountryDetails(BaseModel):
    country_code: str
    country_name: str
    is_active: bool

    class Config:
        orm_mode = True

## EDUCATION LEVEL ##
class CreateEducLevelResponse(BaseModel):
    education_uuid: str
    message: str
class CreateEducLevelRequest(BaseModel):
    education_name: str
    description: str