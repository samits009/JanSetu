import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import ChatRequest, ChatResponse, ConsentRequestPayload, ConsentResponse

# Domain dependencies
from app.repositories.citizen import CitizenRepository
from app.repositories.scheme import SchemeRepository
from app.repositories.application import ApplicationRepository, ConsentRepository, AuditRepository
from app.services.welfare_state import WelfareStateService
from app.services.benefit_survival import BenefitSurvivalService
from app.services.eligibility import EligibilityService
from app.services.evidence_matching import EvidenceMatchingService
from app.services.application_service import ApplicationService
from app.services.application_state_machine import ApplicationStateMachine
from app.services.application_recovery import ApplicationRecoveryService
from app.services.consent import ConsentService
from app.services.audit import AuditService
from app.services.scheme_registry import SchemeRegistryService
from app.services.policy_engine import PolicyRuleEngine
import os
from app.providers.government_handoff import OfficialPortalHandoffProvider
from app.repositories.evidence import EvidenceRepository, DocumentRepository

# Agent imports
from app.agents.providers.gemini import GeminiProvider, GEMINI_AVAILABLE
from app.agents.providers.deterministic import DeterministicDomainFallbackProvider
from app.agents.welfare_agent import WelfareAgent
from app.agents.tool_implementations import AgentContext
from app.services.authorization import authorize_citizen

router = APIRouter()

async def get_agent_context(citizen_id: uuid.UUID, db_session: AsyncSession) -> AgentContext:
    cit_repo = CitizenRepository(db_session)
    scheme_repo = SchemeRepository(db_session)
    app_repo = ApplicationRepository(db_session)
    consent_repo = ConsentRepository(db_session)
    audit_repo = AuditRepository(db_session)
    ev_repo = EvidenceRepository(db_session)
    
    scheme_registry = SchemeRegistryService(scheme_repo)
    policy_engine = PolicyRuleEngine()
    eligibility_service = EligibilityService(policy_engine)
    welfare_state_svc = WelfareStateService(cit_repo, scheme_registry, eligibility_service)
    benefit_survival_svc = BenefitSurvivalService(welfare_state_svc, eligibility_service, scheme_registry)
    evidence_matching_svc = EvidenceMatchingService(ev_repo, scheme_repo)
    state_machine = ApplicationStateMachine(app_repo)
    application_svc = ApplicationService(
        app_repo, state_machine, cit_repo, scheme_registry, eligibility_service, evidence_matching_svc
    )
    consent_svc = ConsentService(consent_repo)
    application_recovery_svc = ApplicationRecoveryService(
        app_repo, state_machine, evidence_matching_svc, consent_svc
    )
    gov_provider = OfficialPortalHandoffProvider(app_repo, state_machine)
    audit_svc = AuditService(audit_repo)

    return AgentContext(
        citizen_id=citizen_id,
        db_session=db_session,
        cit_repo=cit_repo,
        scheme_repo=scheme_repo,
        app_repo=app_repo,
        welfare_state_svc=welfare_state_svc,
        benefit_survival_svc=benefit_survival_svc,
        eligibility_svc=eligibility_service,
        evidence_matching_svc=evidence_matching_svc,
        application_svc=application_svc,
        application_recovery_svc=application_recovery_svc,
        consent_svc=consent_svc,
        audit_svc=audit_svc,
        gov_provider=gov_provider
    )

from app.services.authentication import AuthenticationService

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request, db_session: AsyncSession = Depends(get_async_db)):
    if request.citizen_id:
        principal = await authorize_citizen(request.citizen_id, http_request, db_session)
        effective_citizen_id = principal.citizen_id
    else:
        principal = await AuthenticationService(db_session).current(http_request)
        if not principal.citizen_id:
            raise HTTPException(status_code=400, detail="Citizen profile required for agent context")
        effective_citizen_id = principal.citizen_id

    ctx = await get_agent_context(effective_citizen_id, db_session)
    
    fallback_provider = DeterministicDomainFallbackProvider()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and GEMINI_AVAILABLE:
        try:
            provider = GeminiProvider(api_key=api_key, fallback=fallback_provider)
        except Exception:
            provider = fallback_provider
    else:
        provider = fallback_provider

    agent = WelfareAgent(provider)
    response = await agent.chat(request.message, ctx)
    
    return {
        "message": response.message,
        "actions": response.actions,
        "requires_consent": response.requires_consent,
        "consent_id": response.consent_id,
        "consent_action": response.consent_action,
        "consent_application_id": response.consent_application_id,
        "workflow_state": response.workflow_state,
        "execution_trace": [trace.model_dump() for trace in response.execution_trace]
    }

@router.post("/consent/{consent_id}/grant")
async def provide_consent(
    consent_id: uuid.UUID, 
    request: ConsentRequestPayload, 
    http_request: Request,
    db_session: AsyncSession = Depends(get_async_db)
):
    consent_repo = ConsentRepository(db_session)
    consent = await consent_repo.get_by_id(consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")

    await authorize_citizen(consent.citizen_id, http_request, db_session)
    
    consent_svc = ConsentService(consent_repo)
    
    # Assuming action="GRANT" or "REVOKE"
    if request.action.upper() == "GRANT":
        success = await consent_svc.grant(consent_id)
    elif request.action.upper() == "REVOKE":
        success = await consent_svc.revoke(consent_id)
    else:
        raise HTTPException(status_code=422, detail="Consent action must be GRANT or REVOKE")
        
    if not success:
        raise HTTPException(status_code=404, detail="Consent not found")

    if request.action.upper() == "GRANT":
        await AuditService(AuditRepository(db_session)).record(
            citizen_id=consent.citizen_id,
            actor="CITIZEN",
            action="CONSENT_GRANTED",
            purpose=consent.purpose,
            result="SUCCESS",
            consent_id=consent.id,
            application_id=consent.application_id,
        )
        
    return {"success": True, "granted": request.action.upper() == "GRANT"}
