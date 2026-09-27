"""
Scheme Admin API — Review and Publish workflow
==============================================
All mutating endpoints require admin authorization.

CRITICAL INVARIANT:
  Only POST /{version_id}/publish may modify Scheme.current_version_id.
  approve / reject / mark-needs-review change only the version's verification_status.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.repositories.scheme_query import SchemeQueryRepository
from app.services.scheme_intelligence import SchemeIntelligenceService
from app.services.admin_auth import get_current_admin
from app.schemas.scheme import SchemeReviewResponse, SchemeVersionResponse, SchemeRequirementResponse, SchemeRuleResponse, SchemeBenefitResponse

router = APIRouter()


@router.get("/pending", response_model=List[SchemeVersionResponse], summary="List versions awaiting review (Admin)")
async def get_pending_review(
    db: AsyncSession = Depends(get_async_db),
    actor: str = Depends(get_current_admin),
):
    repo = SchemeQueryRepository(db)
    versions = await repo.get_pending_review()
    result = []
    for v in versions:
        reqs = [SchemeRequirementResponse(**r) for r in (v.requirement_definitions or [])]
        result.append(SchemeVersionResponse(
            id=v.id,
            scheme_id=v.scheme_id,
            version_number=v.version_number,
            effective_from=v.effective_from,
            effective_to=v.effective_to,
            verification_status=v.verification_status,
            content_hash=v.content_hash,
            published_at=v.published_at,
            source_id=v.source_id,
            rules=[SchemeRuleResponse.model_validate(r) for r in v.rules] if v.rules else [],
            requirements=reqs,
            benefits=[SchemeBenefitResponse.model_validate(b) for b in v.benefits] if v.benefits else [],
            created_at=v.created_at,
        ))
    return result


@router.post("/{version_id}/approve", response_model=SchemeReviewResponse, summary="Approve a candidate version (Admin)")
async def approve_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    actor: str = Depends(get_current_admin),
):
    svc = SchemeIntelligenceService(db)
    return await svc.approve_version(version_id, actor)


@router.post("/{version_id}/reject", response_model=SchemeReviewResponse, summary="Reject a candidate version (Admin)")
async def reject_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    actor: str = Depends(get_current_admin),
):
    svc = SchemeIntelligenceService(db)
    return await svc.reject_version(version_id, actor)


@router.post("/{version_id}/mark-needs-review", response_model=SchemeReviewResponse, summary="Mark a version as needing review (Admin)")
async def mark_needs_review(
    version_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    actor: str = Depends(get_current_admin),
):
    svc = SchemeIntelligenceService(db)
    return await svc.mark_needs_review(version_id, actor)


@router.post("/{version_id}/publish", response_model=SchemeReviewResponse, summary="Publish a version as the current live version (Admin)")
async def publish_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    actor: str = Depends(get_current_admin),
):
    """
    CRITICAL: This is the ONLY endpoint that may update Scheme.current_version_id.
    Operates in a transaction. If it fails, current_version_id remains unchanged.
    REJECTED versions cannot be published.
    """
    svc = SchemeIntelligenceService(db)
    return await svc.publish_version(version_id, actor)
