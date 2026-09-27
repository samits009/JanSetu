import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.seed import RAMESH_UUID

OTHER_CITIZEN = "00000000-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected_when_demo_compatibility_disabled(monkeypatch, db_session):
    monkeypatch.setenv("DEV_DEMO_AUTH", "false")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/citizens/{RAMESH_UUID}/welfare-state")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_citizen_cannot_access_another_citizen(monkeypatch, db_session):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.post("/api/auth/demo-login")).status_code == 200
        response = await client.get(f"/api/citizens/{OTHER_CITIZEN}/welfare-state")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_citizen_session_cannot_use_admin_endpoint(monkeypatch, db_session):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    monkeypatch.setattr("app.services.admin_auth.DEV_MOCK_ADMIN_AUTH", True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/demo-login")
        response = await client.post(
            "/api/scheme-versions/00000000-0000-0000-0000-000000000000/publish",
            headers={"X-Admin-Token": "mock-admin-token"},
        )
    assert response.status_code == 403
