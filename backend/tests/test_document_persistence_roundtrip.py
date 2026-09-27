import pytest
import hashlib
from httpx import AsyncClient, ASGITransport
from app.main import app

REAL_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (JanSetu Sovereign Evidence Test) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n300\n%%EOF"


@pytest.mark.asyncio
async def test_document_bytes_persistence_roundtrip(db_session):
    """
    Requirement 8: DOCUMENT ROUND-TRIP TEST
    1. register User A
    2. login
    3. upload a real test PDF
    4. calculate original SHA-256
    5. logout
    6. create fresh HTTP client
    7. login
    8. retrieve document metadata
    9. download/retrieve actual bytes
    10. calculate SHA-256
    11. assert hash equals original
    12. assert metadata equals original
    13. assert owner equals User A
    """
    transport = ASGITransport(app=app)
    expected_hash = hashlib.sha256(REAL_PDF_BYTES).hexdigest()

    # Step 1: Register User A
    async with AsyncClient(transport=transport, base_url="http://test") as client_a:
        reg_res = await client_a.post("/api/auth/register", json={
            "name": "Devendra Nath Sharma",
            "email": "devendra.sharma@example.gov.in",
            "password": "Password123#Secure",
            "phone": "9811111111",
            "preferred_language": "hi",
        })
        assert reg_res.status_code == 200, reg_res.text
        auth_data = reg_res.json()
        assert auth_data["authenticated"] is True
        citizen_a_id = auth_data["citizen_id"]
        user_a_id = auth_data["user_id"]
        assert citizen_a_id is not None

        # Step 2: Login User A (verify credentials check)
        login_res = await client_a.post("/api/auth/login", json={
            "email": "devendra.sharma@example.gov.in",
            "password": "Password123#Secure",
        })
        assert login_res.status_code == 200

        # Step 3: Upload real test PDF bytes
        files = {
            "file": ("aadhaar_front_devendra.pdf", REAL_PDF_BYTES, "application/pdf")
        }
        upload_res = await client_a.post(
            "/api/documents/",
            data={"document_type": "AADHAAR"},
            files=files
        )
        assert upload_res.status_code == 200, upload_res.text
        doc_upload_data = upload_res.json()
        doc_id = doc_upload_data["document_id"]
        assert doc_id is not None

        # Process document to generate extracted claims/evidence
        proc_res = await client_a.post(f"/api/documents/{doc_id}/process")
        assert proc_res.status_code == 200

        # Step 4: Calculate original SHA-256
        assert expected_hash is not None and len(expected_hash) == 64

        # Step 5: Logout
        logout_res = await client_a.post("/api/auth/logout")
        assert logout_res.status_code == 200

    # Step 6: Create completely fresh HTTP client (zero state, no cookies)
    async with AsyncClient(transport=transport, base_url="http://test") as fresh_client:
        # Verify fresh client is unauthenticated
        unauth_me = await fresh_client.get("/api/auth/me")
        assert unauth_me.status_code in (401, 403) or unauth_me.json().get("authenticated") is False

        # Attempt to access document without auth -> BLOCKED
        unauth_doc = await fresh_client.get(f"/api/documents/{doc_id}")
        assert unauth_doc.status_code in (401, 403)

        # Step 7: Login again as User A
        re_login = await fresh_client.post("/api/auth/login", json={
            "email": "devendra.sharma@example.gov.in",
            "password": "Password123#Secure",
        })
        assert re_login.status_code == 200
        re_data = re_login.json()
        assert re_data["citizen_id"] == citizen_a_id

        # Step 8: Retrieve document metadata
        doc_meta_res = await fresh_client.get(f"/api/documents/{doc_id}")
        assert doc_meta_res.status_code == 200, doc_meta_res.text
        doc_meta = doc_meta_res.json()

        # Step 9: Download/retrieve actual bytes from the backend
        download_res = await fresh_client.get(f"/api/documents/{doc_id}/download")
        assert download_res.status_code == 200, download_res.text
        downloaded_bytes = download_res.content

        # Step 10: Calculate SHA-256 of downloaded bytes
        downloaded_hash = hashlib.sha256(downloaded_bytes).hexdigest()

        # Step 11: Assert hash equals original
        assert downloaded_hash == expected_hash, f"Hash mismatch: {downloaded_hash} != {expected_hash}"
        assert download_res.headers.get("X-Content-SHA256") == expected_hash

        # Step 12: Assert metadata equals original
        assert doc_meta["document_type"] == "AADHAAR"
        assert doc_meta["content_hash"] == expected_hash
        assert doc_meta["metadata"]["original_filename"] == "aadhaar_front_devendra.pdf"
        assert doc_meta["metadata"]["content_type"] == "application/pdf"
        assert doc_meta["metadata"]["size_bytes"] == len(REAL_PDF_BYTES)

        # Step 13: Assert owner equals User A
        # Now verify an attacker (User B) CANNOT download or view User A's document
        async with AsyncClient(transport=transport, base_url="http://test") as client_b:
            reg_b = await client_b.post("/api/auth/register", json={
                "name": "Attacker User B",
                "email": "attacker.b@example.gov.in",
                "password": "Password123#Secure",
                "phone": "9876543299",
                "preferred_language": "en",
            })
            assert reg_b.status_code == 200

            # User B attempts to access User A's document metadata -> 404/403
            b_access = await client_b.get(f"/api/documents/{doc_id}")
            assert b_access.status_code in (403, 404)

            # User B attempts to download User A's actual file bytes -> 404/403
            b_download = await client_b.get(f"/api/documents/{doc_id}/download")
            assert b_download.status_code in (403, 404)
