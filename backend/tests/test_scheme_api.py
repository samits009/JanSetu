"""
test_scheme_api.py — Scheme read API tests
Tests pagination, filtering, and detail endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_schemes_paginated(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/schemes?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data
    assert "has_next" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_list_schemes_filter_by_category(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/schemes?category=EMPLOYMENT")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["category"] == "EMPLOYMENT"


@pytest.mark.asyncio
async def test_list_schemes_search(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/schemes?search=BOCW")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert "BOCW" in item["official_name"].upper() or "bocw" in item["official_name"].lower()


@pytest.mark.asyncio
async def test_get_scheme_detail(db_session):
    # Get first scheme ID from list
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        list_resp = await client.get("/api/schemes?page_size=1")
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        if not items:
            pytest.skip("No schemes in database")
        scheme_id = items[0]["id"]

        detail_resp = await client.get(f"/api/schemes/{scheme_id}")
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert "id" in data
    assert "official_name" in data
    assert "category" in data


@pytest.mark.asyncio
async def test_get_scheme_not_found(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/schemes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scheme_versions_list(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        list_resp = await client.get("/api/schemes?page_size=1")
        items = list_resp.json()["items"]
        if not items:
            pytest.skip("No schemes")
        scheme_id = items[0]["id"]
        version_resp = await client.get(f"/api/schemes/{scheme_id}/versions")
    assert version_resp.status_code == 200
    assert isinstance(version_resp.json(), list)


@pytest.mark.asyncio
async def test_scheme_rules_list(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        list_resp = await client.get("/api/schemes?page_size=1")
        items = list_resp.json()["items"]
        if not items:
            pytest.skip("No schemes")
        scheme_id = items[0]["id"]
        rules_resp = await client.get(f"/api/schemes/{scheme_id}/rules")
    assert rules_resp.status_code == 200
    assert isinstance(rules_resp.json(), list)


@pytest.mark.asyncio
async def test_scheme_benefits_list(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        list_resp = await client.get("/api/schemes?page_size=1")
        items = list_resp.json()["items"]
        if not items:
            pytest.skip("No schemes")
        scheme_id = items[0]["id"]
        benefits_resp = await client.get(f"/api/schemes/{scheme_id}/benefits")
    assert benefits_resp.status_code == 200


@pytest.mark.asyncio
async def test_max_page_size_enforced(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/schemes?page_size=999")
    # FastAPI should cap it via Query(le=100) → 422 since > 100 is not allowed
    assert response.status_code == 422
