from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.identity_dao import IdentityDAO
from ..utils.uuid_generator import generate_uuid7

class IdentityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = IdentityDAO(db)
    
    async def get_all_identity_types(self):
        try:
            result = await self.dao.get_all_identity_types()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_identity_type_by_uuid(self, uuid):
        try:
            result = await self.dao.get_identity_type_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=200, detail="No Identity Type Found for this employee")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def create_identity_type(self, request_data):
        try:
            existing = await self.dao.get_identity_type_by_name(request_data.identity_type_name)
            if existing:
                raise HTTPException(status_code=422, detail="Identity Type with this name already exists")
            uuid = generate_uuid7()

            result = await self.dao.create_identity_type(request_data, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete_identity_type(self, uuid):
        try:
            existing = await self.dao.get_identity_type_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail = "Identity Type not Found")
            return await self.dao.delete_identity_type(uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_identity_type(self, uuid, request_data):
        try:
            existing = await self.dao.get_identity_type_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail = "Identity Type Not Found")
            existing = await self.dao.get_identity_type_by_name(request_data.identity_type_name)
            if existing:
                raise HTTPException(status_code=422, detail="Identity Type with this name already exists")
            await self.dao.update_identity_type(uuid, request_data)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
            