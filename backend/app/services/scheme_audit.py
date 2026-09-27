from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scheme_audit import SchemeAuditEvent


# Scheme Intelligence Audit Event Constants
SCHEME_REFRESH_REQUESTED = "SCHEME_REFRESH_REQUESTED"
SCHEME_VERSION_CREATED = "SCHEME_VERSION_CREATED"
SCHEME_VERSION_REVIEWED = "SCHEME_VERSION_REVIEWED"
SCHEME_VERSION_APPROVED = "SCHEME_VERSION_APPROVED"
SCHEME_VERSION_REJECTED = "SCHEME_VERSION_REJECTED"
SCHEME_VERSION_PUBLISHED = "SCHEME_VERSION_PUBLISHED"
SCHEME_VERSION_PUBLISH_FAILED = "SCHEME_VERSION_PUBLISH_FAILED"


class SchemeAuditService:
    """
    Records audit events for Scheme Intelligence operations.
    NEVER stores credentials, secrets, or internal file paths.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record(
        self,
        actor: str,
        action: str,
        scheme_id: Optional[UUID] = None,
        version_id: Optional[UUID] = None,
        result: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None
    ) -> SchemeAuditEvent:
        event = SchemeAuditEvent(
            actor=actor,
            action=action,
            scheme_id=scheme_id,
            version_id=version_id,
            result=result,
            details=details
        )
        self.session.add(event)
        await self.session.flush()
        return event
