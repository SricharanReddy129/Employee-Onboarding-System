from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.weekly_dashboard_interface import DashboardResponse
from Backend.Business_Layer.services.weekly_dashboard_service import get_dashboard_data
from Backend.DAL.utils.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def dashboard(
    range: str = Query(..., description="Filter range like THIS_WEEK"),
    db: AsyncSession = Depends(get_db)
):
    return await get_dashboard_data(db, range)