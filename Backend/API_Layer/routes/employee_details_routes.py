# Backend/API_Layer/routes/employee_details_routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from ..interfaces.employee_details_interfaces import (PersonalDetailsRequest, PersonalDetailsResponse, PersonalDetails,
                                                      UpdatePersonalRequest,
                                                      )
from ...Business_Layer.services.employee_details_service import EmployeeDetailsService

router = APIRouter()

@router.post("", response_model=PersonalDetailsResponse)
async def create_personal_details(request_data: PersonalDetailsRequest, db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        result = await employee_service.create_personal_details(request_data)
        return PersonalDetailsResponse(
            personal_uuid = result.personal_uuid,
            message = "Personal Details Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("", response_model = list[PersonalDetails])
async def get_all_personal_details(db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        result = await employee_service.get_all_personal_details()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/{personal_uuid}", response_model = PersonalDetails)
async def get_personal_details_by_user_uuid(personal_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        result = await employee_service.get_personal_details_by_user_uuid(personal_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{personal_uuid}", response_model = PersonalDetailsResponse)
async def update_personal_details(personal_uuid: str, request_data: UpdatePersonalRequest, db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        result = await employee_service.update_personal_details(personal_uuid, request_data)
        return PersonalDetailsResponse(
            personal_uuid = result.personal_uuid,
            message = "Personal Details Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{personal_uuid}", response_model = PersonalDetailsResponse)
async def delete_personal_details(personal_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        await employee_service.delete_personal_details(personal_uuid)
        return PersonalDetailsResponse(
            personal_uuid = personal_uuid,
            message = "Personal Details Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))