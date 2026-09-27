from typing import List, Optional, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.scheme import Scheme, SchemeEligibilityRule, SchemeVersion
from app.models.application import Benefit, BenefitRisk
from app.repositories.base import BaseRepository

class SchemeRepository(BaseRepository[Scheme]):
    def __init__(self, session):
        super().__init__(Scheme, session)
        
    async def get_with_rules(self, scheme_id: Any) -> Optional[Scheme]:
        stmt = (
            select(Scheme)
            .options(selectinload(Scheme.current_version).selectinload(SchemeVersion.rules))
            .where(Scheme.id == scheme_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_with_rules(self) -> List[Scheme]:
        stmt = select(Scheme).options(
            selectinload(Scheme.current_version).selectinload(SchemeVersion.rules)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_ids(self, scheme_ids: List[Any]) -> List[Scheme]:
        if not scheme_ids:
            return []
        stmt = (
            select(Scheme)
            .options(selectinload(Scheme.current_version).selectinload(SchemeVersion.rules))
            .where(Scheme.id.in_(scheme_ids))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_verified(self) -> List[Scheme]:
        stmt = (
            select(Scheme)
            .join(Scheme.current_version)
            .options(
                selectinload(Scheme.current_version).selectinload(SchemeVersion.rules)
            )
            .where(
                SchemeVersion.verification_status.in_(["VERIFIED", "DEMO"])
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

        
    async def list_for_location(self, state: str) -> List[Scheme]:
        stmt = select(Scheme).where(
            (Scheme.level == 'CENTRAL') | (Scheme.state == state)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class BenefitRepository(BaseRepository[Benefit]):
    def __init__(self, session):
        super().__init__(Benefit, session)

    async def find_for_citizen(self, citizen_id: Any) -> List[Benefit]:
        stmt = (
            select(Benefit)
            .options(selectinload(Benefit.scheme))
            .where(Benefit.citizen_id == citizen_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_benefits(self, citizen_id: UUID) -> List[Benefit]:
        stmt = select(Benefit).where(Benefit.citizen_id == citizen_id, Benefit.status == "ACTIVE")
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class BenefitRiskRepository(BaseRepository[BenefitRisk]):
    def __init__(self, session):
        super().__init__(BenefitRisk, session)
