import pytest
from httpx import ASGITransport, AsyncClient
from app.db.seed import RAMESH_UUID
from app.main import app


@pytest.mark.asyncio
async def test_extracted_claim_becomes_evidence(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "BOCW_CARD"},
            files={"file": ("worker.jpg", b"worker document", "image/jpeg")},
        )
        detail = await client.get(f"/api/documents/{response.json()['document_id']}?citizen_id={RAMESH_UUID}")
    assert detail.status_code == 200
    evidence = detail.json()["evidence"]
    assert evidence[0]["document_id"] == response.json()["document_id"]
    assert evidence[0]["verification_status"] == "PENDING"
