from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from uuid import UUID

from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.application import ApplicationRepository, ConsentRepository, AuditRepository
from app.repositories.citizen import CitizenRepository
from app.repositories.scheme import SchemeRepository
from app.repositories.evidence import EvidenceRepository

from app.services.application_service import ApplicationService
from app.services.application_state_machine import ApplicationStateMachine
from app.services.application_recovery import ApplicationRecoveryService
from app.services.consent import ConsentService
from app.services.audit import AuditService
from app.services.scheme_registry import SchemeRegistryService
from app.services.eligibility import EligibilityService
from app.services.policy_engine import PolicyRuleEngine
from app.services.evidence_matching import EvidenceMatchingService
from app.providers.government_handoff import OfficialPortalHandoffProvider

from app.schemas.application import (
    ApplicationCreateRequest, 
    ApplicationResponse, 
    ApplicationDetailResponse, 
    RecoveryPlanResponse
)
from app.services.authorization import authorize_citizen, authorize_application, get_current_identity
from app.services.identity import IdentityPrincipal

router = APIRouter()

def get_app_service(db: AsyncSession = Depends(get_async_db)) -> ApplicationService:
    app_repo = ApplicationRepository(db)
    cit_repo = CitizenRepository(db)
    scheme_repo = SchemeRepository(db)
    ev_repo = EvidenceRepository(db)
    
    state_machine = ApplicationStateMachine(app_repo)
    registry = SchemeRegistryService(scheme_repo)
    engine = PolicyRuleEngine()
    eligibility = EligibilityService(engine)
    evidence_matching = EvidenceMatchingService(ev_repo, scheme_repo)
    
    return ApplicationService(
        app_repo, state_machine, cit_repo, registry, eligibility, evidence_matching
    )

def get_recovery_service(db: AsyncSession = Depends(get_async_db)) -> ApplicationRecoveryService:
    app_repo = ApplicationRepository(db)
    ev_repo = EvidenceRepository(db)
    scheme_repo = SchemeRepository(db)
    consent_repo = ConsentRepository(db)
    
    state_machine = ApplicationStateMachine(app_repo)
    evidence_matching = EvidenceMatchingService(ev_repo, scheme_repo)
    consent_svc = ConsentService(consent_repo)
    
    return ApplicationRecoveryService(app_repo, state_machine, evidence_matching, consent_svc)

@router.get("/me", response_model=List[ApplicationResponse])
async def list_my_applications(
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db)
):
    if not principal.citizen_id:
        return []
    app_repo = ApplicationRepository(db)
    apps = await app_repo.find_for_citizen(principal.citizen_id)
    return [
        {
            "id": app.id,
            "scheme_id": app.scheme_id,
            "scheme_name": app.scheme.official_name if app.scheme else "Welfare Scheme",
            "status": app.status,
            "created_at": app.created_at,
            "updated_at": app.updated_at
        }
        for app in apps
    ]

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    http_request: Request,
    request: ApplicationCreateRequest,
    service: ApplicationService = Depends(get_app_service)
):
    from app.services.authentication import AuthenticationService
    principal = await AuthenticationService(service.app_repo.session).current(http_request)
    effective_citizen_id = request.citizen_id or principal.citizen_id
    if not effective_citizen_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    if request.citizen_id and request.citizen_id != principal.citizen_id:
        raise HTTPException(status_code=403, detail="Citizen access denied")

    app = await service.create_application(effective_citizen_id, request.scheme_id)
    scheme = await service.scheme_registry.get_scheme(request.scheme_id)
    scheme_name = scheme.official_name if scheme else "Unknown Scheme"
    return {
        "id": app.id,
        "scheme_id": app.scheme_id,
        "scheme_name": scheme_name,
        "status": app.status,
        "created_at": app.created_at,
        "updated_at": app.updated_at
    }

@router.get("/{application_id}/status", response_model=ApplicationDetailResponse)
async def get_application_status(
    application_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    await authorize_application(application_id, request, db)
    repo = ApplicationRepository(db)
    app = await repo.get_with_requirements(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    timeline = await repo.get_timeline(application_id)
        
    return {
        "id": app.id,
        "scheme_id": app.scheme_id,
        "scheme_name": app.scheme.official_name if app.scheme else "Unknown Scheme",
        "status": app.status,
        "requirements": app.requirements,
        "rejection_reason": app.rejection_reason,
        "government_reference_id": app.government_reference_id,
        "timeline": [
            {"status": event.action, "timestamp": event.created_at}
            for event in timeline
            if event.created_at is not None
        ]
    }

@router.post("/{application_id}/recover", response_model=RecoveryPlanResponse)
async def recover_application(
    application_id: UUID,
    request: Request,
    service: ApplicationRecoveryService = Depends(get_recovery_service)
):
    await authorize_application(application_id, request, service.app_repo.session)
    return await service.recover(application_id)

@router.post("/{application_id}/resubmit", response_model=ApplicationResponse)
async def resubmit_application(
    application_id: UUID,
    request: Request,
    service: ApplicationRecoveryService = Depends(get_recovery_service),
    db: AsyncSession = Depends(get_async_db)
):
    await authorize_application(application_id, request, db)
    await service.resubmit(application_id)
    
    app_repo = ApplicationRepository(db)
    state_machine = ApplicationStateMachine(app_repo)
    gov_provider = OfficialPortalHandoffProvider(app_repo, state_machine)
    await gov_provider.prepare_handoff(application_id)
    
    app = await app_repo.get_by_id(application_id)
    return {
        "id": app.id,
        "scheme_id": app.scheme_id,
        "scheme_name": app.scheme.official_name if app.scheme else "Unknown Scheme",
        "status": app.status,
        "created_at": app.created_at,
        "updated_at": app.updated_at
    }

@router.post("/{application_id}/submit", response_model=ApplicationResponse)
async def submit_application(
    application_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    app_repo = ApplicationRepository(db)
    await authorize_application(application_id, request, db)
    state_machine = ApplicationStateMachine(app_repo)
    
    app = await app_repo.get_by_id(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    consent_service = ConsentService(ConsentRepository(db))
    await consent_service.check(app.citizen_id, "APPLICATION_SUBMISSION", app.id)
        
    # State transitions to get to submitting
    if app.status == "EVIDENCE_COMPLETE":
         await state_machine.transition(app.id, app.status, "DRAFTED")
         app = await app_repo.get_by_id(application_id)
    if app.status == "DRAFTED":
         await state_machine.transition(app.id, app.status, "AWAITING_CONSENT")
         app = await app_repo.get_by_id(application_id)
    if app.status == "AWAITING_CONSENT":
         await state_machine.transition(app.id, app.status, "SUBMITTING")

    gov_provider = OfficialPortalHandoffProvider(app_repo, state_machine)
    await gov_provider.submit_application(application_id)

    await AuditService(AuditRepository(db)).record(
        citizen_id=app.citizen_id,
        actor="CITIZEN",
        action="OFFICIAL_PORTAL_HANDOFF",
        purpose="Application prepared and handed off to official portal",
        result="SUCCESS",
        application_id=app.id,
    )
    
    app = await app_repo.get_by_id(application_id)
    
    return {
        "id": app.id,
        "scheme_id": app.scheme_id,
        "scheme_name": app.scheme.official_name if app.scheme else "Unknown Scheme",
        "status": app.status,
        "created_at": app.created_at,
        "updated_at": app.updated_at
    }

@router.post("/{application_id}/handoff")
async def get_portal_handoff(
    application_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    await authorize_application(application_id, request, db)
    app_repo = ApplicationRepository(db)
    state_machine = ApplicationStateMachine(app_repo)
    gov_provider = OfficialPortalHandoffProvider(app_repo, state_machine)
    return await gov_provider.prepare_handoff(application_id)

