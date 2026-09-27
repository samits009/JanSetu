from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.citizen import Citizen, Household, Employment, Location, HouseholdMember
from app.models.application import Benefit, WelfareApplication
from app.repositories.base import BaseRepository


class CitizenRepository(BaseRepository[Citizen]):
    def __init__(self, session: AsyncSession):
        super().__init__(Citizen, session)

    async def get_with_household(self, citizen_id: Any) -> Optional[Citizen]:
        stmt = (
            select(Citizen)
            .options(
                selectinload(Citizen.households).selectinload(HouseholdMember.household)
            )
            .where(Citizen.id == citizen_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_employment(self, citizen_id: Any) -> Optional[Citizen]:
        stmt = (
            select(Citizen)
            .options(selectinload(Citizen.employments))
            .where(Citizen.id == citizen_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_full_welfare_context(self, citizen_id: Any) -> Optional[Citizen]:
        stmt = (
            select(Citizen)
            .options(
                selectinload(Citizen.households).selectinload(HouseholdMember.household),
                selectinload(Citizen.employments),
                selectinload(Citizen.locations),
                selectinload(Citizen.documents),
                selectinload(Citizen.benefits).options(
                    selectinload(Benefit.risks),
                    selectinload(Benefit.scheme),
                ),
                selectinload(Citizen.applications).selectinload(WelfareApplication.scheme)
            )
            .where(Citizen.id == citizen_id)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class HouseholdRepository(BaseRepository[Household]):
    def __init__(self, session: AsyncSession):
        super().__init__(Household, session)


class EmploymentRepository(BaseRepository[Employment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Employment, session)


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: AsyncSession):
        super().__init__(Location, session)
