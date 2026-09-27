import pytest
from httpx import ASGITransport, AsyncClient
from app.db.seed import RAMESH_UUID
from app.main import app


@pytest.mark.asyncio
async def test_claims_endpoint_and_authorized_processing(db_session, monkeypatch):
    monkeypatch.setenv("DEV_DEMO_AUTH", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/demo-login")
        upload = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"},
            files={"file": ("process.pdf", b"process me", "application/pdf")},
        )
        document_id = upload.json()["document_id"]
        processed = await client.post(
            f"/api/documents/{document_id}/process?citizen_id={RAMESH_UUID}"
        )
        claims = await client.get(
            f"/api/documents/{document_id}/claims?citizen_id={RAMESH_UUID}"
        )
    assert processed.status_code == 200
    assert claims.status_code == 200
    assert claims.json()
