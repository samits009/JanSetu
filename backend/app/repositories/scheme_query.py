from typing import List, Optional, Any, Tuple
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.scheme import (
    Scheme, SchemeVersion, SchemeEligibilityRule,
    SchemeSource, SchemeBenefit
)
from app.domain.enums import VerificationStatus, SchemeCategory


MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20


class SchemeQueryRepository:
    """
    Read-optimized repository for scheme intelligence queries.
    Supports pagination and filtering. Does NOT own write operations.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_schemes(
        self,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        state: Optional[str] = None,
        category: Optional[str] = None,
        verification_status: Optional[str] = None,
    ) -> Tuple[List[Scheme], int]:
        """Returns (items, total_count)."""
        page_size = min(page_size, MAX_PAGE_SIZE)
        offset = (page - 1) * page_size

        stmt = select(Scheme).options(
            selectinload(Scheme.current_version),
            selectinload(Scheme.translations)
        )

        if search:
            stmt = stmt.where(Scheme.official_name.ilike(f"%{search}%"))
        if jurisdiction:
            stmt = stmt.where(Scheme.level == jurisdiction.upper())
        if state:
            stmt = stmt.where(
                or_(Scheme.state == state, Scheme.level == "CENTRAL")
            )
        if category:
            stmt = stmt.where(Scheme.category == category.upper())
        if verification_status:
            stmt = stmt.join(Scheme.current_version).where(
                SchemeVersion.verification_status == verification_status.upper()
            )

        # Count and paginate the same filtered relation.
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.offset(offset).limit(page_size).order_by(Scheme.official_name)
        results = (await self.session.execute(stmt)).scalars().all()

        return list(results), total

    async def get_scheme_detail(self, scheme_id: UUID) -> Optional[Scheme]:
        stmt = select(Scheme).where(Scheme.id == scheme_id).options(
            selectinload(Scheme.translations),
            selectinload(Scheme.current_version).options(
                selectinload(SchemeVersion.rules),
                selectinload(SchemeVersion.benefits),
                selectinload(SchemeVersion.source),
            )
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def get_scheme_versions(self, scheme_id: UUID) -> List[SchemeVersion]:
        stmt = (
            select(SchemeVersion)
            .where(SchemeVersion.scheme_id == scheme_id)
            .options(
                selectinload(SchemeVersion.rules),
                selectinload(SchemeVersion.benefits),
                selectinload(SchemeVersion.source),
            )
            .order_by(SchemeVersion.version_number.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_version(self, version_id: UUID) -> Optional[SchemeVersion]:
        stmt = (
            select(SchemeVersion)
            .where(SchemeVersion.id == version_id)
            .options(
                selectinload(SchemeVersion.rules),
                selectinload(SchemeVersion.benefits),
                selectinload(SchemeVersion.source),
            )
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def get_pending_review(self) -> List[SchemeVersion]:
        stmt = (
            select(SchemeVersion)
            .where(SchemeVersion.verification_status == VerificationStatus.NEEDS_REVIEW)
            .options(
                selectinload(SchemeVersion.source),
                selectinload(SchemeVersion.rules),
                selectinload(SchemeVersion.benefits),
            )
            .order_by(SchemeVersion.created_at.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_sources(self) -> List[SchemeSource]:
        stmt = select(SchemeSource).order_by(SchemeSource.authority)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_source(self, source_id: UUID) -> Optional[SchemeSource]:
        stmt = select(SchemeSource).where(SchemeSource.id == source_id)
        return (await self.session.execute(stmt)).scalars().first()

    async def get_scheme_rules(self, scheme_id: UUID) -> List[SchemeEligibilityRule]:
        """Returns rules from the current published version."""
        scheme = await self.get_scheme_detail(scheme_id)
        if not scheme or not scheme.current_version:
            return []
        return scheme.current_version.rules

    async def get_scheme_benefits(self, scheme_id: UUID) -> List[SchemeBenefit]:
        scheme = await self.get_scheme_detail(scheme_id)
        if not scheme or not scheme.current_version:
            return []
        return scheme.current_version.benefits
