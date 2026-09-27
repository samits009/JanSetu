"""
test_scheme_review_api.py
Tests for review workflow (approve, reject, mark-needs-review, pending list).
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.scheme import Scheme, SchemeVersion, SchemeSource
from app.domain.enums import VerificationStatus

ADMIN_HEADERS = {"X-Admin-Token": "mock-admin-token"}


async def _make_version(db_session, status=VerificationStatus.NEEDS_REVIEW):
    source = SchemeSource(authority="Review Test", source_url="t.json", source_type="FIXTURE")
    db_session.add(source)
    scheme = Scheme(official_name=f"Review Test {uuid4().hex[:6]}", category="HEALTH", level="CENTRAL")
    db_session.add(scheme)
    await db_session.flush()
    v = SchemeVersion(scheme_id=scheme.id, version_number=1, verification_status=status, source_id=source.id)
    db_session.add(v)
    await db_session.flush()
    return scheme, v


@pytest.mark.asyncio
async def test_pending_review_list(db_session):
    _, v = await _make_version(db_session, VerificationStatus.NEEDS_REVIEW)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/scheme-review/pending", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert str(v.id) in ids


@pytest.mark.asyncio
async def test_approve_version(db_session):
    _, v = await _make_version(db_session, VerificationStatus.NEEDS_REVIEW)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{v.id}/approve", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert data["verification_status"] == "VERIFIED"


@pytest.mark.asyncio
async def test_reject_version(db_session):
    _, v = await _make_version(db_session, VerificationStatus.NEEDS_REVIEW)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{v.id}/reject", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert data["verification_status"] == "REJECTED"


@pytest.mark.asyncio
async def test_cannot_approve_rejected_version(db_session):
    _, v = await _make_version(db_session, VerificationStatus.REJECTED)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{v.id}/approve", headers=ADMIN_HEADERS)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_mark_needs_review(db_session):
    _, v = await _make_version(db_session, VerificationStatus.DEMO)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{v.id}/mark-needs-review", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert data["verification_status"] == "NEEDS_REVIEW"
