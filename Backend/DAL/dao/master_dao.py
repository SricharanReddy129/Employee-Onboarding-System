# Backend/DAL/dao/master_dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import Countries
from ...API_Layer.interfaces.master_interfaces import CreateCountryRequest

class MasterDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management
    
    async def get_country_by_code(self, code : str):
        result = await self.db.execute(
            select(Countries).where(Countries.calling_code == code)
        )

        return result.scalar_one_or_none()
    async def create_country(self, uuid: str,request_data: CreateCountryRequest):
        new_country = Countries(
            country_uuid = uuid,
            country_name = request_data.country_name,
            calling_code = request_data.calling_code
        )
        self.db.add(new_country)
        await self.db.commit()
        await self.db.refresh(new_country)
        return new_country