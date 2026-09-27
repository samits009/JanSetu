import pytest
from app.ingestion.policy_compiler import PolicyCompiler
from app.ingestion.models import SchemeExtractionResult, ExtractedRule, ExtractedJurisdiction
from app.domain.enums import VerificationStatus, SourceType, PortabilityState
from app.models.scheme import SchemeSource, Scheme, SchemeVersion

@pytest.mark.asyncio
async def test_policy_compiler_versioning(db_session):
    compiler = PolicyCompiler(db_session)
    
    # 1. Setup source
    source = SchemeSource(authority="Test Auth", source_url="test.json", source_type=SourceType.FIXTURE)
    db_session.add(source)
    await db_session.flush()

    # 2. Extract Scenario A (Initial)
    extracted1 = SchemeExtractionResult(
        official_name="Versioned Scheme",
        category="EMPLOYMENT",
        description="V1",
        rules=[ExtractedRule(rule_type="AGE", operator=">=", value=18)],
        jurisdictions=[ExtractedJurisdiction(level="CENTRAL")]
    )
    
    scheme1 = await compiler.compile(extracted1, source, VerificationStatus.DEMO)
    
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    stmt1 = select(Scheme).where(Scheme.id == scheme1.id).options(selectinload(Scheme.current_version))
    scheme1_refetched = (await db_session.execute(stmt1)).scalars().first()
    
    assert scheme1_refetched.current_version.version_number == 1
    assert scheme1_refetched.current_version.verification_status == VerificationStatus.DEMO
    
    v1_id = scheme1_refetched.current_version_id
    
    # 3. Extract Scenario A again (Same content) -> No new version
    scheme1_dup = await compiler.compile(extracted1, source, VerificationStatus.DEMO)
    assert scheme1_dup.current_version_id == v1_id
    
    stmt_dup = select(Scheme).where(Scheme.id == scheme1_dup.id).options(selectinload(Scheme.current_version))
    scheme1_dup_refetched = (await db_session.execute(stmt_dup)).scalars().first()
    assert scheme1_dup_refetched.current_version.version_number == 1

    # 4. Extract Scenario B (Material change) -> New version
    extracted2 = SchemeExtractionResult(
        official_name="Versioned Scheme",
        category="EMPLOYMENT",
        description="V2",
        rules=[ExtractedRule(rule_type="AGE", operator=">=", value=21)], # Changed rule
        jurisdictions=[ExtractedJurisdiction(level="CENTRAL")]
    )
    
    scheme2 = await compiler.compile(extracted2, source, VerificationStatus.DEMO)
    assert scheme2.current_version_id != v1_id
    
    stmt2 = select(Scheme).where(Scheme.id == scheme2.id).options(selectinload(Scheme.current_version))
    scheme2_refetched = (await db_session.execute(stmt2)).scalars().first()
    assert scheme2_refetched.current_version.version_number == 2
    
    # 5. Verify old version remains
    from sqlalchemy import select
    v1 = await db_session.execute(select(SchemeVersion).where(SchemeVersion.id == v1_id))
    assert v1.scalar_one_or_none() is not None

@pytest.mark.asyncio
async def test_failed_publication(db_session):
    compiler = PolicyCompiler(db_session)
    
    # Setup source
    source = SchemeSource(authority="Test Auth", source_url="test.json", source_type=SourceType.FIXTURE)
    db_session.add(source)
    await db_session.flush()

    extracted = SchemeExtractionResult(
        official_name="Failed Scheme",
        category="EMPLOYMENT",
        description="Init",
        rules=[],
        jurisdictions=[]
    )
    
    # Compile with REJECTED status
    scheme = await compiler.compile(extracted, source, VerificationStatus.REJECTED)
    
    # Validation failure / rejection means current_version_id is NOT updated
    assert scheme.current_version_id is None
    
    # The rejected version is persisted for audit, but not live
    from sqlalchemy import select
    versions = await db_session.execute(select(SchemeVersion).where(SchemeVersion.scheme_id == scheme.id))
    v_list = versions.scalars().all()
    assert len(v_list) == 1
    assert v_list[0].verification_status == VerificationStatus.REJECTED
