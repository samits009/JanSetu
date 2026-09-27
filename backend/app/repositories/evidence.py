from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.evidence import Evidence, Document
from app.repositories.base import BaseRepository


class EvidenceRepository(BaseRepository[Evidence]):
    def __init__(self, session: AsyncSession):
        super().__init__(Evidence, session)

    async def find_for_citizen(self, citizen_id: Any) -> List[Evidence]:
        stmt = (
            select(Evidence)
            .options(selectinload(Evidence.document))
            .where(Evidence.citizen_id == citizen_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_matching_requirement(self, citizen_id: Any, requirement_type: str) -> List[Evidence]:
        stmt = (
            select(Evidence)
            .options(selectinload(Evidence.document))
            .where(Evidence.citizen_id == citizen_id)
            .where(Evidence.evidence_type == requirement_type)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_verified_evidence(self, citizen_id: Any) -> List[Evidence]:
        stmt = (
            select(Evidence)
            .join(Evidence.document)
            .options(selectinload(Evidence.document))
            .where(Evidence.citizen_id == citizen_id)
            .where(Document.verification_status == "VERIFIED")
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def find_for_citizen(self, citizen_id: Any) -> List[Document]:
        stmt = (
            select(Document)
            .options(selectinload(Document.evidence))
            .where(Document.citizen_id == citizen_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_hash(self, citizen_id: Any, content_hash: str) -> Document | None:
        stmt = select(Document).where(
            Document.citizen_id == citizen_id,
            Document.content_hash == content_hash,
        ).options(selectinload(Document.evidence))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_document(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        return document

    async def update_document(self, document: Document, **values: Any) -> Document:
        for key, value in values.items():
            setattr(document, key, value)
        self.session.add(document)
        await self.session.flush()
        return document

    async def get_detail_for_citizen(self, document_id: Any, citizen_id: Any) -> Document | None:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.citizen_id == citizen_id,
        ).options(selectinload(Document.evidence))
        result = await self.session.execute(stmt)
        return result.scalars().first()
