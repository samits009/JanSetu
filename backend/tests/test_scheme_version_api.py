"""
test_scheme_version_api.py
Tests for scheme version detail endpoint.
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.scheme import Scheme, SchemeVersion, SchemeSource
from app.domain.enums import VerificationStatus


@pytest.mark.asyncio
async def test_get_version_detail(db_session):
    source = SchemeSource(authority="Test", source_url="t.json", source_type="FIXTURE")
    db_session.add(source)
    scheme = Scheme(official_name=f"Version Detail Test {uuid4().hex[:6]}", category="PENSION", level="CENTRAL")
    db_session.add(scheme)
    await db_session.flush()

    v = SchemeVersion(
        scheme_id=scheme.id,
        version_number=1,
        verification_status=VerificationStatus.DEMO,
        source_id=source.id,
        content_hash="abc123"
    )
    db_session.add(v)
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/scheme-versions/{v.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(v.id)
    assert data["scheme_id"] == str(scheme.id)
    assert data["version_number"] == 1
    assert data["verification_status"] == "DEMO"
    assert data["content_hash"] == "abc123"
    assert "rules" in data
    assert "requirements" in data
    assert "benefits" in data


@pytest.mark.asyncio
async def test_get_version_not_found(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/scheme-versions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_version_ordering(db_session):
    """Versions should be returned newest-first."""
    scheme = Scheme(official_name=f"Ordering Test {uuid4().hex[:6]}", category="HOUSING", level="CENTRAL")
    db_session.add(scheme)
    await db_session.flush()

    v1 = SchemeVersion(scheme_id=scheme.id, version_number=1, verification_status=VerificationStatus.DEMO)
    v2 = SchemeVersion(scheme_id=scheme.id, version_number=2, verification_status=VerificationStatus.NEEDS_REVIEW)
    db_session.add_all([v1, v2])
    await db_session.flush()
    scheme.current_version_id = v1.id
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/schemes/{scheme.id}/versions")

    assert response.status_code == 200
    versions = response.json()
    assert len(versions) >= 2
    # Check descending version number order
    numbers = [v["version_number"] for v in versions]
    assert numbers == sorted(numbers, reverse=True)
