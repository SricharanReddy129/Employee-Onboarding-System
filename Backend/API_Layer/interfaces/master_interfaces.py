from pydantic import BaseModel

class CreateCountryRequest(BaseModel):
    country_name: str
    calling_code: str
    
    class Config:
        orm_mode = True
class CreateCountryResponse(BaseModel):
    message: str
    country_uuid: str