"""
test_scheme_authorization.py
Tests that mutating endpoints require valid admin credentials.
Tests production-mode mock-auth rejection.
"""
import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_refresh_requires_admin(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/schemes/00000000-0000-0000-0000-000000000000/refresh")
    # No admin token → 401 or 422
    assert response.status_code in (401, 422, 503)


@pytest.mark.asyncio
async def test_publish_requires_admin(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/scheme-versions/00000000-0000-0000-0000-000000000000/publish")
    assert response.status_code in (401, 422, 503)


@pytest.mark.asyncio
async def test_approve_requires_admin(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/scheme-versions/00000000-0000-0000-0000-000000000000/approve")
    assert response.status_code in (401, 422, 503)


@pytest.mark.asyncio
async def test_reject_requires_admin(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/scheme-versions/00000000-0000-0000-0000-000000000000/reject")
    assert response.status_code in (401, 422, 503)


@pytest.mark.asyncio
async def test_invalid_admin_token_rejected(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/scheme-versions/00000000-0000-0000-0000-000000000000/publish",
            headers={"X-Admin-Token": "wrong-token"}
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_production_mode_rejects_mock_admin(db_session, monkeypatch):
    """
    When DEV_MOCK_ADMIN_AUTH is false (production mode), the mock admin token
    MUST be rejected, even if the token matches.
    """
    import app.services.admin_auth as auth_module
    original = auth_module.DEV_MOCK_ADMIN_AUTH
    auth_module.DEV_MOCK_ADMIN_AUTH = False
    # Also update the identity provider's flag
    auth_module._admin_identity_provider = auth_module.MockDevAdminIdentity()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/scheme-versions/00000000-0000-0000-0000-000000000000/publish",
                headers={"X-Admin-Token": "mock-admin-token"}
            )
        assert response.status_code == 503, f"Expected 503 in production mode, got {response.status_code}"
    finally:
        auth_module.DEV_MOCK_ADMIN_AUTH = original
        auth_module._admin_identity_provider = auth_module.MockDevAdminIdentity()


@pytest.mark.asyncio
async def test_pending_review_requires_admin(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/scheme-review/pending")
    assert response.status_code in (401, 422, 503)
