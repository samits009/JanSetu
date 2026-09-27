import hashlib
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.ingestion.models import SchemeExtractionResult
from app.models.scheme import Scheme, SchemeVersion, SchemeEligibilityRule, SchemeSource
from app.domain.enums import VerificationStatus

class PolicyCompiler:
    """
    Takes a validated extraction result and compiles it into the database schema.
    Creates a new SchemeVersion if there are material changes.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    def _compute_hash(self, extracted: SchemeExtractionResult) -> str:
        # Sort and dump to create a stable hash of the material policy
        data = extracted.model_dump()
        # Remove volatile fields that don't constitute a policy change
        data.pop('confidence_score', None)
        data.pop('needs_human_review', None)
        
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    async def compile(self, extracted: SchemeExtractionResult, source: SchemeSource, status: VerificationStatus) -> Scheme:
        content_hash = self._compute_hash(extracted)
        
        # Check if scheme already exists (using official_name as a naive identifier for now)
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        stmt = select(Scheme).where(Scheme.official_name == extracted.official_name).options(
            selectinload(Scheme.current_version)
        )
        result = await self.session.execute(stmt)
        scheme = result.scalars().first()

        if scheme:
            if scheme.current_version and scheme.current_version.content_hash == content_hash:
                # No material change
                return scheme
            
            # Need a new version
            version_number = (scheme.current_version.version_number + 1) if scheme.current_version else 1
        else:
            # Create new Scheme
            scheme = Scheme(
                official_name=extracted.official_name,
                category=extracted.category,
                description=extracted.description,
                state=extracted.jurisdictions[0].state if extracted.jurisdictions else None,
                level=extracted.jurisdictions[0].level if extracted.jurisdictions else "CENTRAL"
            )
            self.session.add(scheme)
            await self.session.flush()
            version_number = 1

        # Create new SchemeVersion
        req_defs = [req.model_dump() for req in extracted.requirements]
        
        new_version = SchemeVersion(
            scheme_id=scheme.id,
            version_number=version_number,
            source_id=source.id,
            verification_status=status,
            content_hash=content_hash,
            published_at=datetime.utcnow(),
            requirement_definitions=req_defs
        )
        self.session.add(new_version)
        await self.session.flush()

        # Add rules to this version
        for rule_data in extracted.rules:
            rule = SchemeEligibilityRule(
                scheme_id=scheme.id,
                version_id=new_version.id,
                rule_type=rule_data.rule_type,
                operator=rule_data.operator,
                value=rule_data.value
            )
            self.session.add(rule)

        # Update Scheme pointer only after successful validation/publication
        if status in (VerificationStatus.VERIFIED, VerificationStatus.DEMO):
            scheme.current_version_id = new_version.id
            scheme.current_version = new_version
        await self.session.flush()
        
        return scheme
