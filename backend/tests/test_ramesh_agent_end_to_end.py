import pytest
import uuid
import datetime
from app.agents.providers.mock import MockAIProvider
from app.agents.welfare_agent import WelfareAgent
from app.api.endpoints.agent import get_agent_context

from app.models.citizen import Household, HouseholdMember, Employment, Location
from app.models.scheme import Scheme, SchemeEligibilityRule, SchemeVersion
from app.models.application import Benefit
from app.models.audit import Consent
from app.domain.enums import ApplicationStatus
from sqlalchemy import text

@pytest.mark.asyncio
async def test_ramesh_agent_end_to_end(db_session):
    ctx = await get_agent_context(uuid.uuid4(), db_session)
    # 1. Load Ramesh
    dob = datetime.date.today() - datetime.timedelta(days=32 * 365)
    ramesh = await ctx.cit_repo.create(name="Ramesh Kumar", dob=dob)
    
    # Update ctx to point to Ramesh
    ctx.citizen_id = ramesh.id

    hh = await ctx.cit_repo.session.execute(Household.__table__.insert().values(head_citizen_id=ramesh.id, annual_income=144000).returning(Household.id))
    hh_id = hh.scalar()
    
    db_session.add(HouseholdMember(household_id=hh_id, citizen_id=ramesh.id, relationship_to_head="SELF"))
    db_session.add(Employment(citizen_id=ramesh.id, occupation="construction_worker", start_date=datetime.date.today() - datetime.timedelta(days=100)))
    
    loc_delhi = Location(citizen_id=ramesh.id, location_type="CURRENT", state="Delhi", district="NCR", is_active=True)
    db_session.add(loc_delhi)
    await db_session.flush()

    # Seed Scheme (Delhi BOCW - Since we start in Delhi)
    delhi_scheme = await ctx.scheme_repo.create(
        official_name="Delhi BOCW",
        category="EDUCATION", # Scenario uses education assistance
        state="Delhi",
        level="STATE",
        requirement_definitions=[{"type": "OCCUPATION", "name": "Worker Certificate"}]
    )
    delhi_version = SchemeVersion(scheme_id=delhi_scheme.id, version_number=1, verification_status="VERIFIED")
    db_session.add(delhi_version)
    await db_session.flush()
    delhi_scheme.current_version_id = delhi_version.id
    
    db_session.add(SchemeEligibilityRule(scheme_id=delhi_scheme.id, version_id=delhi_version.id, rule_type="OCCUPATION", operator="==", value="construction_worker"))
    await db_session.flush()
    
    # Add document and evidence to make it satisfied directly
    doc = await db_session.execute(
        text("INSERT INTO documents (id, citizen_id, document_type, verification_status) VALUES (:id, :cid, :dt, :vs) RETURNING id"),
        {"id": uuid.uuid4(), "cid": ramesh.id, "dt": "BOCW_CARD", "vs": "VERIFIED"}
    )
    doc_id = doc.scalar()
    await db_session.execute(
        text("INSERT INTO evidence (id, citizen_id, document_id, evidence_type, data) VALUES (:id, :cid, :did, :et, :d)"),
        {"id": uuid.uuid4(), "cid": ramesh.id, "did": doc_id, "et": "OCCUPATION", "d": '{"verified_occupation": "construction_worker"}'}
    )

    provider = MockAIProvider()
    agent = WelfareAgent(provider)
    
    # We will inject the scheme_id into the provider state
    provider.state["target_scheme_id"] = str(delhi_scheme.id)

    # --- Scenario 1: Location change ---
    resp1 = await agent.chat("Main Delhi se Gorakhpur wapas aa gaya hoon.", ctx)
    assert resp1.workflow_state == "COMPLETED"
    assert "evaluate_location_change" in resp1.actions
    assert len(resp1.execution_trace) > 0

    # --- Scenario 2: Application prep ---
    resp2 = await agent.chat("Mujhe education assistance ke liye apply karna hai.", ctx)
    assert resp2.workflow_state == "AWAITING_CONSENT"
    assert resp2.requires_consent is True
    assert "prepare_application" in resp2.actions
    assert "request_consent" in resp2.actions

    # Find the consent requested
    from sqlalchemy import select
    consent_stmt = select(Consent).where(Consent.action == 'APPLICATION_SUBMISSION', Consent.citizen_id == ramesh.id).order_by(Consent.created_at.desc())
    consent_rec = await db_session.execute(consent_stmt)
    c_row = consent_rec.scalars().first()
    assert c_row is not None
    consent_id = c_row.id
    app_id = c_row.application_id
    
    # Set app_id for next scenarios
    provider.state["target_app_id"] = str(app_id)

    # Explicitly grant consent (Mock user action in UI)
    await ctx.consent_svc.grant(consent_id)

    # --- Scenario 3: Submit ---
    resp3 = await agent.chat("Ha, submit karo.", ctx)
    assert resp3.workflow_state == "COMPLETED"
    assert "submit_application" in resp3.actions

    app = await ctx.app_repo.get_by_id(app_id)
    assert app.status == ApplicationStatus.SUBMITTED

    # --- Scenario 4: Government Response & Recovery ---
    # Simulate gov response
    await ctx.gov_provider.simulate_government_action(app.id, "REVIEW")
    await ctx.gov_provider.simulate_government_action(app.id, "REQUIRE_EVIDENCE", "Need clearer worker cert")
    
    resp4 = await agent.chat("Additional employment proof required.", ctx)
    assert resp4.workflow_state == "AWAITING_CONSENT"
    assert "prepare_recovery" in resp4.actions

    # Get new consent
    consent_stmt2 = select(Consent).where(Consent.action == 'APPLICATION_RESUBMISSION', Consent.citizen_id == ramesh.id).order_by(Consent.created_at.desc())
    consent_rec2 = await db_session.execute(consent_stmt2)
    c2_row = consent_rec2.scalars().first()
    assert c2_row is not None
    consent_id2 = c2_row.id

    await ctx.consent_svc.grant(consent_id2)

    # Resubmit
    resp5 = await agent.chat("Ha", ctx)
    assert resp5.workflow_state == "COMPLETED"
    assert "resubmit_application" in resp5.actions

    app_final = await ctx.app_repo.get_by_id(app_id)
    assert app_final.status == ApplicationStatus.RESUBMITTED
    
    # Audit events
    audits = await db_session.execute(text("SELECT action FROM audit_events WHERE citizen_id = :cid"), {"cid": ramesh.id})
    audit_actions = [row.action for row in audits.fetchall()]
    assert "SUBMIT_APPLICATION" in audit_actions
    assert "RESUBMIT_APPLICATION" in audit_actions
