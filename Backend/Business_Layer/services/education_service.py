from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.education_dao import EducationDocDAO
from ..utils.validation_utils import validate_alphabets_only
from ..utils.uuid_generator import generate_uuid7

class EducationDocService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EducationDocDAO(self.db)
    async def create_education_document(self, request_data):
        try:
            document_name = validate_alphabets_only(request_data.document_name)
            existing = await self.dao.get_document_by_name(document_name)
            if existing:
                raise HTTPException(status_code=404, detail="Document Already Exists")
            uuid = generate_uuid7()
            result = await self.dao.create_education_document(request_data, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_all_education_documents(self):
        try:
            result = await self.dao.get_all_education_documents()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_education_document_by_uuid(self, uuid):
        try:
            result = await self.dao.get_education_document_by_uuid(uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_education_document(self, uuid, request_data):
        try:
            document_name = validate_alphabets_only(request_data.document_name)
            existing = await self.dao.get_document_by_name(document_name)
            if existing:
                raise HTTPException(status_code=404, detail="Document Already Exists")
            return await self.dao.update_education_document(uuid, request_data)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def delete_education_document_by_uuid(self, uuid):
        try:
            existing = await self.dao.get_education_document_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Document Not Found")
            return await self.dao.delete_education_document_by_uuid(uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        