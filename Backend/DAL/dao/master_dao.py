# Backend/DAL/dao/master_dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import Countries


class MasterDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management
    
    async def get_country_by_code(self, code : str):
        result = await self.db.execute(
            select(Countries).where(Countries.calling_code == code)
        )

        return result.scalar_one_or_none()
    async def create_country(self, uuid: str, calling_code: str, country_name: str):
        new_country = Countries(
            country_uuid = uuid,
            country_name = country_name,
            calling_code = calling_code
        )
        self.db.add(new_country)
        await self.db.commit()
        await self.db.refresh(new_country)
        return new_country
    async def get_country_by_uuid(self, country_uuid: str):
        result = await self.db.execute(
            select(Countries).where(Countries.country_uuid == country_uuid)
        )

        return result.scalar_one_or_none()
    async def update_country(self, country_uuid: str, is_active: bool):
        result = await self.db.execute(
            select(Countries).where(Countries.country_uuid == country_uuid)
        )
        
        country = result.scalar_one_or_none()
        if country is None:
            return None
        
        country.is_active = 1 if is_active else 0

        await self.db.commit()
        await self.db.refresh(country)

        return country
   
