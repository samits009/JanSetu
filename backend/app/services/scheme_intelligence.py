"""
SchemeIntelligenceService
===========================
Orchestrates scheme refresh, review, and publish lifecycle.

CRITICAL INVARIANTS:
  - Only PUBLISH may update Scheme.current_version_id
  - REFRESH, APPROVE, REJECT, MARK-NEEDS-REVIEW must NOT touch current_version_id
  - PUBLISH must be transactional: if it fails, current_version_id stays unchanged
  - REJECTED versions can never be published
"""
import os
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.scheme import Scheme, SchemeVersion
from app.domain.enums import VerificationStatus
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.models import SchemeExtractionResult
from app.ingestion.extractor import DeterministicExtractor
from app.ingestion.parser import TextParser
from app.ingestion.normalizer import Normalizer
from app.ingestion.validator import Validator
from app.ingestion.policy_compiler import PolicyCompiler
from app.services.scheme_audit import (
    SchemeAuditService,
    SCHEME_REFRESH_REQUESTED, SCHEME_VERSION_CREATED, SCHEME_VERSION_REVIEWED,
    SCHEME_VERSION_APPROVED, SCHEME_VERSION_REJECTED, SCHEME_VERSION_PUBLISHED,
    SCHEME_VERSION_PUBLISH_FAILED
)
from app.schemas.scheme import SchemeRefreshResponse, SchemeReviewResponse


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "ingestion", "fixtures", "schemes")

# Statuses that are eligible for publication
PUBLISHABLE_STATUSES = {VerificationStatus.DEMO, VerificationStatus.VERIFIED}


class SchemeIntelligenceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.audit = SchemeAuditService(session)
        self.compiler = PolicyCompiler(session)
        self.parser = TextParser()
        self.extractor = DeterministicExtractor()
        self.normalizer = Normalizer()
        self.validator = Validator()

    async def _get_scheme(self, scheme_id: UUID) -> Optional[Scheme]:
        stmt = select(Scheme).where(Scheme.id == scheme_id).options(
            selectinload(Scheme.current_version).selectinload(SchemeVersion.rules)
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def _get_version(self, version_id: UUID) -> Optional[SchemeVersion]:
        stmt = select(SchemeVersion).where(SchemeVersion.id == version_id).options(
            selectinload(SchemeVersion.rules),
            selectinload(SchemeVersion.benefits),
            selectinload(SchemeVersion.portability_rules),
            selectinload(SchemeVersion.renewal_rules),
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def refresh(self, scheme_id: UUID, actor: str) -> SchemeRefreshResponse:
        """
        Trigger a re-ingestion of the scheme from its source.
        MUST NOT modify current_version_id. Returns a candidate version if material change detected.
        """
        scheme = await self._get_scheme(scheme_id)
        if not scheme:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Scheme not found")

        await self.audit.record(
            actor=actor,
            action=SCHEME_REFRESH_REQUESTED,
            scheme_id=scheme_id,
        )

        # Get primary source for this scheme
        if not scheme.current_version or not scheme.current_version.source_id:
            return SchemeRefreshResponse(
                scheme_id=scheme_id,
                material_change=False,
                message="No source configured for refresh. Skipping."
            )

        from app.models.scheme import SchemeSource
        from sqlalchemy import select as sa_select
        source_stmt = sa_select(SchemeSource).where(SchemeSource.id == scheme.current_version.source_id)
        source = (await self.session.execute(source_stmt)).scalars().first()
        if not source:
            return SchemeRefreshResponse(
                scheme_id=scheme_id,
                material_change=False,
                message="Source record not found. Skipping."
            )

        # Run pipeline — compiler won't update current_version_id unless explicitly published
        from app.ingestion.fetcher import LocalFixtureFetcher
        fetcher = LocalFixtureFetcher(FIXTURE_DIR)
        raw = await fetcher.fetch(source.source_url)
        clean = self.parser.parse(raw)
        extracted = await self.extractor.extract(clean)
        normalized = self.normalizer.normalize(extracted)
        status = self.validator.validate(normalized)

        import hashlib, json
        data = extracted.model_dump()
        data.pop('confidence_score', None)
        data.pop('needs_human_review', None)
        content_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

        if scheme.current_version and scheme.current_version.content_hash == content_hash:
            return SchemeRefreshResponse(
                scheme_id=scheme_id,
                material_change=False,
                message="No material change detected. Current version unchanged."
            )

        # Material change — create candidate version WITHOUT updating current_version_id
        version_number = (scheme.current_version.version_number + 1) if scheme.current_version else 1
        from datetime import datetime
        from app.models.scheme import SchemeEligibilityRule
        req_defs = [req.model_dump() for req in extracted.requirements]
        candidate = SchemeVersion(
            scheme_id=scheme.id,
            version_number=version_number,
            source_id=source.id,
            verification_status=status,
            content_hash=content_hash,
            published_at=None,  # Not published yet
            requirement_definitions=req_defs
        )
        self.session.add(candidate)
        await self.session.flush()

        for rule_data in extracted.rules:
            rule = SchemeEligibilityRule(
                scheme_id=scheme.id,
                version_id=candidate.id,
                rule_type=rule_data.rule_type,
                operator=rule_data.operator,
                value=rule_data.value
            )
            self.session.add(rule)
        await self.session.flush()

        # IMPORTANT: Do NOT update scheme.current_version_id here
        await self.audit.record(
            actor=actor,
            action=SCHEME_VERSION_CREATED,
            scheme_id=scheme_id,
            version_id=candidate.id,
            details={"version_number": version_number, "verification_status": status.value}
        )

        return SchemeRefreshResponse(
            scheme_id=scheme_id,
            material_change=True,
            candidate_version_id=candidate.id,
            candidate_version_number=version_number,
            verification_status=status,
            message=f"Material change detected. Candidate Version {version_number} created. Requires review and publication."
        )

    async def approve_version(self, version_id: UUID, actor: str) -> SchemeReviewResponse:
        """Mark a candidate version as approved for publication. Does NOT publish."""
        version = await self._get_version(version_id)
        if not version:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Version not found")
        if version.verification_status == VerificationStatus.REJECTED:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Cannot approve a REJECTED version")

        version.verification_status = VerificationStatus.VERIFIED
        await self.session.flush()

        await self.audit.record(
            actor=actor, action=SCHEME_VERSION_APPROVED,
            scheme_id=version.scheme_id, version_id=version_id,
        )
        return SchemeReviewResponse(
            version_id=version_id,
            verification_status=VerificationStatus.VERIFIED,
            message="Version approved. Ready for publication."
        )

    async def reject_version(self, version_id: UUID, actor: str) -> SchemeReviewResponse:
        """Reject a candidate version. Does NOT alter current_version_id."""
        version = await self._get_version(version_id)
        if not version:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Version not found")

        version.verification_status = VerificationStatus.REJECTED
        await self.session.flush()

        await self.audit.record(
            actor=actor, action=SCHEME_VERSION_REJECTED,
            scheme_id=version.scheme_id, version_id=version_id,
        )
        return SchemeReviewResponse(
            version_id=version_id,
            verification_status=VerificationStatus.REJECTED,
            message="Version rejected. Live version unchanged."
        )

    async def mark_needs_review(self, version_id: UUID, actor: str) -> SchemeReviewResponse:
        """Mark a version as needing human review. Does NOT alter current_version_id."""
        version = await self._get_version(version_id)
        if not version:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Version not found")
        if version.verification_status == VerificationStatus.REJECTED:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Cannot re-review a REJECTED version")

        version.verification_status = VerificationStatus.NEEDS_REVIEW
        await self.session.flush()

        await self.audit.record(
            actor=actor, action=SCHEME_VERSION_REVIEWED,
            scheme_id=version.scheme_id, version_id=version_id,
            details={"new_status": "NEEDS_REVIEW"}
        )
        return SchemeReviewResponse(
            version_id=version_id,
            verification_status=VerificationStatus.NEEDS_REVIEW,
            message="Version marked as NEEDS_REVIEW. Live version unchanged."
        )

    async def publish_version(self, version_id: UUID, actor: str) -> SchemeReviewResponse:
        """
        Atomically promote a version to current.
        Only PUBLISHABLE_STATUSES are allowed.
        REJECTED versions cannot be published.
        current_version_id changes ONLY here.
        """
        version = await self._get_version(version_id)
        if not version:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Version not found")

        if version.verification_status not in PUBLISHABLE_STATUSES:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Version status '{version.verification_status}' is not publishable. "
                       f"Only {[s.value for s in PUBLISHABLE_STATUSES]} can be published."
            )

        # Get the scheme
        scheme_stmt = select(Scheme).where(Scheme.id == version.scheme_id)
        scheme = (await self.session.execute(scheme_stmt)).scalars().first()
        if not scheme:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Scheme not found")

        try:
            from datetime import datetime
            # ATOMIC: this is the ONLY place current_version_id may change
            scheme.current_version_id = version_id
            version.published_at = datetime.utcnow()
            await self.session.flush()

            await self.audit.record(
                actor=actor, action=SCHEME_VERSION_PUBLISHED,
                scheme_id=scheme.id, version_id=version_id,
                result="SUCCESS",
                details={"previous_version_id": str(scheme.current_version_id)}
            )

            return SchemeReviewResponse(
                version_id=version_id,
                verification_status=version.verification_status,
                message=f"Version {version.version_number} is now the live published version."
            )
        except Exception as e:
            await self.audit.record(
                actor=actor, action=SCHEME_VERSION_PUBLISH_FAILED,
                scheme_id=scheme.id if scheme else None,
                version_id=version_id,
                result="FAILED",
                details={"error": str(e)}
            )
            raise
