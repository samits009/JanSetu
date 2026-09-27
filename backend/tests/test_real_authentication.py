import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.main import app
from app.models.identity import User, AuthSession, Identity
from app.models.citizen import Citizen


@pytest.mark.asyncio
async def test_register_creates_user_and_session(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "name": "Pooja Sharma",
            "email": "pooja@example.com",
            "phone": "9876500001",
            "password": "Password123!",
            "preferred_language": "hi"
        }
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["authenticated"] is True
        assert data["citizen_name"] == "Pooja Sharma"
        assert data["email"] == "pooja@example.com"
        assert data["phone"] in ("9876500001", "+919876500001")
        assert data["preferred_language"] == "hi"
        assert data["citizen_id"] is not None
        assert data["user_id"] is not None

        # Verify cookie set
        assert "jansetu_session" in resp.cookies

        # Verify DB records
        user = (await db_session.execute(select(User).where(User.email == "pooja@example.com"))).scalars().first()
        assert user is not None
        assert user.password_hash != "Password123!" # Must be hashed!
        assert "$" in user.password_hash

        citizen = await db_session.get(Citizen, user.citizen_id)
        assert citizen is not None
        assert citizen.name == "Pooja Sharma"


@pytest.mark.asyncio
async def test_register_duplicate_email_blocked(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "name": "User One",
            "email": "duplicate@example.com",
            "phone": "9876500002",
            "password": "Password123!",
            "preferred_language": "hi"
        }
        res1 = await client.post("/api/auth/register", json=payload)
        assert res1.status_code == 200

        # Duplicate email
        res2 = await client.post("/api/auth/register", json={
            "name": "User Two",
            "email": "duplicate@example.com",
            "phone": "9876500003",
            "password": "DifferentPassword123!",
            "preferred_language": "en"
        })
        assert res2.status_code == 400
        assert "already exists" in res2.text


@pytest.mark.asyncio
async def test_login_success_and_failure(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user
        reg_payload = {
            "name": "Anil Kumar",
            "email": "anil@example.com",
            "phone": "9876500004",
            "password": "SecurePassword123!",
            "preferred_language": "en"
        }
        await client.post("/api/auth/register", json=reg_payload)

        # 1. Login with wrong password
        fail_resp = await client.post("/api/auth/login", json={
            "username": "anil@example.com",
            "password": "WrongPassword!"
        })
        assert fail_resp.status_code == 401

        # 2. Login with correct email
        success_email = await client.post("/api/auth/login", json={
            "username": "anil@example.com",
            "password": "SecurePassword123!"
        })
        assert success_email.status_code == 200
        assert success_email.json()["citizen_name"] == "Anil Kumar"
        assert "jansetu_session" in success_email.cookies

        # 3. Login with phone number
        success_phone = await client.post("/api/auth/login", json={
            "username": "9876500004",
            "password": "SecurePassword123!"
        })
        assert success_phone.status_code == 200
        assert success_phone.json()["email"] == "anil@example.com"


@pytest.mark.asyncio
async def test_me_and_logout(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Unauthenticated /api/auth/me should fail
        unauth_resp = await client.get("/api/auth/me")
        assert unauth_resp.status_code == 401

        # Register and login
        await client.post("/api/auth/register", json={
            "name": "Sunita Devi",
            "email": "sunita@example.com",
            "phone": "9876500005",
            "password": "Password123!",
            "preferred_language": "hi"
        })

        # /api/auth/me with session cookie
        me_resp = await client.get("/api/auth/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["citizen_name"] == "Sunita Devi"

        # Logout
        logout_resp = await client.post("/api/auth/logout")
        assert logout_resp.status_code == 200
        assert logout_resp.json()["authenticated"] is False

        # After logout, me should fail
        after_logout = await client.get("/api/auth/me")
        assert after_logout.status_code == 401


@pytest.mark.asyncio
async def test_user_ownership_isolation(db_session):
    """User A cannot access User B resources."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client_a:
        # User A
        reg_a = await client_a.post("/api/auth/register", json={
            "name": "User Alpha",
            "email": "alpha@example.com",
            "phone": "9876500010",
            "password": "Password123!"
        })
        assert reg_a.status_code == 200
        citizen_id_a = reg_a.json()["citizen_id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client_b:
        # User B
        reg_b = await client_b.post("/api/auth/register", json={
            "name": "User Beta",
            "email": "beta@example.com",
            "phone": "9876500020",
            "password": "Password123!"
        })
        assert reg_b.status_code == 200
        citizen_id_b = reg_b.json()["citizen_id"]

        # User B attempts to access User A's welfare state
        resp = await client_b.get(f"/api/citizens/{citizen_id_a}/welfare-state")
        assert resp.status_code == 403
        assert "access denied" in resp.text.lower()

        # User B accessing their own welfare state succeeds
        own_resp = await client_b.get(f"/api/citizens/{citizen_id_b}/welfare-state")
        assert own_resp.status_code == 200

        # User B accessing via /me route
        me_resp = await client_b.get("/api/citizens/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["profile"]["name"] == "User Beta"


@pytest.mark.asyncio
async def test_real_citizen_onboarding_persistence(db_session):
    """Real onboarding updates citizen, location, employment, household."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post("/api/auth/register", json={
            "name": "Kavita Rao",
            "email": "kavita@example.com",
            "phone": "9876500099",
            "password": "Password123!"
        })
        assert reg.status_code == 200

        onboarding_payload = {
            "name": "Kavita Rao",
            "dob": "1992-04-15",
            "gender": "FEMALE",
            "current_state": "Delhi",
            "current_district": "Central Delhi",
            "permanent_state": "Uttar Pradesh",
            "permanent_district": "Varanasi",
            "occupation": "Construction Worker",
            "employer_name": "Delhi Metro Rail",
            "annual_income": 95000,
            "household_members_count": 3
        }

        ob_resp = await client.post("/api/citizens/me/onboarding", json=onboarding_payload)
        assert ob_resp.status_code == 200
        data = ob_resp.json()["profile"]
        assert data["name"] == "Kavita Rao"
        assert len(data["locations"]) >= 2
        assert any(l["district"] == "Central Delhi" for l in data["locations"])
        assert any(l["state"] == "Uttar Pradesh" for l in data["locations"])
        assert any(e["occupation"] == "Construction Worker" for e in data["employments"])

        # Check welfare state immediately calculates without errors
        ws_resp = await client.get("/api/citizens/me/welfare-state")
        assert ws_resp.status_code == 200
        ws = ws_resp.json()
        assert ws["citizen_summary"]["name"] == "Kavita Rao"


@pytest.mark.asyncio
async def test_expired_session_denied(db_session):
    """An expired session token is rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post("/api/auth/register", json={
            "name": "Expired Test User",
            "email": "expired@example.com",
            "password": "Password123!"
        })
        assert reg.status_code == 200
        
        # Verify authenticated
        me = await client.get("/api/auth/me")
        assert me.status_code == 200
        
        # Manually expire the session in the DB
        sessions = (await db_session.execute(select(AuthSession))).scalars().all()
        for s in sessions:
            s.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        await db_session.commit()
        
        # Request should now be denied
        expired_me = await client.get("/api/auth/me")
        assert expired_me.status_code == 401
        assert "expired" in expired_me.text.lower()


@pytest.mark.asyncio
async def test_revoked_session_denied(db_session):
    """A revoked session token is rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reg = await client.post("/api/auth/register", json={
            "name": "Revoked Test User",
            "email": "revoked@example.com",
            "password": "Password123!"
        })
        assert reg.status_code == 200
        
        # Verify authenticated
        me = await client.get("/api/auth/me")
        assert me.status_code == 200
        
        # Manually revoke the session in the DB
        sessions = (await db_session.execute(select(AuthSession))).scalars().all()
        for s in sessions:
            s.revoked_at = datetime.now(timezone.utc)
        await db_session.commit()
        
        # Request should now be denied
        revoked_me = await client.get("/api/auth/me")
        assert revoked_me.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_endpoints_blocked(db_session):
    """Unauthenticated access to citizen-facing endpoints is rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # All of these must fail without a session
        assert (await client.get("/api/auth/me")).status_code == 401
        assert (await client.get("/api/citizens/me")).status_code == 401
        assert (await client.get("/api/citizens/me/welfare-state")).status_code == 401
        assert (await client.get("/api/citizens/me/benefits")).status_code == 401
        assert (await client.get("/api/citizens/me/documents")).status_code == 401
        assert (await client.get("/api/citizens/me/evidence")).status_code == 401
        assert (await client.get("/api/citizens/me/applications")).status_code == 401
        assert (await client.post("/api/agent/chat", json={"message": "hello"})).status_code == 401

