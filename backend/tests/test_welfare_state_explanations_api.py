import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.seed import RAMESH_UUID

@pytest.mark.asyncio
async def test_welfare_state_explanations_api(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Authenticate via demo-login
        login_res = await client.post("/api/auth/demo-login")
        assert login_res.status_code == 200

        resp = await client.get(f"/api/citizens/{RAMESH_UUID}/welfare-state")
        assert resp.status_code == 200
        data = resp.json()

        # Check evidence readiness score
        assert "evidence_readiness_score" in data
        assert isinstance(data["evidence_readiness_score"], int)

        # Check opportunities have explanation and readiness
        assert "new_opportunities" in data
        if len(data["new_opportunities"]) > 0:
            opp = data["new_opportunities"][0]
            assert "why_it_applies" in opp
            assert isinstance(opp["why_it_applies"], list)
            assert "matched_rules" in opp
            assert "readiness_percentage" in opp
            assert "verification_status" in opp
