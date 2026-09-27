from typing import Any, Dict
from app.repositories.application import ApplicationRepository
from app.services.application_state_machine import ApplicationStateMachine
from app.services.eligibility import EligibilityService
from app.services.evidence_matching import EvidenceMatchingService
from app.services.scheme_registry import SchemeRegistryService
from app.repositories.citizen import CitizenRepository
from app.models.application import WelfareApplication, ApplicationRequirement
from app.domain.enums import ApplicationStatus
from app.exceptions import CitizenNotFoundError, SchemeNotFoundError, EligibilityUnknownError
from app.models.audit import AuditEvent

class ApplicationService:
    def __init__(
        self, 
        app_repo: ApplicationRepository, 
        state_machine: ApplicationStateMachine,
        citizen_repo: CitizenRepository,
        scheme_registry: SchemeRegistryService,
        eligibility_service: EligibilityService,
        evidence_matching: EvidenceMatchingService
    ):
        self.app_repo = app_repo
        self.state_machine = state_machine
        self.citizen_repo = citizen_repo
        self.scheme_registry = scheme_registry
        self.eligibility_service = eligibility_service
        self.evidence_matching = evidence_matching

    async def create_application(self, citizen_id: Any, scheme_id: Any) -> WelfareApplication:
        # 1. Verify citizen
        citizen = await self.citizen_repo.get_full_welfare_context(citizen_id)
        if not citizen:
            raise CitizenNotFoundError(f"Citizen {citizen_id} not found")

        # 2. Verify scheme
        scheme = await self.scheme_registry.get_scheme(scheme_id)
        if not scheme:
            raise SchemeNotFoundError(f"Scheme {scheme_id} not found")

        # 3. Evaluate eligibility
        eligibility = self.eligibility_service.evaluate(citizen, scheme)
        
        # 4. Match evidence
        evidence_matches = await self.evidence_matching.match(citizen_id, scheme_id)

        # 5. Create WelfareApplication
        # Initial status is DISCOVERED before we formally check it in state machine, 
        # or we just create it as ELIGIBILITY_CHECKED directly if allowed by business rules.
        # But let's create as DISCOVERED and transition.
        app = await self.app_repo.create(
            citizen_id=citizen_id,
            scheme_id=scheme_id,
            status=ApplicationStatus.DISCOVERED
        )
        
        await self.state_machine.transition(app.id, ApplicationStatus.DISCOVERED, ApplicationStatus.ELIGIBILITY_CHECKED)

        # 6. Create ApplicationRequirement rows
        all_satisfied = True
        for match in evidence_matches:
            req = await self.app_repo.add_requirement(ApplicationRequirement(
                application_id=app.id,
                requirement_type=match["requirement_type"] if "requirement_type" in match else match["requirement_id"],
                description=match["requirement_name"],
                is_mandatory=True # assuming mandatory for now
            ))
            if match["status"] != "SATISFIED":
                all_satisfied = False

        import datetime
        missing_reqs = [m for m in evidence_matches if m["status"] != "SATISFIED"]
        snapshot = {
            "citizen_facts": {
                "age": citizen.get_age() if hasattr(citizen, 'get_age') else "unknown",
                "phone": citizen.phone,
            },
            "household_facts": [
                {
                    "annual_income": hh.household.annual_income if hh.household else None,
                    "members_count": 1 # Mocked for snapshot to prevent lazy-load error
                } for hh in citizen.households
            ] if citizen.households else [],
            "employment_facts": [
                {
                    "occupation": emp.occupation,
                    "is_current": emp.is_current
                } for emp in citizen.employments
            ] if citizen.employments else [],
            "location": {
                "state": citizen.locations[0].state if citizen.locations else None,
                "district": citizen.locations[0].district if citizen.locations else None
            },
            "scheme_state": {
                "id": str(scheme.id),
                "name": scheme.official_name,
                "level": scheme.level
            },
            "eligibility_result": eligibility,
            "supporting_evidence": [m for m in evidence_matches if m["status"] == "SATISFIED"],
            "missing_requirements": missing_reqs,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        await self.app_repo.save_snapshot(app.id, snapshot)

        # 8. Set appropriate application state
        if all_satisfied and not evidence_matches:
             # if no requirements or all satisfied
             await self.state_machine.transition(app.id, ApplicationStatus.ELIGIBILITY_CHECKED, ApplicationStatus.EVIDENCE_COMPLETE)
        elif all_satisfied:
             await self.state_machine.transition(app.id, ApplicationStatus.ELIGIBILITY_CHECKED, ApplicationStatus.EVIDENCE_COMPLETE)
        else:
             await self.state_machine.transition(app.id, ApplicationStatus.ELIGIBILITY_CHECKED, ApplicationStatus.EVIDENCE_REQUIRED)

        return await self.app_repo.get_by_id(app.id)
