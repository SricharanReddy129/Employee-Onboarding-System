from pydantic import BaseModel
from enum import Enum

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

class UploadFileResponse(BaseModel):
    file_path: str
    message: str

class EmployeEduDoc(BaseModel):
    mapping_uuid: str
    user_uuid: str
    institution_name: str 
    specialization: str
    year_of_passing: int

class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    verified = "verified"
    rejected = "rejected"

class EmployeEduDocDetails(BaseModel):
    document_uuid: str
    mapping_uuid: str
    user_uuid: str
    institution_name: str 
    specialization: str
    year_of_passing: int
    file_path: str
    status: DocumentStatus

class DeleteEmpEducResponse(BaseModel):
    document_uuid: str
    file_path:str
    message: str


class CountryEducationMappingResponse(BaseModel):
    mapping_uuid: str
    education_name: str
    document_name: str
    is_mandatory: bool

