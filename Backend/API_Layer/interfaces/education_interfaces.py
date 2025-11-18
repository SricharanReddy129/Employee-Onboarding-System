from pydantic import BaseModel

# Education Documents #
class CreateEducDocRequest(BaseModel):
    document_name: str
    description: str

class EducDocResponse(BaseModel):
    education_document_uuid: str
    message: str

class EducDocDetails(BaseModel):
    education_document_uuid: str
    document_name: str
    description: str
    
