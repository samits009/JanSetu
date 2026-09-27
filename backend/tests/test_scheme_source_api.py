"""
test_scheme_source_api.py
Tests for scheme source read endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_scheme_sources(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/scheme-sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_source_does_not_expose_filesystem_path(db_session):
    """source_url should be None for local fixture sources (filesystem paths hidden)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/scheme-sources")
    assert response.status_code == 200
    for source in response.json():
        url = source.get("source_url")
        if url is not None:
            # Any exposed URL must be an HTTP(S) URL, never a filesystem path
            assert url.startswith("http"), f"Filesystem path leaked: {url}"


@pytest.mark.asyncio
async def test_get_source_not_found(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/scheme-sources/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
