import pytest
from httpx import ASGITransport, AsyncClient
from app.db.seed import RAMESH_UUID
from app.main import app


@pytest.mark.asyncio
async def test_mock_provenance_is_persisted(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"},
            files={"file": ("proof.pdf", b"provenance", "application/pdf")},
        )
        document = await client.get(f"/api/documents/{response.json()['document_id']}?citizen_id={RAMESH_UUID}")
    assert document.json()["extraction_method"] == "MOCK"
    assert document.json()["status"] == "EXTRACTED"
