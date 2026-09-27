from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.repositories.scheme_query import SchemeQueryRepository
from app.schemas.scheme import SchemeSourceResponse

router = APIRouter()


def _source_resp(source) -> SchemeSourceResponse:
    return SchemeSourceResponse(
        id=source.id,
        authority=source.authority,
        source_type=source.source_type,
        # Only expose non-internal public URLs, omit filesystem paths
        source_url=source.source_url if source.source_url and source.source_url.startswith("http") else None,
        jurisdiction=source.jurisdiction,
        active=source.active,
        last_checked=source.last_checked,
        created_at=source.created_at,
    )


@router.get("", response_model=List[SchemeSourceResponse], summary="List all scheme sources")
async def list_scheme_sources(db: AsyncSession = Depends(get_async_db)):
    repo = SchemeQueryRepository(db)
    sources = await repo.list_sources()
    return [_source_resp(s) for s in sources]


@router.get("/{source_id}", response_model=SchemeSourceResponse, summary="Get a scheme source")
async def get_scheme_source(source_id: UUID, db: AsyncSession = Depends(get_async_db)):
    repo = SchemeQueryRepository(db)
    source = await repo.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return _source_resp(source)
