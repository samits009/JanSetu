import pytest
import datetime
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.repositories.citizen import CitizenRepository
from app.repositories.scheme import SchemeRepository
from app.repositories.evidence import DocumentRepository, EvidenceRepository
from app.models.citizen import Employment, Location
from app.models.scheme import SchemeVersion, SchemeEligibilityRule
from app.models.application import Benefit

@pytest.mark.asyncio
async def test_get_benefit_detail_api(db_session):
    cit_repo = CitizenRepository(db_session)
    scheme_repo = SchemeRepository(db_session)
    doc_repo = DocumentRepository(db_session)
    ev_repo = EvidenceRepository(db_session)

    # 1. Use seeded Ramesh citizen
    from app.db.seed import RAMESH_UUID
    citizen = await cit_repo.get_full_welfare_context(RAMESH_UUID)
    assert citizen is not None

    # 2. Create Scheme with versioned requirement definitions
    scheme = await scheme_repo.create(
        official_name="Delhi Construction Worker Assistance Custom",
        category="HOUSING",
        state="Delhi",
        level="STATE",
        benefit_amount=15000
    )
    version = SchemeVersion(
        scheme_id=scheme.id,
        version_number=1,
        verification_status="VERIFIED",
        requirement_definitions=[
            {"id": "req_occ", "type": "OCCUPATION", "name": "BOCW Registration Card"},
            {"id": "req_skill", "type": "SKILL_CERTIFICATE", "name": "Construction Skill Certificate"}
        ]

    )
    db_session.add(version)
    await db_session.flush()
    scheme.current_version_id = version.id

    rule = SchemeEligibilityRule(
        scheme_id=scheme.id,
        version_id=version.id,
        rule_type="OCCUPATION",
        operator="==",
        value="Construction Worker"
    )
    db_session.add(rule)


    # 3. Add Verified Document & Evidence for OCCUPATION, leave IDENTITY missing
    doc = await doc_repo.create(citizen_id=citizen.id, document_type="BOCW_CARD", verification_status="VERIFIED")
    await ev_repo.create(citizen_id=citizen.id, document_id=doc.id, evidence_type="OCCUPATION", data={"occupation": "construction_worker"})

    # 4. Create an active benefit entry
    benefit = Benefit(citizen_id=citizen.id, scheme_id=scheme.id, status="ACTIVE")
    db_session.add(benefit)
    await db_session.flush()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Authenticate via demo-login
        login_res = await client.post("/api/auth/demo-login")
        assert login_res.status_code == 200

        resp = await client.get(
            f"/api/benefits/{benefit.id}?citizen_id={citizen.id}"
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id"] == str(benefit.id)
        assert data["scheme_name"] == "Delhi Construction Worker Assistance Custom"
        assert data["eligibility_status"] == "ELIGIBLE"
        assert len(data["satisfied_requirements"]) >= 1
        assert any(r["type"] == "OCCUPATION" for r in data["satisfied_requirements"])
        assert len(data["missing_requirements"]) >= 1
        assert any(r["type"] == "SKILL_CERTIFICATE" for r in data["missing_requirements"])

        assert len(data["supporting_evidence"]) >= 1
        assert any(e["document_type"] == "BOCW_CARD" for e in data["supporting_evidence"])

@pytest.mark.asyncio
async def test_get_benefit_detail_by_scheme_id_opportunity(db_session):
    cit_repo = CitizenRepository(db_session)
    scheme_repo = SchemeRepository(db_session)

    from app.db.seed import RAMESH_UUID
    citizen = await cit_repo.get_full_welfare_context(RAMESH_UUID)
    assert citizen is not None

    # Scheme without existing Benefit row (new opportunity)
    scheme = await scheme_repo.create(
        official_name="National Solar Rooftop Subsidy",
        category="HOUSING",
        state="ALL",
        level="CENTRAL",
        benefit_amount=30000
    )
    version = SchemeVersion(
        scheme_id=scheme.id,
        version_number=1,
        verification_status="VERIFIED",
        requirement_definitions=[
            {"id": "req_electricity", "type": "ELECTRICITY_BILL", "name": "Latest Electricity Bill"}
        ]
    )
    db_session.add(version)
    await db_session.flush()
    scheme.current_version_id = version.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/auth/demo-login")

        # Query using scheme.id instead of benefit.id
        resp = await client.get(
            f"/api/benefits/{scheme.id}?citizen_id={citizen.id}"
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id"] == str(scheme.id)
        assert data["scheme_id"] == str(scheme.id)
        assert data["scheme_name"] == "National Solar Rooftop Subsidy"
        assert data["status"] == "NEW_OPPORTUNITY"
        assert len(data["missing_requirements"]) == 1
        assert data["missing_requirements"][0]["type"] == "ELECTRICITY_BILL"


