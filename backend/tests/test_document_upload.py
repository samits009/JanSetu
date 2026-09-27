import io
import pytest
from httpx import ASGITransport, AsyncClient
from app.db.seed import RAMESH_UUID
from app.main import app


@pytest.mark.asyncio
async def test_valid_document_upload_persists_and_generates_claim(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"},
            files={"file": ("proof.pdf", b"valid document", "application/pdf")},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "EXTRACTED"
    assert payload["duplicate_detected"] is False
    assert payload["document_id"]


@pytest.mark.asyncio
async def test_document_detail_returns_evidence(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        upload = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"},
            files={"file": ("detail.png", b"detail document", "image/png")},
        )
        document_id = upload.json()["document_id"]
        response = await client.get(f"/api/documents/{document_id}?citizen_id={RAMESH_UUID}")
    assert response.status_code == 200
    assert response.json()["evidence"]
    assert response.json()["extraction_method"] == "MOCK"
