from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.citizen import CitizenRepository
from app.repositories.scheme import SchemeRepository
from app.repositories.evidence import EvidenceRepository
from app.services.scheme_registry import SchemeRegistryService
from app.services.eligibility import EligibilityService
from app.services.policy_engine import PolicyRuleEngine
from app.services.welfare_state import WelfareStateService
from app.services.evidence_matching import EvidenceMatchingService

from app.schemas.benefit import BenefitDetailResponse
from app.services.authorization import authorize_citizen

router = APIRouter()

def get_eligibility_service():
    engine = PolicyRuleEngine()
    return EligibilityService(engine)

def get_evidence_matching_service(db: AsyncSession = Depends(get_async_db)):
    ev_repo = EvidenceRepository(db)
    scheme_repo = SchemeRepository(db)
    return EvidenceMatchingService(ev_repo, scheme_repo)

@router.get("/{benefit_id}", response_model=BenefitDetailResponse)
async def get_benefit_detail(
    benefit_id: UUID,
    citizen_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    eligibility_svc: EligibilityService = Depends(get_eligibility_service),
    evidence_svc: EvidenceMatchingService = Depends(get_evidence_matching_service)
    , _auth=Depends(authorize_citizen)
):
    from sqlalchemy import select
    from app.models.application import Benefit, WelfareApplication
    
    stmt = select(Benefit).where(Benefit.id == benefit_id, Benefit.citizen_id == citizen_id)
    result = await db.execute(stmt)
    benefit = result.scalar_one_or_none()
    
    scheme_repo = SchemeRepository(db)
    cit_repo = CitizenRepository(db)
    
    if benefit:
        scheme_id = benefit.scheme_id
        scheme = await scheme_repo.get_with_rules(scheme_id)
        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")
        benefit_status = benefit.status
        record_id = benefit.id
    else:
        scheme = await scheme_repo.get_with_rules(benefit_id)
        if not scheme:
            raise HTTPException(status_code=404, detail="Benefit or scheme not found")
        scheme_id = scheme.id
        benefit_status = "NEW_OPPORTUNITY"
        record_id = scheme.id
        
    citizen = await cit_repo.get_full_welfare_context(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    
    # Evaluate eligibility
    eligibility = eligibility_svc.evaluate(citizen, scheme)
    
    # Evaluate evidence
    coverage = await evidence_svc.evaluate_coverage(citizen_id, scheme_id)
    
    # Format requirements
    satisfied = []
    missing = []
    
    for req in coverage["requirements"]:
        req_eval = {
            "id": req["requirement_id"],
            "name": req["requirement_name"],
            "type": req["requirement_type"],
            "is_satisfied": req["is_satisfied"],
            "linked_evidence_id": req["evidence_id"] if req["is_satisfied"] else None,
            "reason": req.get("reason")
        }
        if req["is_satisfied"]:
            satisfied.append(req_eval)
        else:
            missing.append(req_eval)
            
    # Format evidence
    supporting_evidence = []
    for ev in coverage["evidence_used"]:
        supporting_evidence.append({
            "id": ev["evidence_id"],
            "type": ev["evidence_type"],
            "document_type": ev["document_type"],
            "confidence": ev["confidence"]
        })

    is_eligible = (eligibility.get("status") == "eligible")
    reasons = [f["reason"] for f in eligibility.get("failed_rules", [])]
    if is_eligible:
        reasons = ["Citizen profile fully satisfies deterministic eligibility rules"]

    # Check for active application
    app_stmt = select(WelfareApplication).where(WelfareApplication.citizen_id == citizen_id, WelfareApplication.scheme_id == scheme_id).order_by(WelfareApplication.created_at.desc())
    app_res = await db.execute(app_stmt)
    app_record = app_res.scalars().first()

    return {
        "id": record_id,
        "scheme_id": scheme.id,
        "scheme_name": scheme.official_name,
        "status": benefit_status,
        "eligibility_status": "ELIGIBLE" if is_eligible else "INELIGIBLE",
        "satisfied_requirements": satisfied,
        "missing_requirements": missing,
        "supporting_evidence": supporting_evidence,
        "reasons": reasons,
        "application_status": app_record.status if app_record else None,
        "application_id": app_record.id if app_record else None
    }

