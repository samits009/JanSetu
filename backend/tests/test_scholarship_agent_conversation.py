import pytest
import uuid
from app.agents.tool_implementations import SearchSchemesInput, CheckScholarshipEligibilityInput
from app.agents.tools import tool_registry
from app.agents.providers.deterministic import DeterministicDomainFallbackProvider
from app.agents.welfare_agent import WelfareAgent
from app.api.endpoints.agent import get_agent_context


@pytest.mark.asyncio
async def test_scholarship_tools_direct(db_session):
    ctx = await get_agent_context(uuid.uuid4(), db_session)

    # 1. Test search_schemes tool
    search_tool = tool_registry.get_tool("search_schemes")
    assert search_tool is not None
    res = await search_tool.func(ctx, SearchSchemesInput(category="EDUCATION"))
    assert res.success is True
    assert res.data["count"] >= 3
    names = [s["name"] for s in res.data["schemes"]]
    assert any("Scholarship" in n for n in names)

    # 2. Test check_scholarship_eligibility tool for Class 12, OBC, 2 Lakhs
    check_tool = tool_registry.get_tool("check_scholarship_eligibility")
    assert check_tool is not None
    elig_res = await check_tool.func(
        ctx,
        CheckScholarshipEligibilityInput(
            class_or_course="12",
            annual_income=200000.0,
            category="OBC",
            gender="male"
        )
    )
    assert elig_res.success is True
    assert elig_res.data["eligible_count"] >= 1
    matched = elig_res.data["eligible_schemes"]
    matched_names = [m["name"] for m in matched]
    assert any("Post-Matric" in n or "NMMSS" in n or "PM-USP" in n for n in matched_names)


@pytest.mark.asyncio
async def test_scholarship_agent_two_turn_conversation(db_session):
    ctx = await get_agent_context(uuid.uuid4(), db_session)
    provider = DeterministicDomainFallbackProvider()
    agent = WelfareAgent(provider)

    # TURN 1: User asks for scholarships
    turn1_prompt = "I am a student and I need to look for scholarships, suggest me some scholarships"
    resp1 = await agent.chat(turn1_prompt, ctx)
    assert resp1.message is not None
    # Must list scholarships and prompt for user criteria
    msg1 = resp1.message.lower()
    assert "scholarship" in msg1 or "nmmss" in msg1 or "छात्रवृत्ति" in msg1
    assert "income" in msg1 or "आय" in msg1 or "class" in msg1 or "course" in msg1

    # TURN 2: User provides student details
    turn2_prompt = "I am in class 12, my family income is 2 lakh per year, category is OBC"
    resp2 = await agent.chat(turn2_prompt, ctx)
    assert resp2.message is not None
    msg2 = resp2.message.lower()
    # Must evaluate eligibility and show matching scholarships / next steps
    assert "scholarship" in msg2 or "eligible" in msg2 or "documents" in msg2 or "application" in msg2

