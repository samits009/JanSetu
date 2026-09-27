import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.seed import RAMESH_UUID


@pytest.mark.asyncio
async def test_demo_login_me_and_logout(monkeypatch, db_session):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login = await client.post("/api/auth/demo-login")
        assert login.status_code == 200
        assert login.json()["citizen_id"] == str(RAMESH_UUID)
        assert "jansetu_session" in login.cookies
        me = await client.get("/api/auth/me")
        assert me.status_code == 200
        logout = await client.post("/api/auth/logout")
        assert logout.status_code == 200
        assert (await client.get("/api/auth/me")).status_code == 401


@pytest.mark.asyncio
async def test_invalid_session_rejected(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"jansetu_session": "invalid"}) as client:
        assert (await client.get("/api/auth/me")).status_code == 401
