from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.repositories.scheme_query import SchemeQueryRepository
from app.schemas.scheme import SchemeVersionResponse, SchemeRuleResponse, SchemeBenefitResponse, SchemeRequirementResponse

router = APIRouter()


@router.get("/{version_id}", response_model=SchemeVersionResponse, summary="Get a specific scheme version")
async def get_scheme_version(version_id: UUID, db: AsyncSession = Depends(get_async_db)):
    repo = SchemeQueryRepository(db)
    version = await repo.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    reqs = [SchemeRequirementResponse(**r) for r in (version.requirement_definitions or [])]
    return SchemeVersionResponse(
        id=version.id,
        scheme_id=version.scheme_id,
        version_number=version.version_number,
        effective_from=version.effective_from,
        effective_to=version.effective_to,
        verification_status=version.verification_status,
        content_hash=version.content_hash,
        published_at=version.published_at,
        source_id=version.source_id,
        rules=[SchemeRuleResponse.model_validate(r) for r in version.rules],
        requirements=reqs,
        benefits=[SchemeBenefitResponse.model_validate(b) for b in version.benefits],
        created_at=version.created_at,
    )
