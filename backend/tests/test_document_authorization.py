import pytest
from httpx import ASGITransport, AsyncClient
from app.db.seed import RAMESH_UUID
from app.main import app


@pytest.mark.asyncio
async def test_document_detail_requires_authenticated_owner(db_session, monkeypatch):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/demo-login")
        response = await client.get(
            "http://test/api/documents/00000000-0000-0000-0000-000000000001"
            f"?citizen_id={RAMESH_UUID}"
        )
    assert response.status_code in (403, 404)
