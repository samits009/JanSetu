import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_logout_invalidates_session(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.post("/api/auth/demo-login")).status_code == 200
        assert (await client.get("/api/auth/me")).status_code == 200
        await client.post("/api/auth/logout")
        assert (await client.get("/api/auth/me")).status_code == 401
