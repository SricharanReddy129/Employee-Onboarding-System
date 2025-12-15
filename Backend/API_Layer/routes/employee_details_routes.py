# Backend/API_Layer/routes/employee_details_routes.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from ..interfaces.employee_details_interfaces import (PersonalDetailsRequest, PersonalDetailsResponse, PersonalDetails,
                                                      UpdatePersonalRequest, CreateAddressRequest, CreateAddressResponse,
                                                      AddressDetails, EmployeeIdentityResponse)
from ...Business_Layer.services.employee_details_service import EmployeeDetailsService, AddressService, EmployeeIdentityService
from datetime import date
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
    
## Addresses Routes ##

@router.post("/address", response_model = CreateAddressResponse)
async def create_address(request_data: CreateAddressRequest, db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        result = await address_service.create_address(request_data)
        return CreateAddressResponse(
            address_uuid = result.address_uuid,
            message = "Address Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/address/", response_model = list[AddressDetails])
async def get_all_addresses(db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        result = await address_service.get_all_addresses()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/address/{address_uuid}", response_model = AddressDetails)
async def get_address_by_address_uuid(address_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        result = await address_service.get_address_by_address_uuid(address_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/address/{address_uuid}", response_model = CreateAddressResponse)
async def update_address(address_uuid: str, request_data: CreateAddressRequest, db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        result = await address_service.update_address(address_uuid, request_data)
        return CreateAddressResponse(
            address_uuid = address_uuid,
            message = "Address Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/address/{address_uuid}", response_model=CreateAddressResponse)
async def delete_address(address_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        await address_service.delete_address(address_uuid)
        return CreateAddressResponse(
            address_uuid = address_uuid,
            message = "Address Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Employee Identity Document Routes #
@router.post("/identity", response_model=EmployeeIdentityResponse)
async def create_employee_identity(
    mapping_uuid: str = Form(...),
    user_uuid: str = Form(...),
    expiry_date: Optional[date] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        employee_service = EmployeeIdentityService(db)

        result = await employee_service.create_employee_identity(
            mapping_uuid=mapping_uuid,
            user_uuid=user_uuid,
            expiry_date=expiry_date,
            file=file
        )

        return EmployeeIdentityResponse(
            identity_uuid=result.document_uuid,
            message="Employee Identity Document Created Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    