import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.seed import RAMESH_UUID


@pytest.mark.asyncio
async def test_document_endpoint_does_not_allow_url_identity_override(monkeypatch, db_session):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/demo-login")
        response = await client.get(f"/api/citizens/00000000-0000-0000-0000-000000000001/documents")
    assert response.status_code == 403
