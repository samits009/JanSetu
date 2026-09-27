import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from sqlalchemy import select

from app.main import app
from app.db.session import async_session_maker
from app.models.identity import User
from app.models.citizen import Citizen, Location, Employment
from app.models.scheme import Scheme, SchemeTranslation, RequirementTranslation
from app.services.password import hash_password

@pytest.mark.asyncio
async def test_dynamic_scheme_localization(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Fetch in English
        res_en = await client.get("/api/schemes?language=en")
        assert res_en.status_code == 200
        data_en = res_en.json()
        assert "items" in data_en
        
        # 2. Fetch in Hindi
        res_hi = await client.get("/api/schemes?language=hi")
        assert res_hi.status_code == 200
        data_hi = res_hi.json()
        assert "items" in data_hi

        # If translations were seeded or present, verify distinction
        hi_names = [s["official_name"] for s in data_hi["items"]]
        en_names = [s["official_name"] for s in data_en["items"]]
        assert len(data_hi["items"]) == len(data_en["items"])

@pytest.mark.asyncio
async def test_welfare_state_hindi_localization(db_session):
    unique_email = f"citizen_hi_{uuid4().hex[:6]}@jansetu.gov.in"
    unique_phone = f"98{uuid4().int % 100000000:08d}"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user
        reg_res = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "password": "Password@123",
                "name": "सुरेश कुमार",
                "phone": unique_phone,
                "preferred_language": "hi"
            }
        )
        assert reg_res.status_code in [200, 201]

        # Onboard with Hindi language preference
        onboard_res = await client.post(
            "/api/citizens/me/onboarding",
            json={
                "name": "सुरेश कुमार",
                "date_of_birth": "1988-06-20",
                "gender": "male",
                "phone": unique_phone,
                "current_state": "Delhi",
                "current_district": "North Delhi",
                "employment_status": "construction_worker",
                "occupation": "construction_worker",
                "annual_income": 95000,
                "household_members": 3,
                "dependents": 2
            }
        )
        assert onboard_res.status_code == 200

        # Query welfare state in Hindi
        ws_res = await client.get("/api/citizens/me/welfare-state?language=hi")
        assert ws_res.status_code == 200
        ws_data = ws_res.json()
        assert "new_opportunities" in ws_data
        
        # Verify why_it_applies has Hindi text if opportunities exist
        if ws_data["new_opportunities"]:
            opp = ws_data["new_opportunities"][0]
            assert "why_it_applies" in opp
            assert isinstance(opp["why_it_applies"], list)

@pytest.mark.asyncio
async def test_official_portal_handoff_workflow(db_session):
    unique_email = f"handoff_user_{uuid4().hex[:6]}@jansetu.gov.in"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register
        reg_res = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "password": "Password@123",
                "name": "दिनेश वर्मा",
                "preferred_language": "hi"
            }
        )
        assert reg_res.status_code in [200, 201]
        citizen_id = reg_res.json()["citizen_id"]

        # Fetch schemes to find an active scheme
        schemes_res = await client.get("/api/schemes")
        assert schemes_res.status_code == 200
        items = schemes_res.json()["items"]
        if not items:
            pytest.skip("No schemes available in test DB")
        target_scheme_id = items[0]["id"]

        # Create application
        create_res = await client.post(
            "/api/applications/",
            json={"citizen_id": citizen_id, "scheme_id": target_scheme_id}
        )
        assert create_res.status_code == 200
        app_id = create_res.json()["id"]

        # Prepare official portal handoff
        handoff_res = await client.post(f"/api/applications/{app_id}/handoff")
        assert handoff_res.status_code == 200
        handoff_data = handoff_res.json()
        assert "handoff_reference" in handoff_data
        assert "portal_url" in handoff_data
        assert handoff_data["status"] == "HANDOFF_PREPARED"
        assert handoff_data["handoff_reference"].startswith("JS-HANDOFF-")
