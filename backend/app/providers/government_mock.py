from typing import Any
import uuid
from app.domain.enums import ApplicationStatus
from app.repositories.application import ApplicationRepository
from app.services.application_state_machine import ApplicationStateMachine

class GovernmentApplicationProvider:
    async def submit_application(self, application_id: Any) -> str:
        raise NotImplementedError

    async def get_application_status(self, application_id: Any) -> str:
        raise NotImplementedError

    async def resubmit_application(self, application_id: Any) -> str:
        raise NotImplementedError


class MockGovernmentApplicationProvider(GovernmentApplicationProvider):
    def __init__(self, app_repo: ApplicationRepository, state_machine: ApplicationStateMachine):
        self.app_repo = app_repo
        self.state_machine = state_machine

    async def submit_application(self, application_id: Any) -> str:
        app = await self.app_repo.get_by_id(application_id)
        if not app:
            raise ValueError("Application not found")
        
        gov_ref = f"MOCK-GOV-{uuid.uuid4().hex[:8].upper()}"
        
        # State machine will have been used to go to SUBMITTING before this,
        # but mock provider transitions to SUBMITTED
        await self.state_machine.transition(app.id, app.status, ApplicationStatus.SUBMITTED)
        await self.app_repo.record_provider_response(app.id, gov_ref)
        return gov_ref

    async def get_application_status(self, application_id: Any) -> str:
        app = await self.app_repo.get_by_id(application_id)
        return app.status.name if app else "UNKNOWN"

    async def simulate_government_action(self, application_id: Any, action: str, reason: str = None) -> None:
        """Deterministic way for tests to move state forward."""
        app = await self.app_repo.get_by_id(application_id)
        
        if action == "REVIEW":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.UNDER_REVIEW)
        elif action == "REQUIRE_EVIDENCE":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.REQUIRES_EVIDENCE)
            if reason:
                await self.app_repo.record_provider_response(app.id, app.government_reference_id, rejection_reason=reason)
        elif action == "APPROVE":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.APPROVED)
        elif action == "REJECT":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.REJECTED)
            if reason:
                await self.app_repo.record_provider_response(app.id, app.government_reference_id, rejection_reason=reason)

    async def resubmit_application(self, application_id: Any) -> str:
        # Assuming the caller already transitioned to RESUBMITTED,
        # Or this provider transitions it
        app = await self.app_repo.get_by_id(application_id)
        return app.government_reference_id or "UNKNOWN"
