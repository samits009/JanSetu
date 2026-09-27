import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .tools import tool_registry
from .permissions import ToolPermissionLevel
from .tool_schemas import ToolResult

from app.services.welfare_state import WelfareStateService
from app.services.benefit_survival import BenefitSurvivalService
from app.services.eligibility import EligibilityService
from app.services.evidence_matching import EvidenceMatchingService
from app.services.application_service import ApplicationService
from app.services.application_recovery import ApplicationRecoveryService
from app.services.consent import ConsentService
from app.services.audit import AuditService
from app.repositories.citizen import CitizenRepository
from app.repositories.scheme import SchemeRepository
from app.repositories.application import ApplicationRepository
from app.providers.government_handoff import GovernmentApplicationProvider
from app.domain.enums import ApplicationStatus

# Re-usable context passed to tools
class AgentContext:
    def __init__(
        self,
        citizen_id: uuid.UUID,
        db_session: AsyncSession,
        cit_repo: CitizenRepository,
        scheme_repo: SchemeRepository,
        app_repo: ApplicationRepository,
        welfare_state_svc: WelfareStateService,
        benefit_survival_svc: BenefitSurvivalService,
        eligibility_svc: EligibilityService,
        evidence_matching_svc: EvidenceMatchingService,
        application_svc: ApplicationService,
        application_recovery_svc: ApplicationRecoveryService,
        consent_svc: ConsentService,
        audit_svc: AuditService,
        gov_provider: GovernmentApplicationProvider
    ):
        self.citizen_id = citizen_id
        self.db_session = db_session
        self.cit_repo = cit_repo
        self.scheme_repo = scheme_repo
        self.app_repo = app_repo
        self.welfare_state_svc = welfare_state_svc
        self.benefit_survival_svc = benefit_survival_svc
        self.eligibility_svc = eligibility_svc
        self.evidence_matching_svc = evidence_matching_svc
        self.application_svc = application_svc
        self.application_recovery_svc = application_recovery_svc
        self.consent_svc = consent_svc
        self.audit_svc = audit_svc
        self.gov_provider = gov_provider


# ---------------------------------------------------------
# READ_ONLY Tools
# ---------------------------------------------------------

class GetCitizenProfileInput(BaseModel):
    pass

@tool_registry.register(
    name="get_citizen_profile",
    description="Get the citizen profile, household, and employments.",
    input_schema=GetCitizenProfileInput,
    permission_level=ToolPermissionLevel.READ_ONLY
)
async def get_citizen_profile(ctx: AgentContext, args: GetCitizenProfileInput) -> ToolResult:
    citizen = await ctx.cit_repo.get_full_welfare_context(ctx.citizen_id)
    if not citizen:
        return ToolResult(success=False, reason="Citizen not found")
    
    return ToolResult(
        success=True,
        data={
            "name": citizen.name,
            "dob": str(citizen.dob),
            "locations": [{"state": l.state, "district": l.district, "is_active": l.is_active} for l in citizen.locations],
            "employments": [{"occupation": e.occupation, "is_active": getattr(e, 'is_active', True)} for e in citizen.employments]
        },
        reason="Fetched profile"
    )

class GetWelfareStateInput(BaseModel):
    pass

@tool_registry.register(
    name="get_welfare_state",
    description="Get the current welfare state of the citizen including active benefits and new opportunities.",
    input_schema=GetWelfareStateInput,
    permission_level=ToolPermissionLevel.READ_ONLY
)
async def get_welfare_state(ctx: AgentContext, args: GetWelfareStateInput) -> ToolResult:
    state = await ctx.welfare_state_svc.evaluate(ctx.citizen_id)
    return ToolResult(
        success=True,
        data={
            "active_benefits": [{"scheme_name": b.scheme.official_name, "status": b.status} for b in state["active_benefits"]],
            "new_opportunities": [{"scheme_name": s.official_name, "category": s.category, "id": str(s.id)} for s in state["new_opportunities"]]
        },
        reason="Fetched welfare state"
    )

class EvaluateLocationChangeInput(BaseModel):
    state: str
    district: str

@tool_registry.register(
    name="evaluate_location_change",
    description="Evaluate the impact of a location change on the citizen's benefits.",
    input_schema=EvaluateLocationChangeInput,
    permission_level=ToolPermissionLevel.READ_ONLY
)
async def evaluate_location_change(ctx: AgentContext, args: EvaluateLocationChangeInput) -> ToolResult:
    # Need to find the location object. For the mock we can just pass the string.
    # In reality, the BenefitSurvivalService expects a Location object.
    # We will simulate the check here.
    from app.models.citizen import Location
    dummy_loc = Location(citizen_id=ctx.citizen_id, state=args.state, district=args.district)
    
    survival = await ctx.benefit_survival_svc.evaluate_location_change(ctx.citizen_id, dummy_loc)
    return ToolResult(
        success=True,
        data={
            "continued_benefits": [{"scheme_name": b.scheme.official_name} for b in survival["continued_benefits"]],
            "at_risk_benefits": [{"scheme_name": b.scheme.official_name} for b in survival["at_risk_benefits"]],
            "new_benefits": [{"scheme_name": s.official_name} for s in survival["new_benefits"]]
        },
        reason="Evaluated location change"
    )


class EvaluateEligibilityInput(BaseModel):
    category: str

@tool_registry.register(
    name="evaluate_eligibility",
    description="Evaluate eligibility for schemes in a given category.",
    input_schema=EvaluateEligibilityInput,
    permission_level=ToolPermissionLevel.READ_ONLY
)
async def evaluate_eligibility(ctx: AgentContext, args: EvaluateEligibilityInput) -> ToolResult:
    state = await ctx.welfare_state_svc.evaluate(ctx.citizen_id)
    schemes = [s for s in state["new_opportunities"] if s.category == args.category]
    return ToolResult(
        success=True,
        data={
            "eligible_schemes": [{"id": str(s.id), "name": s.official_name} for s in schemes]
        },
        reason="Evaluated eligibility"
    )

class SearchEvidenceInput(BaseModel):
    category: Optional[str] = None
    requirement_type: Optional[str] = None

@tool_registry.register(
    name="search_evidence",
    description="Search for existing evidence matching a category or requirement type.",
    input_schema=SearchEvidenceInput,
    permission_level=ToolPermissionLevel.READ_ONLY
)
async def search_evidence(ctx: AgentContext, args: SearchEvidenceInput) -> ToolResult:
    if args.requirement_type:
        evidence = await ctx.evidence_matching_svc.evidence_repo.find_matching_requirement(
            ctx.citizen_id, args.requirement_type
        )
    else:
        evidence = await ctx.evidence_matching_svc.evidence_repo.find_for_citizen(ctx.citizen_id)

    return ToolResult(
        success=True,
        data={
            "found_evidence": bool(evidence),
            "evidence": [
                {
                    "id": str(item.id),
                    "evidence_type": item.evidence_type,
                    "confidence": item.confidence,
                    "document_type": item.document.document_type if item.document else None,
                    "verified": item.document.verification_status == "VERIFIED" if item.document else False,
                }
                for item in evidence
            ],
        },
        reason="Evidence searched"
    )


class InterpretGovernmentResponseInput(BaseModel):
    application_id: str

@tool_registry.register(
    name="interpret_government_response",
    description="Get the status of an application and interpret any government requirements.",
    input_schema=InterpretGovernmentResponseInput,
    permission_level=ToolPermissionLevel.READ_ONLY
)
async def interpret_government_response(ctx: AgentContext, args: InterpretGovernmentResponseInput) -> ToolResult:
    status = await ctx.gov_provider.get_application_status(uuid.UUID(args.application_id))
    return ToolResult(
        success=True,
        data={"status": status, "interpretation": "Additional evidence may be required if UNDER_REVIEW or REQUIRES_EVIDENCE"},
        reason="Interpreted government response"
    )

# ---------------------------------------------------------
# LOW_IMPACT Tools
# ---------------------------------------------------------

class PrepareApplicationInput(BaseModel):
    scheme_id: str

@tool_registry.register(
    name="prepare_application",
    description="Prepare a new welfare application.",
    input_schema=PrepareApplicationInput,
    permission_level=ToolPermissionLevel.LOW_IMPACT
)
async def prepare_application(ctx: AgentContext, args: PrepareApplicationInput) -> ToolResult:
    try:
        app = await ctx.application_svc.create_application(ctx.citizen_id, uuid.UUID(args.scheme_id))
        return ToolResult(
            success=True,
            data={"application_id": str(app.id), "status": app.status},
            reason="Application prepared"
        )
    except Exception as e:
        return ToolResult(success=False, reason=str(e))


class PrepareRecoveryInput(BaseModel):
    application_id: str

@tool_registry.register(
    name="prepare_recovery",
    description="Prepare an application recovery plan after evidence was rejected.",
    input_schema=PrepareRecoveryInput,
    permission_level=ToolPermissionLevel.LOW_IMPACT
)
async def prepare_recovery(ctx: AgentContext, args: PrepareRecoveryInput) -> ToolResult:
    try:
        # Check consent first
        if not await ctx.consent_svc.verify(ctx.citizen_id, "APPLICATION_SUBMISSION", uuid.UUID(args.application_id)):
            return ToolResult(success=False, reason="Consent not granted or expired")
        
        gov_ref = await ctx.gov_provider.submit_application(uuid.UUID(args.application_id))
        app = await ctx.app_repo.get_by_id(uuid.UUID(args.application_id))
        return ToolResult(
            success=True,
            data={"application_id": str(app.id), "status": app.status, "government_reference": gov_ref},
            reason="Application submitted"
        )
    except Exception as e:
        return ToolResult(success=False, reason=str(e))

# ---------------------------------------------------------
# HIGH_IMPACT Tools
# ---------------------------------------------------------

class RequestConsentInput(BaseModel):
    action: str
    application_id: Optional[str] = None

@tool_registry.register(
    name="request_consent",
    description="Request explicit consent from the citizen. DOES NOT GRANT CONSENT, ONLY ASKS FOR IT.",
    input_schema=RequestConsentInput,
    permission_level=ToolPermissionLevel.HIGH_IMPACT
)
async def request_consent(ctx: AgentContext, args: RequestConsentInput) -> ToolResult:
    app_id = uuid.UUID(args.application_id) if args.application_id else None
    consent = await ctx.consent_svc.request(ctx.citizen_id, args.action, app_id)
    return ToolResult(
        success=True,
        data={
            "consent_id": str(consent.id),
            "action": getattr(consent.action, "value", consent.action),
            "application_id": str(consent.application_id) if consent.application_id else None,
            "status": "PENDING",
        },
        reason="Consent requested. Waiting for citizen approval.",
        requires_consent=True
    )


class SubmitApplicationInput(BaseModel):
    application_id: str

@tool_registry.register(
    name="submit_application",
    description="Submit an application to the government. Requires explicit consent.",
    input_schema=SubmitApplicationInput,
    permission_level=ToolPermissionLevel.HIGH_IMPACT,
    requires_consent=True,
    audit_action="SUBMIT_APPLICATION"
)
async def submit_application(ctx: AgentContext, args: SubmitApplicationInput) -> ToolResult:
    app_id = uuid.UUID(args.application_id)
    
    # 1. Verify Application Exists
    app = await ctx.app_repo.get_by_id(app_id)
    if not app:
        return ToolResult(success=False, reason="Application not found")
        
    # 2. Check Consent
    try:
        await ctx.consent_svc.check(ctx.citizen_id, "APPLICATION_SUBMISSION", app_id)
    except Exception as e:
        return ToolResult(success=False, reason=f"Consent verification failed: {e}")
        
    # 3. Verify Application State and transition
    try:
        if app.status == ApplicationStatus.EVIDENCE_COMPLETE:
             await ctx.application_svc.state_machine.transition(app.id, app.status, ApplicationStatus.DRAFTED)
             app = await ctx.app_repo.get_by_id(app_id)
        if app.status == ApplicationStatus.DRAFTED:
             await ctx.application_svc.state_machine.transition(app.id, app.status, ApplicationStatus.AWAITING_CONSENT)
             app = await ctx.app_repo.get_by_id(app_id)
        if app.status == ApplicationStatus.AWAITING_CONSENT:
             await ctx.application_svc.state_machine.transition(app.id, app.status, ApplicationStatus.SUBMITTING)
    except Exception as e:
        return ToolResult(success=False, reason=f"State transition failed: {e}")

    # 4. Audit Event
    consent = await ctx.consent_svc.consent_repo.find_valid_consent(ctx.citizen_id, "APPLICATION_SUBMISSION", app_id)
    await ctx.audit_svc.record(
        citizen_id=ctx.citizen_id,
        actor="AGENT",
        action="SUBMIT_APPLICATION",
        purpose="Agent submitting application",
        result="SUCCESS",
        consent_id=consent.id if consent else None,
        application_id=app.id
    )

    # 5. Government Submission
    await ctx.gov_provider.submit_application(app.id)

    return ToolResult(
        success=True,
        data={"application_id": str(app.id), "status": "SUBMITTED"},
        reason="Application successfully submitted"
    )


class ResubmitApplicationInput(BaseModel):
    application_id: str

@tool_registry.register(
    name="resubmit_application",
    description="Resubmit an application to the government after recovery. Requires explicit consent.",
    input_schema=ResubmitApplicationInput,
    permission_level=ToolPermissionLevel.HIGH_IMPACT,
    requires_consent=True,
    audit_action="RESUBMIT_APPLICATION"
)
async def resubmit_application(ctx: AgentContext, args: ResubmitApplicationInput) -> ToolResult:
    app_id = uuid.UUID(args.application_id)
    
    app = await ctx.app_repo.get_by_id(app_id)
    if not app:
        return ToolResult(success=False, reason="Application not found")
        
    try:
        await ctx.consent_svc.check(ctx.citizen_id, "APPLICATION_RESUBMISSION", app_id)
    except Exception as e:
        return ToolResult(success=False, reason=f"Consent verification failed: {e}")

    try:
        await ctx.application_recovery_svc.resubmit(app_id)
    except Exception as e:
        return ToolResult(success=False, reason=f"Resubmission failed: {e}")

    consent = await ctx.consent_svc.consent_repo.find_valid_consent(ctx.citizen_id, "APPLICATION_RESUBMISSION", app_id)
    await ctx.audit_svc.record(
        citizen_id=ctx.citizen_id,
        actor="AGENT",
        action="RESUBMIT_APPLICATION",
        purpose="Agent resubmitting application",
        result="SUCCESS",
        consent_id=consent.id if consent else None,
        application_id=app.id
    )

    return ToolResult(
        success=True,
        data={"application_id": str(app.id), "status": "RESUBMITTED"},
        reason="Application successfully resubmitted"
    )
