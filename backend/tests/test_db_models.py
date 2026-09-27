import pytest
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Citizen, Household, Document, Scheme, Evidence

@pytest.mark.asyncio
async def test_citizen_household_relationship(db_session: AsyncSession):
    citizen = Citizen(name="Test Citizen", phone="1111111111")
    db_session.add(citizen)
    await db_session.flush()
    
    household = Household(head_citizen_id=citizen.id, annual_income=50000)
    db_session.add(household)
    await db_session.flush()
    
    # Verify foreign key constraint and linkage
    assert household.head_citizen_id == citizen.id
        
@pytest.mark.asyncio
async def test_evidence_graph(db_session: AsyncSession):
    citizen = Citizen(name="Test Citizen", phone="2222222222")
    db_session.add(citizen)
    await db_session.flush()
    
    doc = Document(citizen_id=citizen.id, document_type="AADHAAR", verification_status="VERIFIED")
    db_session.add(doc)
    await db_session.flush()
    
    evidence = Evidence(
        citizen_id=citizen.id,
        document_id=doc.id,
        evidence_type="IDENTITY",
        data={"verified_name": "Test Citizen"}
    )
    db_session.add(evidence)
    await db_session.flush()
    
    assert evidence.document_id == doc.id
    assert evidence.citizen_id == citizen.id
    assert evidence.data["verified_name"] == "Test Citizen"

