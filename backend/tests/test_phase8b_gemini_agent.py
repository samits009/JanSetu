import pytest
import uuid
import datetime
from app.agents.providers.gemini import GeminiProvider
from app.agents.providers.deterministic import DeterministicDomainFallbackProvider
from app.agents.welfare_agent import WelfareAgent
from app.api.endpoints.agent import get_agent_context
from app.models.citizen import Household, HouseholdMember, Employment, Location
from app.models.scheme import Scheme, SchemeEligibilityRule, SchemeVersion
from sqlalchemy import text


@pytest.mark.asyncio
async def test_gemini_provider_degradation_to_deterministic_fallback():
    fallback = DeterministicDomainFallbackProvider()
    # Initialized with a dummy key that fails, with 0 retries and quick timeout
    provider = GeminiProvider(
        api_key="invalid-api-key-for-test",
        max_retries=0,
        timeout_seconds=0.5,
        fallback=fallback
    )

    ctx = {"citizen_id": str(uuid.uuid4())}
    # Should gracefully degrade to deterministic fallback
    res = await provider.generate_response("Mujhe aavedan karna hai", ctx, [])
    assert res["action"] in ("text", "tool_call")
    if res["action"] == "text":
        assert "जनसेतु" in res["message"] or "JanSetu" in res["message"]


@pytest.mark.asyncio
async def test_deterministic_domain_provider_end_to_end(db_session):
    # Setup citizen and scheme
    ctx = await get_agent_context(uuid.uuid4(), db_session)
    dob = datetime.date.today() - datetime.timedelta(days=30 * 365)
    citizen = await ctx.cit_repo.create(name="Anil Verma", dob=dob)
    ctx.citizen_id = citizen.id

    loc = Location(citizen_id=citizen.id, location_type="CURRENT", state="Delhi", district="Central", is_active=True)
    db_session.add(loc)
    emp = Employment(citizen_id=citizen.id, occupation="carpenter", start_date=datetime.date.today() - datetime.timedelta(days=60))
    db_session.add(emp)
    await db_session.flush()

    scheme = await ctx.scheme_repo.create(
        official_name="Delhi BOCW Assistance",
        category="HOUSING",
        state="Delhi",
        level="STATE",
        requirement_definitions=[{"type": "OCCUPATION", "name": "Worker Card"}]
    )
    version = SchemeVersion(scheme_id=scheme.id, version_number=1, verification_status="VERIFIED")
    db_session.add(version)
    await db_session.flush()
    scheme.current_version_id = version.id

    db_session.add(SchemeEligibilityRule(scheme_id=scheme.id, version_id=version.id, rule_type="OCCUPATION", operator="==", value="carpenter"))
    await db_session.flush()

    # Use the deterministic domain fallback provider
    provider = DeterministicDomainFallbackProvider()
    agent = WelfareAgent(provider)

    # Test migration prompt
    resp_mig = await agent.chat("Main Delhi se Gorakhpur shifted ho gaya hoon", ctx)
    assert resp_mig.workflow_state in ("COMPLETED", "AWAITING_CONSENT")
    assert "evaluate_location_change" in resp_mig.actions
    assert len(resp_mig.execution_trace) > 0
    # Assert execution trace does not contain internal chain-of-thought
    for trace in resp_mig.execution_trace:
        assert not hasattr(trace, "thought")
