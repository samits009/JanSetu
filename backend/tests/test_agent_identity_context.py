import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.seed import RAMESH_UUID


@pytest.mark.asyncio
async def test_agent_cannot_override_authenticated_citizen(monkeypatch, db_session):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/demo-login")
        response = await client.post("/api/agent/chat", json={
            "citizen_id": "00000000-0000-0000-0000-000000000001",
            "message": "show profile",
        })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_agent_uses_authenticated_demo_citizen(monkeypatch, db_session):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/demo-login")
        response = await client.post("/api/agent/chat", json={
            "citizen_id": str(RAMESH_UUID),
            "message": "show profile",
        })
    assert response.status_code == 200
