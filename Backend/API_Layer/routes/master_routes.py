from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..interfaces.master_interfaces import CreateCountryRequest, CreateCountryResponse
from ...Business_Layer.services.master_services import CountryService
from ...DAL.utils.dependencies import get_db

router = APIRouter()

@router.post("/country", response_model= CreateCountryResponse)
async def create_country(
    request_data : CreateCountryRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        print("country details", request_data)
        country_service = CountryService(db)
        country_id = await country_service.create_country(request_data)
        return CreateCountryResponse(
            message = "Created Country Successfully",
            country_uuid = country_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))