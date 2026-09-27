from typing import Any
from app.repositories.application import ApplicationRepository, ConsentRepository
from app.exceptions import ConsentRequiredError
from app.models.audit import Consent

class ConsentService:
    def __init__(self, consent_repo: ConsentRepository):
        self.consent_repo = consent_repo

    async def request(self, citizen_id: Any, action: str, application_id: Any = None) -> Consent:
        # In a real system, this would trigger an OTP or biometric flow
        # For now, we create a pending consent record
        return await self.consent_repo.create(
            citizen_id=citizen_id,
            action=action,
            application_id=application_id,
            purpose=action,
            is_granted=False
        )

    async def grant(self, consent_id: Any) -> bool:
        consent = await self.consent_repo.get_by_id(consent_id)
        if not consent:
            return False
        await self.consent_repo.update(consent, is_granted=True)
        return True

    async def revoke(self, consent_id: Any) -> bool:
        consent = await self.consent_repo.get_by_id(consent_id)
        if not consent:
            return False
        await self.consent_repo.update(consent, is_granted=False)
        return True

    async def check(self, citizen_id: Any, action: str, application_id: Any = None) -> None:
        consent = await self.consent_repo.find_valid_consent(citizen_id, action, application_id)
        if not consent:
            raise ConsentRequiredError(f"Valid consent not found for {action}")
