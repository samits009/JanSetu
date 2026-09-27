from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.repositories.scheme_query import SchemeQueryRepository
from app.services.scheme_intelligence import SchemeIntelligenceService
from app.services.admin_auth import get_current_admin
from app.schemas.scheme import (
    SchemeSummaryResponse, SchemeDetailResponse, PaginatedSchemeResponse,
    SchemeVersionResponse, SchemeRuleResponse, SchemeRequirementResponse,
    SchemeBenefitResponse, SchemeRefreshResponse,
)

router = APIRouter()

MAX_PAGE_SIZE = 100


from sqlalchemy import select
from app.models.scheme import RequirementTranslation


def _summary(scheme, language: Optional[str] = None) -> SchemeSummaryResponse:
    vs = scheme.current_version.verification_status if scheme.current_version else None
    official_name = scheme.official_name
    description = scheme.description

    if language and getattr(scheme, "translations", None):
        for t in scheme.translations:
            if t.language == language:
                official_name = t.official_name or official_name
                description = t.description or description
                break

    return SchemeSummaryResponse(
        id=scheme.id,
        official_name=official_name,
        category=scheme.category,
        level=scheme.level,
        state=scheme.state,
        description=description,
        current_version_id=scheme.current_version_id,
        verification_status=vs,
        created_at=scheme.created_at,
    )


def _version_resp(version, req_map: Optional[dict] = None) -> SchemeVersionResponse:
    raw_reqs = version.requirement_definitions or []
    reqs = []
    for r in raw_reqs:
        r_copy = dict(r)
        if req_map and r_copy.get("name") in req_map:
            trans = req_map[r_copy["name"]]
            r_copy["name"] = trans.get("label", r_copy["name"])
            if trans.get("description"):
                r_copy["description"] = trans["description"]
        reqs.append(SchemeRequirementResponse(**r_copy))

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


@router.get("", response_model=PaginatedSchemeResponse, summary="List schemes (paginated)")
async def list_schemes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=MAX_PAGE_SIZE),
    search: Optional[str] = Query(default=None),
    jurisdiction: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    verification_status: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_async_db),
):
    repo = SchemeQueryRepository(db)
    items, total = await repo.list_schemes(
        page=page, page_size=page_size, search=search,
        jurisdiction=jurisdiction, state=state,
        category=category, verification_status=verification_status,
    )
    return PaginatedSchemeResponse(
        items=[_summary(s, language=language) for s in items],
        page=page,
        page_size=page_size,
        total=total,
        has_next=(page * page_size) < total,
    )


@router.get("/{scheme_id}", response_model=SchemeDetailResponse, summary="Get scheme detail")
async def get_scheme(
    scheme_id: UUID, 
    language: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_async_db)
):
    repo = SchemeQueryRepository(db)
    scheme = await repo.get_scheme_detail(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    req_map = None
    official_name = scheme.official_name
    description = scheme.description

    if language:
        if getattr(scheme, "translations", None):
            for t in scheme.translations:
                if t.language == language:
                    official_name = t.official_name or official_name
                    description = t.description or description
                    break

        req_trans = (await db.execute(
            select(RequirementTranslation).where(RequirementTranslation.language == language)
        )).scalars().all()
        req_map = {rt.requirement_name: {"label": rt.label, "description": rt.description} for rt in req_trans}

    cv = _version_resp(scheme.current_version, req_map=req_map) if scheme.current_version else None
    return SchemeDetailResponse(
        id=scheme.id,
        official_name=official_name,
        authority=scheme.authority,
        category=scheme.category,
        level=scheme.level,
        state=scheme.state,
        description=description,
        current_version_id=scheme.current_version_id,
        current_version=cv,
        created_at=scheme.created_at,
        updated_at=scheme.updated_at,
    )


@router.get("/{scheme_id}/versions", response_model=List[SchemeVersionResponse], summary="List all versions of a scheme")
async def list_scheme_versions(scheme_id: UUID, db: AsyncSession = Depends(get_async_db)):
    repo = SchemeQueryRepository(db)
    versions = await repo.get_scheme_versions(scheme_id)
    return [_version_resp(v) for v in versions]


@router.get("/{scheme_id}/rules", response_model=List[SchemeRuleResponse], summary="Get current version rules")
async def get_scheme_rules(scheme_id: UUID, db: AsyncSession = Depends(get_async_db)):
    repo = SchemeQueryRepository(db)
    rules = await repo.get_scheme_rules(scheme_id)
    return [SchemeRuleResponse.model_validate(r) for r in rules]


@router.get("/{scheme_id}/requirements", response_model=List[SchemeRequirementResponse], summary="Get current version requirements")
async def get_scheme_requirements(scheme_id: UUID, db: AsyncSession = Depends(get_async_db)):
    repo = SchemeQueryRepository(db)
    scheme = await repo.get_scheme_detail(scheme_id)
    if not scheme or not scheme.current_version:
        return []
    reqs = scheme.current_version.requirement_definitions or []
    return [SchemeRequirementResponse(**r) for r in reqs]


@router.get("/{scheme_id}/benefits", response_model=List[SchemeBenefitResponse], summary="Get current version benefits")
async def get_scheme_benefits(scheme_id: UUID, db: AsyncSession = Depends(get_async_db)):
    repo = SchemeQueryRepository(db)
    benefits = await repo.get_scheme_benefits(scheme_id)
    return [SchemeBenefitResponse.model_validate(b) for b in benefits]


@router.post("/{scheme_id}/refresh", response_model=SchemeRefreshResponse, summary="Refresh scheme from source (Admin only)")
async def refresh_scheme(
    scheme_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    actor: str = Depends(get_current_admin),
):
    svc = SchemeIntelligenceService(db)
    return await svc.refresh(scheme_id, actor)
