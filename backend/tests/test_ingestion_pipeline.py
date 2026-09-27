import pytest
import os
import json
from app.ingestion.pipeline import IngestionPipeline
from app.models.scheme import SchemeSource, Scheme, SchemeVersion, SchemeEligibilityRule
from app.domain.enums import SourceType, VerificationStatus

@pytest.mark.asyncio
async def test_full_pipeline_end_to_end(db_session):
    # Ensure fixture exists
    fixture_dir = os.path.join(os.path.dirname(__file__), "..", "app", "ingestion", "fixtures", "schemes")
    
    # 1. Create Source
    source = SchemeSource(
        authority="UP Labour Department",
        source_url="bocw_up.json",
        source_type=SourceType.FIXTURE
    )
    db_session.add(source)
    await db_session.flush()

    # 2. Run Pipeline
    pipeline = IngestionPipeline(db_session, fixture_dir)
    scheme = await pipeline.ingest_source(source)

    # 3. Verify Contract Outputs (Re-fetch to ensure relationships are loaded for sync access in tests)
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    stmt = select(Scheme).where(Scheme.id == scheme.id).options(
        selectinload(Scheme.current_version).selectinload(SchemeVersion.rules)
    )
    result = await db_session.execute(stmt)
    scheme_refetched = result.scalars().first()

    assert scheme_refetched.official_name == "UP BOCW"
    assert scheme_refetched.category == "EMPLOYMENT"
    
    # Validation status for FIXTURE should be DEMO
    assert scheme_refetched.current_version.verification_status == VerificationStatus.DEMO
    
    # Version checks
    assert scheme_refetched.current_version.version_number == 1
    assert len(scheme_refetched.current_version.rules) == 2
    
    # Data was normalized/extracted
    occ_rule = next(r for r in scheme_refetched.current_version.rules if r.rule_type == "OCCUPATION")
    assert occ_rule.value == "construction_worker"

@pytest.mark.asyncio
async def test_invalid_source_pipeline(db_session):
    fixture_dir = os.path.join(os.path.dirname(__file__), "..", "app", "ingestion", "fixtures", "schemes")
    pipeline = IngestionPipeline(db_session, fixture_dir)
    
    source = SchemeSource(
        authority="Unknown",
        source_url="does_not_exist.json",
        source_type=SourceType.FIXTURE
    )
    db_session.add(source)
    await db_session.flush()

    with pytest.raises(FileNotFoundError):
        await pipeline.ingest_source(source)
