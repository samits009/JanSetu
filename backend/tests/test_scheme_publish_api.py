"""
test_scheme_publish_api.py
Critical lifecycle tests for the publish endpoint.
Verifies the invariant: only PUBLISH may update current_version_id.
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.models.scheme import Scheme, SchemeVersion, SchemeSource
from app.domain.enums import VerificationStatus

ADMIN_HEADERS = {"X-Admin-Token": "mock-admin-token"}


async def _create_scheme_with_version(db_session, status=VerificationStatus.DEMO) -> tuple:
    source = SchemeSource(authority="Test", source_url="test.json", source_type="FIXTURE")
    db_session.add(source)
    await db_session.flush()

    scheme = Scheme(official_name=f"Publish Test Scheme {uuid4().hex[:6]}", category="EDUCATION", level="CENTRAL")
    db_session.add(scheme)
    await db_session.flush()

    v1 = SchemeVersion(scheme_id=scheme.id, version_number=1, verification_status=VerificationStatus.DEMO, source_id=source.id)
    db_session.add(v1)
    await db_session.flush()
    scheme.current_version_id = v1.id
    await db_session.flush()

    return scheme, v1, source


@pytest.mark.asyncio
async def test_publish_demo_version_succeeds(db_session):
    scheme, v1, _ = await _create_scheme_with_version(db_session)
    # Create a candidate v2
    v2 = SchemeVersion(scheme_id=scheme.id, version_number=2, verification_status=VerificationStatus.DEMO)
    db_session.add(v2)
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{v2.id}/publish", headers=ADMIN_HEADERS)

    assert response.status_code == 200, response.text
    data = response.json()
    assert "version_id" in data

    # Verify current_version_id changed in DB
    await db_session.refresh(scheme)
    assert scheme.current_version_id == v2.id


@pytest.mark.asyncio
async def test_publish_rejected_version_fails(db_session):
    scheme, v1, _ = await _create_scheme_with_version(db_session)
    rejected_v = SchemeVersion(scheme_id=scheme.id, version_number=2, verification_status=VerificationStatus.REJECTED)
    db_session.add(rejected_v)
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{rejected_v.id}/publish", headers=ADMIN_HEADERS)

    assert response.status_code == 400
    # current_version_id must remain v1
    await db_session.refresh(scheme)
    assert scheme.current_version_id == v1.id


@pytest.mark.asyncio
async def test_approve_does_not_change_current_version(db_session):
    scheme, v1, _ = await _create_scheme_with_version(db_session)
    v2 = SchemeVersion(scheme_id=scheme.id, version_number=2, verification_status=VerificationStatus.NEEDS_REVIEW)
    db_session.add(v2)
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{v2.id}/approve", headers=ADMIN_HEADERS)
    assert response.status_code == 200

    # v1 must still be current
    await db_session.refresh(scheme)
    assert scheme.current_version_id == v1.id


@pytest.mark.asyncio
async def test_reject_does_not_change_current_version(db_session):
    scheme, v1, _ = await _create_scheme_with_version(db_session)
    v2 = SchemeVersion(scheme_id=scheme.id, version_number=2, verification_status=VerificationStatus.NEEDS_REVIEW)
    db_session.add(v2)
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/scheme-versions/{v2.id}/reject", headers=ADMIN_HEADERS)
    assert response.status_code == 200

    await db_session.refresh(scheme)
    assert scheme.current_version_id == v1.id


@pytest.mark.asyncio
async def test_full_lifecycle_v1_current_until_publish(db_session):
    """
    Critical lifecycle test:
    V1 is current → refresh creates V2 → V1 remains current
    → approve V2 → V1 still current → publish V2 → V2 becomes current → V1 immutable
    """
    scheme, v1, _ = await _create_scheme_with_version(db_session)
    v2 = SchemeVersion(scheme_id=scheme.id, version_number=2, verification_status=VerificationStatus.NEEDS_REVIEW)
    db_session.add(v2)
    await db_session.flush()

    v1_id = v1.id
    v2_id = v2.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Before publish: V1 is current
        detail_resp = await client.get(f"/api/schemes/{scheme.id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["current_version_id"] == str(v1_id)

        # Approve V2 → V1 still current
        approve_resp = await client.post(f"/api/scheme-versions/{v2_id}/approve", headers=ADMIN_HEADERS)
        assert approve_resp.status_code == 200

        detail_resp2 = await client.get(f"/api/schemes/{scheme.id}")
        assert detail_resp2.json()["current_version_id"] == str(v1_id)

        # Publish V2 → V2 becomes current
        publish_resp = await client.post(f"/api/scheme-versions/{v2_id}/publish", headers=ADMIN_HEADERS)
        assert publish_resp.status_code == 200

        detail_resp3 = await client.get(f"/api/schemes/{scheme.id}")
        assert detail_resp3.json()["current_version_id"] == str(v2_id)

    # Verify V1 still exists in DB (immutable)
    v1_check = (await db_session.execute(select(SchemeVersion).where(SchemeVersion.id == v1_id))).scalars().first()
    assert v1_check is not None


@pytest.mark.asyncio
async def test_historical_application_pinned_after_publish(db_session):
    """Existing applications must remain pinned to their version after a new version is published."""
    from app.models.citizen import Citizen
    from app.models.application import WelfareApplication
    from app.domain.enums import ApplicationStatus

    scheme, v1, _ = await _create_scheme_with_version(db_session)
    citizen = Citizen(name="Historical Citizen")
    db_session.add(citizen)
    await db_session.flush()

    app_record = WelfareApplication(
        citizen_id=citizen.id, scheme_id=scheme.id,
        scheme_version_id=v1.id, status=ApplicationStatus.APPROVED
    )
    db_session.add(app_record)
    await db_session.flush()

    # Publish V2
    v2 = SchemeVersion(scheme_id=scheme.id, version_number=2, verification_status=VerificationStatus.DEMO)
    db_session.add(v2)
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(f"/api/scheme-versions/{v2.id}/publish", headers=ADMIN_HEADERS)

    # App record still references V1
    await db_session.refresh(app_record)
    assert app_record.scheme_version_id == v1.id
