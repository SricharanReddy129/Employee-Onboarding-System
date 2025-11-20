from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from ...Business_Layer.services.education_service import EducationDocService
from ...DAL.utils.dependencies import get_db
from ...DAL.utils.storage_utils import S3StorageService
from ...API_Layer.interfaces.education_interfaces import (CreateEducDocRequest, EducDocResponse, EmployeEduDoc,DeleteEmpEducResponse,
                                                          EducDocDetails, UploadFileResponse, EmployeEduDocDetails)

router = APIRouter()

@router.post("/create_education_document", response_model=EducDocResponse)
async def create_education_document(request_data: CreateEducDocRequest, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.create_education_document(request_data)
        return EducDocResponse(
            education_document_uuid =result.education_document_uuid,
            message="Education Document Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/education-document", response_model=list[EducDocDetails])
async def get_all_education_documents(db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_all_education_documents()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/education-document/{uuid}", response_model = CreateEducDocRequest)
async def get_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_education_document_by_uuid(uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/education-document/{uuid}", response_model = EducDocResponse)
async def update_education_document(uuid: str, request_data: CreateEducDocRequest, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.update_education_document(uuid, request_data)
        return EducDocResponse(
            education_document_uuid = result.education_document_uuid,
            message = "Education Document Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/education-document/{uuid}", response_model = EducDocResponse)
async def delete_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.delete_education_document_by_uuid(uuid)
        return EducDocResponse(
            education_document_uuid = result.education_document_uuid,
            message = "Education Document Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Employee Education Documents ##
    
# creating employee eductaion documents and related details
@router.post("/employee-education-document", response_model=UploadFileResponse)
async def create_employee_education_document(request_data: str = Form(...), file: UploadFile = File(...),
                                              db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        data = EmployeEduDoc.model_validate_json(request_data)
        result = await education_service.create_employee_education_document(data, file)
        return UploadFileResponse(
            file_path = result,
            message = "Employee Education Document Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# get all employee education documents
@router.get("/employee-education-document", response_model=list[EmployeEduDocDetails])
async def get_all_employee_education_documents(db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_all_employee_education_documents()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get employee education document by uuid
@router.get("/employee-education-document/{uuid}", response_model=EmployeEduDocDetails)
async def get_employee_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_employee_education_document_by_uuid(uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# delete employee education document by uuid
@router.delete("/employee-education-document/{uuid}", response_model=DeleteEmpEducResponse)
async def delete_employee_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.delete_employee_education_document_by_uuid(uuid)
        return DeleteEmpEducResponse(
            document_uuid = uuid,
            file_path = result,
            message = "Successfully Deleted Employee Education Document"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))