import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_full_persistence_cycle(db_session):
    """
    Mandatory persistence integration test.

    Verifies: register -> onboard -> welfare state -> language preference -> logout -> re-login -> state intact.
    PostgreSQL is the canonical source of truth. All data must survive logout/login.
    """
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # PHASE 1: Register new citizen
        reg = await client.post("/api/auth/register", json={
            "name": "Priya Nair",
            "email": "priya.nair@persistence.test",
            "phone": "9870000001",
            "password": "SecurePass123!",
            "preferred_language": "en",
        })
        assert reg.status_code == 200, f"Register failed: {reg.text}"
        reg_data = reg.json()
        assert reg_data["authenticated"] is True
        assert reg_data["citizen_name"] == "Priya Nair"
        assert reg_data["email"] == "priya.nair@persistence.test"
        assert reg_data["phone"] == "9870000001"
        assert reg_data["preferred_language"] == "en"
        citizen_id = reg_data["citizen_id"]
        assert citizen_id is not None

        # PHASE 2: Complete onboarding
        ob = await client.post("/api/citizens/me/onboarding", json={
            "name": "Priya Nair",
            "date_of_birth": "1990-08-15",
            "gender": "female",
            "phone": "9870000001",
            "current_state": "Maharashtra",
            "current_district": "Pune",
            "permanent_state": "Kerala",
            "permanent_district": "Ernakulam",
            "occupation": "Construction Worker",
            "employment_status": "informal_labor",
            "annual_income": 120000,
            "household_members": 3,
            "dependents": 2,
        })
        assert ob.status_code == 200, f"Onboarding failed: {ob.text}"
        ob_profile = ob.json()["profile"]
        assert ob_profile["name"] == "Priya Nair"
        assert ob_profile["gender"] == "female"
        assert ob_profile["onboarding_completed"] is True
        assert any(loc["district"] == "Pune" for loc in ob_profile["locations"])
        assert any(loc["state"] == "Kerala" for loc in ob_profile["locations"])
        emp_list = ob_profile["employments"]
        assert any(e["occupation"] == "Construction Worker" for e in emp_list)
        assert any(e["employment_status"] == "informal_labor" for e in emp_list)

        # PHASE 3: Welfare state accessible
        ws = await client.get("/api/citizens/me/welfare-state")
        assert ws.status_code == 200, f"Welfare state failed: {ws.text}"
        assert ws.json()["citizen_summary"]["name"] == "Priya Nair"

        # PHASE 4: Language preference change persists to PostgreSQL
        pref_put = await client.put("/api/citizens/me/preferences", json={"preferred_language": "hi"})
        assert pref_put.status_code == 200, f"Preferences update failed: {pref_put.text}"
        assert pref_put.json()["preferred_language"] == "hi"

        # PHASE 5: /api/auth/me reflects the DB-updated language
        me_resp = await client.get("/api/auth/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["preferred_language"] == "hi"

        # PHASE 6: Logout
        logout = await client.post("/api/auth/logout")
        assert logout.status_code == 200
        assert logout.json()["authenticated"] is False

        # Session should be gone
        after_logout = await client.get("/api/auth/me")
        assert after_logout.status_code == 401

    # PHASE 7: Re-login in a fresh client (proves PostgreSQL persistence)
    async with AsyncClient(transport=transport, base_url="http://test") as fresh_client:
        login = await fresh_client.post("/api/auth/login", json={
            "username": "priya.nair@persistence.test",
            "password": "SecurePass123!",
        })
        assert login.status_code == 200, f"Re-login failed: {login.text}"
        login_data = login.json()
        assert login_data["authenticated"] is True
        assert login_data["citizen_name"] == "Priya Nair"
        assert login_data["email"] == "priya.nair@persistence.test"
        # Phone must persist across sessions
        assert login_data["phone"] == "9870000001"
        # Language preference must persist (was changed to 'hi')
        assert login_data["preferred_language"] == "hi"

        # PHASE 8: Full citizen profile survives re-login
        me2 = await fresh_client.get("/api/citizens/me")
        assert me2.status_code == 200, f"Post-login /me failed: {me2.text}"
        profile = me2.json()["profile"]
        assert profile["name"] == "Priya Nair"
        assert profile["gender"] == "female"
        assert profile["onboarding_completed"] is True
        assert any(loc["district"] == "Pune" for loc in profile["locations"])
        assert any(loc["state"] == "Kerala" for loc in profile["locations"])
        emp_list2 = profile["employments"]
        assert any(e["occupation"] == "Construction Worker" for e in emp_list2)
        assert any(e["employment_status"] == "informal_labor" for e in emp_list2)

        # PHASE 9: Welfare state intact after re-login
        ws2 = await fresh_client.get("/api/citizens/me/welfare-state")
        assert ws2.status_code == 200
        assert ws2.json()["citizen_summary"]["name"] == "Priya Nair"

        # PHASE 10: Multi-user isolation
        # Register a second citizen and verify cross-access is denied
        reg_b = await fresh_client.post("/api/auth/register", json={
            "name": "Arjun Reddy",
            "email": "arjun.reddy@persistence.test",
            "phone": "9870000002",
            "password": "SecurePass123!",
        })
        if reg_b.status_code == 200:
            citizen_id_b = reg_b.json()["citizen_id"]
            # Now logged in as Arjun; try to access original citizen_id (Priya's data)
            cross_access = await fresh_client.get(f"/api/citizens/{citizen_id}/welfare-state")
            assert cross_access.status_code == 403, \
                f"Cross-user access must be denied (403), got {cross_access.status_code}: {cross_access.text}"
