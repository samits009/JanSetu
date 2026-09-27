from typing import Any, Dict
from app.models.application import WelfareApplication
from app.repositories.application import ApplicationRepository
from app.services.application_state_machine import ApplicationStateMachine
from app.domain.enums import ApplicationStatus
from app.services.evidence_matching import EvidenceMatchingService
from app.services.consent import ConsentService

class ApplicationRecoveryService:
    def __init__(
        self, 
        app_repo: ApplicationRepository,
        state_machine: ApplicationStateMachine,
        evidence_matching: EvidenceMatchingService,
        consent_service: ConsentService
    ):
        self.app_repo = app_repo
        self.state_machine = state_machine
        self.evidence_matching = evidence_matching
        self.consent_service = consent_service

    async def recover(self, application_id: Any) -> Dict[str, Any]:
        app = await self.app_repo.get_recovery_context(application_id)
        if not app:
            raise ValueError("Application not found")

        # Must be in REJECTED or REQUIRES_EVIDENCE to transition to RECOVERY_READY
        if app.status in [ApplicationStatus.REJECTED, ApplicationStatus.REQUIRES_EVIDENCE]:
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.RECOVERY_READY)
        elif app.status != ApplicationStatus.RECOVERY_READY:
            raise ValueError("Application not in a recoverable state")
        
        # Identify failed requirements (simplified logic)
        # We'll just re-run evidence matching to see if any new evidence is available
        evidence_matches = await self.evidence_matching.match(app.citizen_id, app.scheme_id)
        
        recovery_plan = {
            "application_id": str(app.id),
            "failed_requirements": [],
            "found_alternatives": [],
            "missing_still": []
        }

        # Check which requirements are still missing
        for match in evidence_matches:
            if match["status"] == "SATISFIED":
                recovery_plan["found_alternatives"].append(match)
            else:
                recovery_plan["missing_still"].append(match)

        # If everything is satisfied now (e.g. user uploaded a document in between)
        if not recovery_plan["missing_still"]:
            # We are ready to resubmit, but need consent first
            pass

        return recovery_plan

    async def resubmit(self, application_id: Any) -> WelfareApplication:
        app = await self.app_repo.get_by_id(application_id)
        
        # Check for consent before resubmitting
        await self.consent_service.check(app.citizen_id, "APPLICATION_RESUBMISSION", app.id)

        await self.state_machine.transition(app.id, ApplicationStatus.RECOVERY_READY, ApplicationStatus.RESUBMITTED)
        return app
