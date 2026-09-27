import pytest
from httpx import ASGITransport, AsyncClient
from app.db.seed import RAMESH_UUID
from app.main import app


@pytest.mark.asyncio
async def test_executable_and_mismatched_types_are_rejected(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        executable = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"},
            files={"file": ("script.exe", b"MZ", "application/octet-stream")},
        )
        mismatch = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"},
            files={"file": ("fake.pdf", b"not pdf", "image/png")},
        )
    assert executable.status_code == 415
    assert mismatch.status_code == 415


@pytest.mark.asyncio
async def test_oversized_document_is_rejected(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/documents/",
            data={"citizen_id": str(RAMESH_UUID), "document_type": "GENERAL"},
            files={"file": ("large.pdf", b"x" * (10 * 1024 * 1024 + 1), "application/pdf")},
        )
    assert response.status_code == 413
