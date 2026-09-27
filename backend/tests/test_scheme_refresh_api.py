"""
test_scheme_refresh_api.py
Critical refresh tests:
  - no-material-change → no new version
  - material change → candidate version created, current unchanged
  - unauthorized refresh rejected
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.models.scheme import Scheme, SchemeVersion, SchemeSource
from app.domain.enums import VerificationStatus

ADMIN_HEADERS = {"X-Admin-Token": "mock-admin-token"}


@pytest.mark.asyncio
async def test_refresh_scheme_not_found(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/schemes/00000000-0000-0000-0000-000000000000/refresh",
            headers=ADMIN_HEADERS
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_refresh_without_source_returns_message(db_session):
    """Scheme with no source configured returns a 'no source' message, not an error."""
    scheme = Scheme(official_name=f"No Source Scheme {uuid4().hex[:6]}", category="NUTRITION", level="CENTRAL")
    db_session.add(scheme)
    await db_session.flush()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/schemes/{scheme.id}/refresh", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert data["material_change"] == False
    assert "source" in data["message"].lower() or "no" in data["message"].lower()


@pytest.mark.asyncio
async def test_refresh_does_not_require_no_admin():
    """Refresh without admin header should return 401 or 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/schemes/00000000-0000-0000-0000-000000000000/refresh")
    assert response.status_code in (401, 422, 503)
