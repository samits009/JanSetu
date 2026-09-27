from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.citizen import CitizenRepository
from app.repositories.scheme import SchemeRepository
from app.repositories.evidence import EvidenceRepository, DocumentRepository
from app.repositories.application import ApplicationRepository
from app.services.scheme_registry import SchemeRegistryService
from app.services.eligibility import EligibilityService
from app.services.policy_engine import PolicyRuleEngine
from app.services.welfare_state import WelfareStateService
from app.services.benefit_survival import BenefitSurvivalService

from app.schemas.citizen import CitizenResponse, OnboardingRequest, OnboardingStepRequest
from app.schemas.welfare import WelfareStateResponse
from app.schemas.benefit import BenefitResponse, BenefitSummary
from app.schemas.document import DocumentResponse, EvidenceResponse
from app.schemas.application import ApplicationResponse
from app.schemas.survival import LocationChangeRequest, SurvivalResponse
from app.models.citizen import Location, Employment, Household, HouseholdMember
from app.models.identity import User
from app.services.authorization import authorize_citizen, get_current_identity
from app.services.identity import IdentityPrincipal
from sqlalchemy import select
from pydantic import BaseModel

router = APIRouter()

def get_cit_repo(db: AsyncSession = Depends(get_async_db)):
    return CitizenRepository(db)

def get_welfare_service(db: AsyncSession = Depends(get_async_db)):
    cit_repo = CitizenRepository(db)
    scheme_repo = SchemeRepository(db)
    registry = SchemeRegistryService(scheme_repo)
    engine = PolicyRuleEngine()
    eligibility = EligibilityService(engine)
    return WelfareStateService(cit_repo, registry, eligibility)

def get_survival_service(db: AsyncSession = Depends(get_async_db)):
    welfare_service = get_welfare_service(db)
    engine = PolicyRuleEngine()
    eligibility = EligibilityService(engine)
    scheme_repo = SchemeRepository(db)
    registry = SchemeRegistryService(scheme_repo)
    return BenefitSurvivalService(welfare_service, eligibility, registry)

@router.get("/me", response_model=CitizenResponse)
async def get_my_citizen(
    principal: IdentityPrincipal = Depends(get_current_identity),
    repo: CitizenRepository = Depends(get_cit_repo)
):
    if not principal.citizen_id:
        raise HTTPException(status_code=404, detail="Citizen profile not linked to user")
    citizen = await repo.get_full_welfare_context(principal.citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen profile not found")
    return {"profile": citizen}

@router.get("/me/welfare-state", response_model=WelfareStateResponse)
async def get_my_welfare_state(
    language: Optional[str] = Query(default=None),
    principal: IdentityPrincipal = Depends(get_current_identity),
    service: WelfareStateService = Depends(get_welfare_service),
    db: AsyncSession = Depends(get_async_db)
):
    if not principal.citizen_id:
        raise HTTPException(status_code=404, detail="Citizen profile not linked to user")
    effective_lang = language or principal.preferred_language
    return await get_welfare_state(principal.citizen_id, language=effective_lang, service=service, _auth=principal, db=db)

@router.get("/me/benefits", response_model=List[BenefitSummary])
async def get_my_benefits(
    principal: IdentityPrincipal = Depends(get_current_identity),
    service: WelfareStateService = Depends(get_welfare_service),
):
    if not principal.citizen_id:
        return []
    state = await service.evaluate(principal.citizen_id)
    return state["active_benefits"]

@router.get("/me/documents", response_model=List[DocumentResponse])
async def get_my_documents(
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
):
    if not principal.citizen_id:
        return []
    repo = DocumentRepository(db)
    return await repo.find_for_citizen(principal.citizen_id)

@router.get("/me/evidence", response_model=List[EvidenceResponse])
async def get_my_evidence(
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
):
    if not principal.citizen_id:
        return []
    repo = EvidenceRepository(db)
    return await repo.find_for_citizen(principal.citizen_id)

@router.get("/me/applications", response_model=List[ApplicationResponse])
async def get_my_applications(
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
):
    if not principal.citizen_id:
        return []
    repo = ApplicationRepository(db)
    apps = await repo.find_for_citizen(principal.citizen_id)
    result = []
    for app in apps:
        result.append({
            "id": app.id,
            "scheme_id": app.scheme_id,
            "scheme_name": app.scheme.official_name if app.scheme else "Unknown Scheme",
            "status": app.status,
            "created_at": app.created_at,
            "updated_at": app.updated_at
        })
    return result
 
@router.put("/me/onboarding/step", response_model=CitizenResponse)
@router.post("/me/onboarding/step", response_model=CitizenResponse)
async def save_onboarding_step(
    data: OnboardingStepRequest,
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
    repo: CitizenRepository = Depends(get_cit_repo)
):
    if not principal.citizen_id:
        raise HTTPException(status_code=404, detail="Citizen profile not linked to user")
    citizen = await repo.get_full_welfare_context(principal.citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen profile not found")

    # Step 1: Personal fields
    if data.name:
        citizen.name = data.name.strip()
    if data.dob:
        citizen.dob = data.dob
    if data.gender:
        citizen.gender = data.gender
    if data.phone:
        citizen.phone = data.phone.strip()

    # Step 2: Location fields
    if data.current_state and data.current_district:
        current_loc = next((l for l in citizen.locations if l.location_type == "CURRENT" and l.is_active), None)
        if current_loc:
            current_loc.state = data.current_state
            current_loc.district = data.current_district
        else:
            current_loc = Location(
                citizen_id=citizen.id,
                location_type="CURRENT",
                state=data.current_state,
                district=data.current_district,
                is_active=True
            )
            db.add(current_loc)

    if data.permanent_state and data.permanent_district:
        perm_loc = next((l for l in citizen.locations if l.location_type == "HOME" and l.is_active), None)
        if perm_loc:
            perm_loc.state = data.permanent_state
            perm_loc.district = data.permanent_district
        else:
            perm_loc = Location(
                citizen_id=citizen.id,
                location_type="HOME",
                state=data.permanent_state,
                district=data.permanent_district,
                is_active=True
            )
            db.add(perm_loc)

    # Step 3: Employment fields
    if data.occupation or data.employment_status or data.annual_income is not None or data.employer_name:
        current_emp = next((e for e in citizen.employments if e.is_current), None)
        if current_emp:
            if data.occupation:
                current_emp.occupation = data.occupation
            if data.employment_status:
                current_emp.employment_status = data.employment_status
            if data.annual_income is not None:
                current_emp.annual_income = data.annual_income
            if data.employer_name:
                current_emp.employer_name = data.employer_name
        else:
            new_emp = Employment(
                citizen_id=citizen.id,
                occupation=data.occupation or "Unspecified",
                employment_status=data.employment_status or "EMPLOYED",
                employer_name=data.employer_name,
                annual_income=data.annual_income,
                is_current=True
            )
            db.add(new_emp)

    # Step 4: Household fields
    if data.household_members_count is not None or data.children_count is not None:
        hh_res = await db.execute(select(Household).where(Household.head_citizen_id == citizen.id))
        household = hh_res.scalars().first()
        member_count = data.household_members_count or 1
        children_count = data.children_count or 0
        dependents_count = children_count
        if not household:
            household = Household(
                head_citizen_id=citizen.id,
                annual_income=data.annual_income or 0,
                member_count=member_count,
                dependents_count=dependents_count,
                children_count=children_count,
            )
            db.add(household)
            await db.flush()
            hh_member = HouseholdMember(
                household_id=household.id,
                citizen_id=citizen.id,
                relationship_to_head="SELF"
            )
            db.add(hh_member)
        else:
            if data.annual_income is not None:
                household.annual_income = data.annual_income
            household.member_count = member_count
            household.dependents_count = dependents_count
            household.children_count = children_count

    citizen.onboarding_step = data.step
    if data.step >= 4:
        citizen.onboarding_completed = True

    await db.flush()
    refreshed_citizen = await repo.get_full_welfare_context(citizen.id)
    return CitizenResponse(profile=refreshed_citizen)


@router.post("/me/onboarding", response_model=CitizenResponse)
async def submit_onboarding(
    data: OnboardingRequest,
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
    repo: CitizenRepository = Depends(get_cit_repo)
):
    if not principal.citizen_id:
        raise HTTPException(status_code=404, detail="Citizen profile not linked to user")
    citizen = await repo.get_full_welfare_context(principal.citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen profile not found")

    # Update citizen personal fields
    if data.name:
        citizen.name = data.name.strip()
    if data.dob:
        citizen.dob = data.dob
    if data.phone:
        citizen.phone = data.phone.strip()
    if data.gender:
        citizen.gender = data.gender

    # Mark onboarding progress
    citizen.onboarding_completed = True
    citizen.onboarding_step = 4

    # Deactivate previous locations and insert new
    for loc in citizen.locations:
        loc.is_active = False

    current_loc = Location(
        citizen_id=citizen.id,
        location_type="CURRENT",
        state=data.current_state,
        district=data.current_district,
        is_active=True
    )
    db.add(current_loc)

    if data.permanent_state and data.permanent_district:
        perm_loc = Location(
            citizen_id=citizen.id,
            location_type="HOME",
            state=data.permanent_state,
            district=data.permanent_district,
            is_active=True
        )
        db.add(perm_loc)

    # Deactivate previous employment and insert new
    for emp in citizen.employments:
        emp.is_current = False

    new_emp = Employment(
        citizen_id=citizen.id,
        occupation=data.occupation,
        employment_status=data.employment_status,
        employer_name=data.employer_name,
        annual_income=data.annual_income,
        is_current=True
    )
    db.add(new_emp)

    # Household
    hh_res = await db.execute(select(Household).where(Household.head_citizen_id == citizen.id))
    household = hh_res.scalars().first()
    member_count = data.household_members_count or 1
    children_count = data.children_count or 0
    dependents_count = children_count  # children are the primary dependents; extend as needed
    if not household:
        household = Household(
            head_citizen_id=citizen.id,
            annual_income=data.annual_income or 0,
            member_count=member_count,
            dependents_count=dependents_count,
            children_count=children_count,
        )
        db.add(household)
        await db.flush()
        hh_member = HouseholdMember(
            household_id=household.id,
            citizen_id=citizen.id,
            relationship_to_head="SELF"
        )
        db.add(hh_member)
    else:
        household.annual_income = data.annual_income or 0
        household.member_count = member_count
        household.dependents_count = dependents_count
        household.children_count = children_count

    await db.flush()
    refreshed_citizen = await repo.get_full_welfare_context(citizen.id)
    return {"profile": refreshed_citizen}


class PreferencesUpdateRequest(BaseModel):
    preferred_language: Optional[str] = None  # 'en' | 'hi'


class PreferencesResponse(BaseModel):
    preferred_language: str


@router.get("/me/preferences", response_model=PreferencesResponse)
async def get_my_preferences(
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
):
    """Return the authenticated citizen's persisted preferences (language, etc.)."""
    from app.models.identity import User
    user = (await db.execute(select(User).where(User.citizen_id == principal.citizen_id))).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return PreferencesResponse(preferred_language=user.preferred_language or "hi")


@router.put("/me/preferences", response_model=PreferencesResponse)
async def update_my_preferences(
    data: PreferencesUpdateRequest,
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
):
    """Persist the authenticated citizen's preferences to PostgreSQL."""
    from app.models.identity import User
    user = (await db.execute(select(User).where(User.citizen_id == principal.citizen_id))).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.preferred_language and data.preferred_language in ("en", "hi"):
        user.preferred_language = data.preferred_language
    await db.flush()
    return PreferencesResponse(preferred_language=user.preferred_language)


@router.get("/{citizen_id}", response_model=CitizenResponse)
async def get_citizen(citizen_id: UUID, repo: CitizenRepository = Depends(get_cit_repo), _auth=Depends(authorize_citizen)):
    citizen = await repo.get_full_welfare_context(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    return {"profile": citizen}

@router.get("/{citizen_id}/welfare-state", response_model=WelfareStateResponse)
async def get_welfare_state(
    citizen_id: UUID,
    language: Optional[str] = Query(default=None),
    service: WelfareStateService = Depends(get_welfare_service),
    _auth=Depends(authorize_citizen),
    db: AsyncSession = Depends(get_async_db)
):
    effective_lang = language or getattr(_auth, "preferred_language", None)
    state = await service.evaluate(citizen_id, language=effective_lang)
    trans_map = {}
    if effective_lang:
        from app.models.scheme import SchemeTranslation
        scheme_ids = set()
        for b in state["active_benefits"]:
            scheme_ids.add(b.scheme_id)
        for b in state["at_risk"]:
            scheme_ids.add(b.scheme_id)
        for opp in state["new_opportunities"]:
            scheme_ids.add(opp["scheme"].id)
        for item in state["needs_verification"]:
            scheme_ids.add(item["scheme"].id)

        if scheme_ids:
            trans_res = await db.execute(
                select(SchemeTranslation).where(
                    SchemeTranslation.scheme_id.in_(list(scheme_ids)),
                    SchemeTranslation.language == effective_lang
                )
            )
            for tr in trans_res.scalars().all():
                trans_map[tr.scheme_id] = tr.official_name

    def benefit_summary(benefit):
        return {
            "id": benefit.id,
            "scheme_id": benefit.scheme_id,
            "scheme_name": trans_map.get(benefit.scheme_id, benefit.scheme.official_name),
            "status": benefit.status.value if hasattr(benefit.status, "value") else benefit.status,
            "amount": benefit.scheme.benefit_amount,
        }

    action_required = []
    for application in state["action_required"]:
        action_required.append({
            "application_id": application.id,
            "title": "Evidence required for application",
            "description": application.rejection_reason or "Additional evidence is required to continue.",
            "action_type": "EVIDENCE_REQUIRED",
            "urgency": "HIGH",
        })

    opportunities = []
    for opportunity in state["new_opportunities"]:
        scheme = opportunity["scheme"]
        vs = scheme.current_version.verification_status if scheme.current_version else "VERIFIED"
        opportunities.append({
            "id": scheme.id,
            "scheme_name": trans_map.get(scheme.id, scheme.official_name),
            "category": scheme.category.value if hasattr(scheme.category, "value") else scheme.category,
            "amount": scheme.benefit_amount,
            "why_it_applies": opportunity.get("why_it_applies", []),
            "matched_rules": opportunity.get("matched_rules", []),
            "missing_evidence": [],
            "readiness_percentage": 100,
            "verification_status": vs.value if hasattr(vs, "value") else str(vs)
        })

    # Calculate evidence readiness score across citizen profile (e.g. 100% if no gaps, else proportion)
    total_gaps = len(state["document_gaps"])
    readiness_score = max(35, 100 - (total_gaps * 20)) if total_gaps > 0 else 100

    return {
        "active_benefits": [benefit_summary(item) for item in state["active_benefits"]],
        "action_required": action_required,
        "new_opportunities": opportunities,
        "at_risk": [benefit_summary(item) for item in state["at_risk"]],
        "needs_verification": [
            {
                "scheme_id": item["scheme"].id,
                "scheme_name": trans_map.get(item["scheme"].id, item["scheme"].official_name),
                "missing_data": item["missing_data"]
            }
            for item in state["needs_verification"]
        ],
        "pending_applications": [
            {"id": item.id, "scheme_id": item.scheme_id, "status": item.status}
            for item in state["pending_applications"]
        ],
        "document_gaps": state["document_gaps"],
        "recommended_actions": state["recommended_actions"],
        "citizen_summary": state["citizen_summary"],
        "evidence_readiness_score": readiness_score,
    }


@router.get("/{citizen_id}/benefits", response_model=List[BenefitSummary])
async def get_benefits(citizen_id: UUID, service: WelfareStateService = Depends(get_welfare_service), _auth=Depends(authorize_citizen)):
    state = await service.evaluate(citizen_id)
    return state["active_benefits"]

@router.post("/{citizen_id}/location-change", response_model=SurvivalResponse)
async def simulate_location_change(
    citizen_id: UUID,
    request: LocationChangeRequest,
    service: BenefitSurvivalService = Depends(get_survival_service)
    , _auth=Depends(authorize_citizen)
):
    loc = Location(citizen_id=citizen_id, state=request.state, district=request.district)
    survival = await service.evaluate_location_change(citizen_id, loc)
    return survival

@router.get("/{citizen_id}/documents", response_model=List[DocumentResponse])
async def get_documents(citizen_id: UUID, db: AsyncSession = Depends(get_async_db), _auth=Depends(authorize_citizen)):
    repo = DocumentRepository(db)
    docs = await repo.find_for_citizen(citizen_id)
    return docs

@router.get("/{citizen_id}/evidence", response_model=List[EvidenceResponse])
async def get_evidence(citizen_id: UUID, db: AsyncSession = Depends(get_async_db), _auth=Depends(authorize_citizen)):
    repo = EvidenceRepository(db)
    evidence = await repo.find_for_citizen(citizen_id)
    return evidence

@router.get("/{citizen_id}/applications", response_model=List[ApplicationResponse])
async def get_applications(citizen_id: UUID, db: AsyncSession = Depends(get_async_db), _auth=Depends(authorize_citizen)):
    repo = ApplicationRepository(db)
    apps = await repo.find_for_citizen(citizen_id)
    # the schema expects scheme_name which isn't on the application object directly unless joined, 
    # but let's assume it works or we'll fetch scheme_name if needed.
    # The application model has scheme.official_name if joined.
    result = []
    for app in apps:
        app_dict = {
            "id": app.id,
            "scheme_id": app.scheme_id,
            "scheme_name": app.scheme.official_name if app.scheme else "Unknown Scheme",
            "status": app.status,
            "created_at": app.created_at,
            "updated_at": app.updated_at
        }
        result.append(app_dict)
    return result
