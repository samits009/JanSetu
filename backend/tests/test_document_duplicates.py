import pytest
from httpx import ASGITransport, AsyncClient
from app.db.seed import RAMESH_UUID
from app.main import app


@pytest.mark.asyncio
async def test_duplicate_document_is_reported_without_new_record(db_session):
    files = {"file": ("same.pdf", b"same bytes", "application/pdf")}
    data = {"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post("/api/documents/", data=data, files=files)
        second = await client.post("/api/documents/", data=data, files={"file": ("renamed.pdf", b"same bytes", "application/pdf")})
    assert first.json()["duplicate_detected"] is False
    assert second.json()["duplicate_detected"] is True
    assert second.json()["document_id"] == first.json()["document_id"]
