from typing import Any
from app.exceptions import InvalidApplicationTransitionError
from app.domain.enums import ApplicationStatus
from app.repositories.application import ApplicationRepository

class ApplicationStateMachine:
    def __init__(self, app_repo: ApplicationRepository):
        self.app_repo = app_repo
        
        self.valid_transitions = {
            ApplicationStatus.DISCOVERED: [ApplicationStatus.ELIGIBILITY_CHECKED],
            ApplicationStatus.ELIGIBILITY_CHECKED: [ApplicationStatus.EVIDENCE_REQUIRED, ApplicationStatus.EVIDENCE_COMPLETE],
            ApplicationStatus.EVIDENCE_COMPLETE: [ApplicationStatus.DRAFTED],
            ApplicationStatus.DRAFTED: [ApplicationStatus.AWAITING_CONSENT],
            ApplicationStatus.AWAITING_CONSENT: [ApplicationStatus.SUBMITTING],
            ApplicationStatus.SUBMITTING: [ApplicationStatus.SUBMITTED],
            ApplicationStatus.SUBMITTED: [ApplicationStatus.UNDER_REVIEW],
            ApplicationStatus.UNDER_REVIEW: [ApplicationStatus.APPROVED, ApplicationStatus.REQUIRES_EVIDENCE, ApplicationStatus.REJECTED],
            ApplicationStatus.REJECTED: [ApplicationStatus.RECOVERY_READY],
            ApplicationStatus.RECOVERY_READY: [ApplicationStatus.RESUBMITTED],
            ApplicationStatus.RESUBMITTED: [ApplicationStatus.UNDER_REVIEW],
            
            # Dead ends, or loops
            ApplicationStatus.REQUIRES_EVIDENCE: [ApplicationStatus.RECOVERY_READY],
            ApplicationStatus.APPROVED: [],
            ApplicationStatus.EVIDENCE_REQUIRED: [ApplicationStatus.EVIDENCE_COMPLETE]
        }

    async def transition(self, application_id: Any, current_status: ApplicationStatus, target_status: ApplicationStatus) -> bool:
        allowed = self.valid_transitions.get(current_status, [])
        if target_status not in allowed:
            raise InvalidApplicationTransitionError(f"Cannot transition from {current_status.name} to {target_status.name}")
        
        return await self.app_repo.update_status(application_id, target_status)
