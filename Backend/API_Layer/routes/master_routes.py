from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..interfaces.master_interfaces import CreateCountryResponse, CountryDetails
from ...Business_Layer.services.master_services import CountryService
from ...DAL.utils.dependencies import get_db

router = APIRouter()

@router.post("/country", response_model= CreateCountryResponse)
async def create_country(
    calling_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        print("country details", calling_code)
        country_service = CountryService(db)
        country_id = await country_service.create_country(calling_code)
        return CreateCountryResponse(
            message = "Created Country Successfully",
            country_uuid = country_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# deactivate country by country uuid
@router.put("/deactivateoractivate/{country_uuid}", response_model= CreateCountryResponse)
async def update_country(
    country_uuid: str,
    is_active: bool,
    db: AsyncSession = Depends(get_db)
):
    try:
        country_service = CountryService(db)
        country = await country_service.update_country(country_uuid, is_active)
        return CreateCountryResponse(
            message=country,
            country_uuid=country_uuid
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get country details by uuid
@router.get("/country/{country_uuid}", response_model=CountryDetails)
async def get_country_uuid(
    country_uuid: str,
    db: AsyncSession = Depends(get_db)):
    try:
        country_service = CountryService(db)
        result = await country_service.get_country_uuid(country_uuid)
        return CountryDetails(
            country_code = result.calling_code,
            country_name = result.country_name,
            is_active = result.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
