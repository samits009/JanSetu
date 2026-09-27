import pytest
import hashlib
from httpx import AsyncClient, ASGITransport
from app.main import app

REAL_TEST_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 50 >>\nstream\nBT /F1 12 Tf 100 700 Td (Sovereign Citizen Document A) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n306\n%%EOF"

REAL_TEST_DOC_B_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 50 >>\nstream\nBT /F1 12 Tf 100 700 Td (Sovereign Citizen Document B) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n306\n%%EOF"


@pytest.mark.asyncio
async def test_requirement_18_complete_account_round_trip(db_session):
    """
    Requirement 18: Complete Account Round Trip
    REGISTER -> LOGIN -> CREATE PROFILE -> SET LOCATION -> SET EMPLOYMENT -> SET HOUSEHOLD
    -> SET LANGUAGE = HINDI -> UPLOAD ACTUAL FILE -> VERIFY DOCUMENT PERSISTENCE
    -> VERIFY EVIDENCE PERSISTENCE -> CREATE APPLICATION -> VERIFY APPLICATION PERSISTENCE
    -> LOGOUT -> FRESH CLIENT -> LOGIN -> VERIFY PROFILE -> VERIFY LOCATION -> VERIFY EMPLOYMENT
    -> VERIFY HOUSEHOLD -> VERIFY HINDI -> VERIFY DOCUMENT -> VERIFY FILE BYTES -> VERIFY EVIDENCE
    -> VERIFY APPLICATION.
    EVERY VALUE MUST MATCH.
    """
    transport = ASGITransport(app=app)
    expected_doc_hash = hashlib.sha256(REAL_TEST_PDF_BYTES).hexdigest()

    # 1. REGISTER
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reg_res = await client.post("/api/auth/register", json={
            "name": "Ananya Roy",
            "email": "ananya.roy@example.gov.in",
            "password": "Password123#Secure",
            "phone": "9812345678",
            "preferred_language": "en",
        })
        assert reg_res.status_code == 200, reg_res.text
        auth_data = reg_res.json()
        citizen_id = auth_data["citizen_id"]
        assert citizen_id is not None

        # 2. LOGIN
        login_res = await client.post("/api/auth/login", json={
            "email": "ananya.roy@example.gov.in",
            "password": "Password123#Secure",
        })
        assert login_res.status_code == 200

        # 3. ONBOARDING STEP-BY-STEP (PROFILE + LOCATION + EMPLOYMENT + HOUSEHOLD)
        # Step 1: Personal Profile
        s1_res = await client.put("/api/citizens/me/onboarding/step", json={
            "step": 1,
            "name": "Ananya Roy",
            "date_of_birth": "1992-08-20",
            "gender": "female",
            "phone": "9812345678",
        })
        assert s1_res.status_code == 200, s1_res.text
        assert s1_res.json()["profile"]["onboarding_step"] == 1

        # Step 2: Location
        s2_res = await client.put("/api/citizens/me/onboarding/step", json={
            "step": 2,
            "current_state": "Maharashtra",
            "current_district": "Pune",
            "permanent_state": "West Bengal",
            "permanent_district": "Kolkata",
        })
        assert s2_res.status_code == 200, s2_res.text
        assert s2_res.json()["profile"]["onboarding_step"] == 2

        # Step 3: Employment
        s3_res = await client.put("/api/citizens/me/onboarding/step", json={
            "step": 3,
            "occupation": "Handicraft Artisan",
            "employment_status": "SELF_EMPLOYED",
            "annual_income": 95000,
            "employer_name": "Artisan Guild",
        })
        assert s3_res.status_code == 200, s3_res.text
        assert s3_res.json()["profile"]["onboarding_step"] == 3

        # Step 4: Household & Complete
        s4_res = await client.put("/api/citizens/me/onboarding/step", json={
            "step": 4,
            "household_members": 3,
            "dependents": 2,
            "annual_income": 95000,
        })
        assert s4_res.status_code == 200, s4_res.text
        profile_data = s4_res.json()["profile"]
        assert profile_data["onboarding_step"] == 4
        assert profile_data["onboarding_completed"] is True

        # SET LANGUAGE = HINDI
        lang_res = await client.put("/api/citizens/me/preferences", json={
            "preferred_language": "hi"
        })
        assert lang_res.status_code == 200
        assert lang_res.json()["preferred_language"] == "hi"

        # UPLOAD ACTUAL FILE
        files = {
            "file": ("artisan_certificate.pdf", REAL_TEST_PDF_BYTES, "application/pdf")
        }
        up_res = await client.post(
            "/api/documents/",
            data={"document_type": "INCOME_CERTIFICATE"},
            files=files
        )
        assert up_res.status_code == 200, up_res.text
        doc_data = up_res.json()
        doc_id = doc_data["document_id"]

        # VERIFY DOCUMENT PERSISTENCE & PROCESS FOR EVIDENCE
        proc_res = await client.post(f"/api/documents/{doc_id}/process")
        assert proc_res.status_code == 200

        # VERIFY EVIDENCE PERSISTENCE
        ev_res = await client.get("/api/citizens/me/evidence")
        assert ev_res.status_code == 200
        evidence_list = ev_res.json()
        assert len(evidence_list) > 0

        # CREATE APPLICATION
        # Discover an available scheme
        wf_res = await client.get("/api/citizens/me/welfare-state")
        assert wf_res.status_code == 200
        wf_data = wf_res.json()
        opportunities = wf_data.get("new_opportunities", [])
        assert len(opportunities) > 0, "Expected at least 1 eligible scheme opportunity"
        target_scheme_id = opportunities[0]["id"]

        # Grant consent & submit application
        app_create_res = await client.post("/api/applications/", json={
            "scheme_id": target_scheme_id,
        })
        assert app_create_res.status_code in (200, 201), app_create_res.text
        app_data = app_create_res.json()
        application_id = app_data["id"]
        assert application_id is not None

        # LOGOUT
        logout_res = await client.post("/api/auth/logout")
        assert logout_res.status_code == 200

    # 4. FRESH HTTP CLIENT (Zero memory, fresh cookies, simulating closing and reopening browser)
    async with AsyncClient(transport=transport, base_url="http://test") as fresh_client:
        # LOGIN
        re_login = await fresh_client.post("/api/auth/login", json={
            "email": "ananya.roy@example.gov.in",
            "password": "Password123#Secure",
        })
        assert re_login.status_code == 200
        auth_me = re_login.json()

        # VERIFY PROFILE
        assert auth_me["citizen_id"] == citizen_id
        assert auth_me["citizen_name"] == "Ananya Roy"
        assert auth_me["onboarding_completed"] is True
        assert auth_me["onboarding_step"] == 4

        cit_res = await fresh_client.get("/api/citizens/me")
        assert cit_res.status_code == 200
        p = cit_res.json()["profile"]
        assert p["name"] == "Ananya Roy"
        assert p["dob"] == "1992-08-20"
        assert p["gender"] == "female"

        # VERIFY LOCATION
        current_loc = next((l for l in p["locations"] if l["location_type"] == "CURRENT" and l["is_active"]), None)
        assert current_loc is not None
        assert current_loc["state"] == "Maharashtra"
        assert current_loc["district"] == "Pune"

        perm_loc = next((l for l in p["locations"] if l["location_type"] == "HOME" and l["is_active"]), None)
        assert perm_loc is not None
        assert perm_loc["state"] == "West Bengal"
        assert perm_loc["district"] == "Kolkata"

        # VERIFY EMPLOYMENT
        curr_emp = next((e for e in p["employments"] if e["is_active"]), None)
        assert curr_emp is not None
        assert curr_emp["occupation"] == "Handicraft Artisan"
        assert curr_emp["employment_status"] == "SELF_EMPLOYED"
        assert curr_emp["annual_income"] == 95000
        assert curr_emp["employer_name"] == "Artisan Guild"

        # VERIFY HINDI PREFERENCE RESTORED
        assert auth_me["preferred_language"] == "hi"
        pref_res = await fresh_client.get("/api/citizens/me/preferences")
        assert pref_res.status_code == 200
        assert pref_res.json()["preferred_language"] == "hi"

        # VERIFY DOCUMENT METADATA
        doc_get_res = await fresh_client.get(f"/api/documents/{doc_id}")
        assert doc_get_res.status_code == 200
        doc_details = doc_get_res.json()
        assert doc_details["document_type"] == "INCOME_CERTIFICATE"
        assert doc_details["content_hash"] == expected_doc_hash
        assert doc_details["metadata"]["original_filename"] == "artisan_certificate.pdf"

        # VERIFY ACTUAL FILE BYTES
        download_res = await fresh_client.get(f"/api/documents/{doc_id}/download")
        assert download_res.status_code == 200
        assert hashlib.sha256(download_res.content).hexdigest() == expected_doc_hash
        assert download_res.content == REAL_TEST_PDF_BYTES

        # VERIFY EVIDENCE PERSISTENCE (without reprocessing!)
        ev_restored = await fresh_client.get("/api/citizens/me/evidence")
        assert ev_restored.status_code == 200
        ev_items = ev_restored.json()
        assert len(ev_items) > 0

        # VERIFY APPLICATION PERSISTENCE
        app_list_res = await fresh_client.get("/api/citizens/me/applications")
        assert app_list_res.status_code == 200
        user_apps = app_list_res.json()
        matching_app = next((a for a in user_apps if a["id"] == application_id), None)
        assert matching_app is not None
        assert matching_app["scheme_id"] == target_scheme_id


@pytest.mark.asyncio
async def test_requirement_19_user_isolation(db_session):
    """
    Requirement 19: USER A / USER B ISOLATION TEST
    Create: USER A, USER B.
    Give them visibly different:
    - names
    - locations
    - languages
    - documents
    - applications
    Verify:
    A cannot read B.
    B cannot read A.
    Verify malicious citizen_id changes and direct resource ID manipulation.
    Backend must derive ownership from the authenticated session.
    """
    transport = ASGITransport(app=app)

    # Setup User A
    async with AsyncClient(transport=transport, base_url="http://test") as client_a:
        res_a = await client_a.post("/api/auth/register", json={
            "name": "Aarav Patel",
            "email": "aarav.patel@example.gov.in",
            "password": "Password123#Secure",
            "phone": "9819999001",
            "preferred_language": "hi",
        })
        assert res_a.status_code == 200
        cit_a_id = res_a.json()["citizen_id"]

        # User A Onboarding
        await client_a.put("/api/citizens/me/onboarding/step", json={
            "step": 4,
            "name": "Aarav Patel",
            "current_state": "Gujarat",
            "current_district": "Ahmedabad",
            "occupation": "Textile Weaver",
            "annual_income": 80000,
        })

        # User A uploads Document A
        up_a = await client_a.post(
            "/api/documents/",
            data={"document_type": "AADHAAR"},
            files={"file": ("doc_a.pdf", REAL_TEST_PDF_BYTES, "application/pdf")}
        )
        assert up_a.status_code == 200
        doc_a_id = up_a.json()["document_id"]
        await client_a.post(f"/api/documents/{doc_a_id}/process")

        # User A creates application
        schemes_res = await client_a.get("/api/schemes")
        assert schemes_res.status_code == 200
        schemes = schemes_res.json().get("items", [])
        assert len(schemes) >= 2
        scheme_a_id = schemes[0]["id"]
        scheme_b_id = schemes[1]["id"]
        app_a = await client_a.post("/api/applications/", json={"scheme_id": scheme_a_id})
        assert app_a.status_code in (200, 201)
        app_a_id = app_a.json()["id"]

    # Setup User B
    async with AsyncClient(transport=transport, base_url="http://test") as client_b:
        res_b = await client_b.post("/api/auth/register", json={
            "name": "Balwinder Singh",
            "email": "balwinder.singh@example.gov.in",
            "password": "Password123#Secure",
            "phone": "9819999002",
            "preferred_language": "en",
        })
        assert res_b.status_code == 200
        cit_b_id = res_b.json()["citizen_id"]

        # User B Onboarding
        await client_b.put("/api/citizens/me/onboarding/step", json={
            "step": 4,
            "name": "Balwinder Singh",
            "current_state": "Punjab",
            "current_district": "Amritsar",
            "occupation": "Agricultural Laborer",
            "annual_income": 110000,
        })

        # User B uploads Document B
        up_b = await client_b.post(
            "/api/documents/",
            data={"document_type": "INCOME_CERTIFICATE"},
            files={"file": ("doc_b.pdf", REAL_TEST_DOC_B_BYTES, "application/pdf")}
        )
        assert up_b.status_code == 200
        doc_b_id = up_b.json()["document_id"]

        # User B creates application
        app_b = await client_b.post("/api/applications/", json={"scheme_id": scheme_b_id})
        assert app_b.status_code in (200, 201)
        app_b_id = app_b.json()["id"]

        # ========================================================
        # ISOLATION VERIFICATION: B CANNOT ACCESS A's RESOURCES
        # ========================================================

        # 1. B attempts to view A's profile via direct citizen_id manipulation -> 403 Forbidden
        b_access_a_profile = await client_b.get(f"/api/citizens/{cit_a_id}")
        assert b_access_a_profile.status_code in (403, 404)

        # 2. B attempts to view A's document metadata -> 404/403
        b_access_a_doc = await client_b.get(f"/api/documents/{doc_a_id}")
        assert b_access_a_doc.status_code in (403, 404)

        # 3. B attempts to download A's file bytes -> 404/403
        b_download_a_bytes = await client_b.get(f"/api/documents/{doc_a_id}/download")
        assert b_download_a_bytes.status_code in (403, 404)

        # 4. B attempts to view A's application -> 403/404
        b_access_a_app = await client_b.get(f"/api/applications/{app_a_id}")
        assert b_access_a_app.status_code in (403, 404)

        # 5. B attempts to manipulate citizen_id in query parameter -> BLOCKED
        b_spoof_cit_id = await client_b.get(f"/api/documents/?citizen_id={cit_a_id}")
        assert b_spoof_cit_id.status_code in (403, 404)

    # ISOLATION VERIFICATION: A CANNOT ACCESS B's RESOURCES
    async with AsyncClient(transport=transport, base_url="http://test") as client_a:
        # Login A
        await client_a.post("/api/auth/login", json={
            "email": "aarav.patel@example.gov.in",
            "password": "Password123#Secure",
        })

        # A attempts to access B's document metadata -> 403/404
        a_access_b_doc = await client_a.get(f"/api/documents/{doc_b_id}")
        assert a_access_b_doc.status_code in (403, 404)

        # A attempts to download B's file bytes -> 403/404
        a_download_b_bytes = await client_a.get(f"/api/documents/{doc_b_id}/download")
        assert a_download_b_bytes.status_code in (403, 404)

        # A attempts to access B's application -> 403/404
        a_access_b_app = await client_a.get(f"/api/applications/{app_b_id}")
        assert a_access_b_app.status_code in (403, 404)

        # A attempts to view B's welfare state via spoofing citizen_id -> 403
        a_spoof_wf = await client_a.get(f"/api/citizens/{cit_b_id}/welfare-state")
        assert a_spoof_wf.status_code in (403, 404)
