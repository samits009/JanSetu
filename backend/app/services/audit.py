from typing import Any, Dict, Optional
from app.repositories.application import AuditRepository
from app.models.audit import AuditEvent

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def record(
        self, 
        citizen_id: Any, 
        actor: str, 
        action: str, 
        purpose: str, 
        result: str, 
        consent_id: Optional[Any] = None,
        application_id: Optional[Any] = None,
        safe_data: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        # We explicitly only store safe_data, which avoids raw documents/secrets
        return await self.audit_repo.create(
            citizen_id=citizen_id,
            actor=actor,
            action=action,
            result=result,
            consent_id=consent_id,
            application_id=application_id,
            data_used=safe_data
        )
