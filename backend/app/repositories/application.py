from typing import Optional, Any, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.application import WelfareApplication, ApplicationRequirement
from app.models.audit import Consent, AuditEvent, AgentAction
from app.repositories.base import BaseRepository
from app.domain.enums import ApplicationStatus


class ApplicationRepository(BaseRepository[WelfareApplication]):
    def __init__(self, session: AsyncSession):
        super().__init__(WelfareApplication, session)

    async def get_with_requirements(self, application_id: Any) -> Optional[WelfareApplication]:
        stmt = (
            select(WelfareApplication)
            .options(
                selectinload(WelfareApplication.requirements).selectinload(ApplicationRequirement.evidence_links),
                selectinload(WelfareApplication.scheme)
            )
            .where(WelfareApplication.id == application_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_for_citizen(self, citizen_id: Any) -> List[WelfareApplication]:
        stmt = (
            select(WelfareApplication)
            .options(
                selectinload(WelfareApplication.scheme)
            )
            .where(WelfareApplication.citizen_id == citizen_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, application_id: Any, status: ApplicationStatus) -> bool:
        stmt = (
            update(WelfareApplication)
            .where(WelfareApplication.id == application_id)
            .values(status=status)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def add_requirement(self, requirement: ApplicationRequirement) -> ApplicationRequirement:
        self.session.add(requirement)
        await self.session.flush()
        return requirement

    async def save_snapshot(self, application_id: Any, snapshot: Dict[str, Any]) -> bool:
        stmt = (
            update(WelfareApplication)
            .where(WelfareApplication.id == application_id)
            .values(snapshot=snapshot)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def get_recovery_context(self, application_id: Any) -> Optional[WelfareApplication]:
        # Same as get_with_requirements but makes intent clear
        return await self.get_with_requirements(application_id)

    async def get_timeline(self, application_id: Any) -> List[AuditEvent]:
        stmt = (
            select(AuditEvent)
            .where(AuditEvent.application_id == application_id)
            .order_by(AuditEvent.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def record_provider_response(self, application_id: Any, gov_ref: str, rejection_reason: Optional[str] = None) -> bool:
        values = {"government_reference_id": gov_ref}
        if rejection_reason is not None:
            values["rejection_reason"] = rejection_reason
            
        stmt = (
            update(WelfareApplication)
            .where(WelfareApplication.id == application_id)
            .values(**values)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0


class ConsentRepository(BaseRepository[Consent]):
    def __init__(self, session: AsyncSession):
        super().__init__(Consent, session)

    async def find_valid_consent(self, citizen_id: Any, action: Any, application_id: Optional[Any] = None) -> Optional[Consent]:
        stmt = select(Consent).where(
            Consent.citizen_id == citizen_id,
            Consent.action == action,
            Consent.is_granted == True
        )
        if application_id:
            stmt = stmt.where(Consent.application_id == application_id)
            
        result = await self.session.execute(stmt)
        return result.scalars().first()


class AuditRepository(BaseRepository[AuditEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditEvent, session)

class AgentActionRepository(BaseRepository[AgentAction]):
    def __init__(self, session: AsyncSession):
        super().__init__(AgentAction, session)
