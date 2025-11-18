# Backend/DAL/dao/education_dao.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import EducationDocumentType, EmployeeEducationDocument, CountryEducationDocumentMapping

class EducationDocDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_document_by_name(self, document_name):
        result = await self.db.execute(select(EducationDocumentType).where(EducationDocumentType.document_name == document_name))
        return result.scalar_one_or_none()


    async def create_education_document(self, request_data, uuid):
        new_edu_doc = EducationDocumentType(
            education_document_uuid = uuid,
            document_name = request_data.document_name,
            description = request_data.description
        )
        self.db.add(new_edu_doc)
        await self.db.commit()
        await self.db.refresh(new_edu_doc)
        return new_edu_doc
    
    async def get_all_education_documents(self):
        result = await self.db.execute(select(EducationDocumentType))
        return result.scalars().all()
    async def get_education_document_by_uuid(self, uuid):
        result = await self.db.execute(select(EducationDocumentType).where(EducationDocumentType.education_document_uuid == uuid))
        return result.scalar_one_or_none()
    async def update_education_document(self, uuid, request_data):
        result = await self.db.execute(select(EducationDocumentType).where(EducationDocumentType.education_document_uuid == uuid))
        edu_doc = result.scalar_one_or_none()
        if edu_doc is None:
            return None
        edu_doc.document_name = request_data.document_name
        edu_doc.description = request_data.description
        await self.db.commit()
        await self.db.refresh(edu_doc)
        return edu_doc
    async def delete_education_document_by_uuid(self, uuid):
        result = await self.db.execute(select(EducationDocumentType).where(EducationDocumentType.education_document_uuid == uuid))
        edu_doc = result.scalar_one_or_none()
        if edu_doc is None:
            return None
        await self.db.delete(edu_doc)
        await self.db.commit()
        return edu_doc