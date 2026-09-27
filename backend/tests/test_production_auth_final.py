import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.main import app
from app.models.identity import User, AuthSession, AuthIdentity, Identity
from app.models.citizen import Citizen
from app.services.google_oauth import google_oauth_service


@pytest.mark.asyncio
async def test_register_with_gmail(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/auth/register", json={
            "name": "Aarav Sharma",
            "email": "aarav.sharma@gmail.com",
            "mobile_number": "+91 9811122233",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
        })
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["authenticated"] is True
        assert data["email"] == "aarav.sharma@gmail.com"
        assert data["mobile_number"] == "+919811122233"
        assert "jansetu_session" in resp.cookies


@pytest.mark.asyncio
async def test_register_with_icloud(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/auth/register", json={
            "name": "Diya Patel",
            "email": "diya.patel@icloud.com",
            "mobile_number": "09822233344",
            "password": "SecurePassword123!",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "diya.patel@icloud.com"
        assert resp.json()["mobile_number"] == "+919822233344"


@pytest.mark.asyncio
async def test_register_with_outlook(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/auth/register", json={
            "name": "Rohan Verma",
            "email": "rohan.verma@outlook.com",
            "mobile_number": "919833344455",
            "password": "SecurePassword123!",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "rohan.verma@outlook.com"
        assert resp.json()["mobile_number"] == "+919833344455"


@pytest.mark.asyncio
async def test_register_with_yahoo(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/auth/register", json={
            "name": "Meera Sen",
            "email": "meera.sen@yahoo.com",
            "mobile_number": "9844455566",
            "password": "SecurePassword123!",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "meera.sen@yahoo.com"
        assert resp.json()["mobile_number"] == "+919844455566"


@pytest.mark.asyncio
async def test_register_with_custom_domain(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Academic / Enterprise domains
        resp = await client.post("/api/auth/register", json={
            "name": "Dr. Rajesh Gupta",
            "email": "rgupta@iitd.ac.in",
            "mobile_number": "+91-9855566677",
            "password": "SecurePassword123!",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "rgupta@iitd.ac.in"
        assert resp.json()["mobile_number"] == "+919855566677"


@pytest.mark.asyncio
async def test_duplicate_email(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post("/api/auth/register", json={
            "name": "Duplicate Test One",
            "email": "first.unique@domain.com",
            "mobile_number": "9866677788",
            "password": "Password123!",
        })
        assert first.status_code == 200

        second = await client.post("/api/auth/register", json={
            "name": "Duplicate Test Two",
            "email": "first.unique@domain.com",  # Duplicate email
            "mobile_number": "9866677789",
            "password": "Password123!",
        })
        assert second.status_code == 400
        assert "email" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_duplicate_mobile(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post("/api/auth/register", json={
            "name": "Mobile Test One",
            "email": "mobile1@domain.com",
            "mobile_number": "9877788899",
            "password": "Password123!",
        })
        assert first.status_code == 200

        # Try registering with same mobile in different formatting
        second = await client.post("/api/auth/register", json={
            "name": "Mobile Test Two",
            "email": "mobile2@domain.com",
            "mobile_number": "+91 98777 88899",  # Same canonical number
            "password": "Password123!",
        })
        assert second.status_code == 400
        assert "mobile" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_with_email(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/register", json={
            "name": "Email Login User",
            "email": "email.login@domain.com",
            "mobile_number": "9888899900",
            "password": "StrongPassword123!",
        })

        resp = await client.post("/api/auth/login", json={
            "email": "email.login@domain.com",
            "password": "StrongPassword123!",
        })
        assert resp.status_code == 200
        assert resp.json()["citizen_name"] == "Email Login User"
        assert "jansetu_session" in resp.cookies


@pytest.mark.asyncio
async def test_login_with_mobile(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/register", json={
            "name": "Mobile Login User",
            "email": "mobile.login@domain.com",
            "mobile_number": "9899900011",
            "password": "StrongPassword123!",
        })

        # Login using raw 10-digit mobile
        resp1 = await client.post("/api/auth/login", json={
            "username": "9899900011",
            "password": "StrongPassword123!",
        })
        assert resp1.status_code == 200
        assert resp1.json()["email"] == "mobile.login@domain.com"

        # Login using +91 formatted mobile
        resp2 = await client.post("/api/auth/login", json={
            "username": "+91 9899900011",
            "password": "StrongPassword123!",
        })
        assert resp2.status_code == 200
        assert resp2.json()["email"] == "mobile.login@domain.com"


@pytest.mark.asyncio
async def test_invalid_password(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/register", json={
            "name": "Password User",
            "email": "pwd.user@domain.com",
            "mobile_number": "9812345678",
            "password": "CorrectPassword123!",
        })

        resp = await client.post("/api/auth/login", json={
            "email": "pwd.user@domain.com",
            "password": "WrongPassword!",
        })
        assert resp.status_code == 401
        assert "invalid" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_session_persistence(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        reg = await client.post("/api/auth/register", json={
            "name": "Persistence User",
            "email": "persist@domain.com",
            "mobile_number": "9823456789",
            "password": "Password123!",
        })
        assert reg.status_code == 200
        cookie = reg.cookies.get("jansetu_session")
        assert cookie is not None

        # Authenticated request without Authorization header relies purely on HTTP-only cookie
        me_resp = await client.get("/api/auth/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "persist@domain.com"


@pytest.mark.asyncio
async def test_logout(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/register", json={
            "name": "Logout User",
            "email": "logout@domain.com",
            "mobile_number": "9834567890",
            "password": "Password123!",
        })

        logout_resp = await client.post("/api/auth/logout")
        assert logout_resp.status_code == 200
        assert logout_resp.json()["authenticated"] is False

        # Session should now be revoked
        me_resp = await client.get("/api/auth/me")
        assert me_resp.status_code == 401


@pytest.mark.asyncio
async def test_user_isolation(db_session):
    """User A's session cannot access User B's citizen details or records."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client_a:
        res_a = await client_a.post("/api/auth/register", json={
            "name": "User Alpha",
            "email": "alpha.iso@domain.com",
            "mobile_number": "9845678901",
            "password": "Password123!",
        })
        citizen_id_a = res_a.json()["citizen_id"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client_b:
        res_b = await client_b.post("/api/auth/register", json={
            "name": "User Beta",
            "email": "beta.iso@domain.com",
            "mobile_number": "9856789012",
            "password": "Password123!",
        })
        citizen_id_b = res_b.json()["citizen_id"]

        # Attempt to access User A's citizen data using User B's session
        unauth_resp = await client_b.get(f"/api/citizens/{citizen_id_a}/welfare-state")
        assert unauth_resp.status_code == 403

        # Accessing own citizen profile succeeds
        own_resp = await client_b.get("/api/citizens/me")
        assert own_resp.status_code == 200
        assert own_resp.json()["profile"]["name"] == "User Beta"


@pytest.mark.asyncio
async def test_google_state_validation():
    """State generation and CSRF validation."""
    state = google_oauth_service.generate_state(ttl_seconds=60)
    assert len(state) >= 32
    assert google_oauth_service.validate_state(state) is True
    # Second validation of same state must fail (one-time use)
    assert google_oauth_service.validate_state(state) is False
    # Random or unknown state must fail
    assert google_oauth_service.validate_state("non-existent-state") is False


@pytest.mark.asyncio
async def test_google_identity_creation(db_session, monkeypatch):
    """First-time Google login creates citizen, user, auth_identity, and redirects to onboarding."""
    fake_sub = "google-sub-unique-12345"
    fake_email = "new.google.user@example.com"
    fake_name = "New Google User"

    # Stub Google provider interactions for test suite
    async def mock_exchange(code):
        return {"access_token": "mock-access-token"}

    async def mock_user_info(token):
        return {
            "sub": fake_sub,
            "email": fake_email,
            "name": fake_name,
            "email_verified": True,
        }

    monkeypatch.setattr(google_oauth_service, "exchange_code", mock_exchange)
    monkeypatch.setattr(google_oauth_service, "get_user_info", mock_user_info)
    valid_state = google_oauth_service.generate_state()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        resp = await client.get(f"/api/auth/google/callback?code=mock_code&state={valid_state}")
        assert resp.status_code == 302
        assert "/onboarding" in resp.headers["location"]
        assert "jansetu_session" in resp.cookies

        # Verify DB records
        auth_id = (await db_session.execute(
            select(AuthIdentity).where(AuthIdentity.provider == "google", AuthIdentity.provider_subject == fake_sub)
        )).scalars().first()
        assert auth_id is not None
        assert auth_id.provider_email == fake_email

        user = await db_session.get(User, auth_id.user_id)
        assert user is not None
        assert user.email == fake_email
        assert user.password_hash is None  # OAuth-only user has no local password hash
        assert user.email_verified is True
        assert user.mobile_number is None  # Must be completed in onboarding


@pytest.mark.asyncio
async def test_google_identity_login(db_session, monkeypatch):
    """Returning Google user signs in directly to Home / Onboarding."""
    fake_sub = "google-sub-returning-789"
    fake_email = "returning.google@example.com"

    async def mock_exchange(code):
        return {"access_token": "mock-access-token"}

    async def mock_user_info(token):
        return {
            "sub": fake_sub,
            "email": fake_email,
            "name": "Returning Google User",
            "email_verified": True,
        }

    monkeypatch.setattr(google_oauth_service, "exchange_code", mock_exchange)
    monkeypatch.setattr(google_oauth_service, "get_user_info", mock_user_info)

    # 1. First signup
    state1 = google_oauth_service.generate_state()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        res1 = await client.get(f"/api/auth/google/callback?code=code1&state={state1}")
        assert res1.status_code == 302

    # 2. Returning login
    state2 = google_oauth_service.generate_state()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        res2 = await client.get(f"/api/auth/google/callback?code=code2&state={state2}")
        assert res2.status_code == 302
        assert "jansetu_session" in res2.cookies


@pytest.mark.asyncio
async def test_google_account_linking(db_session, monkeypatch):
    """
    Scenario: User already created email+password account.
    Attempts Google sign-in with matching email -> Collision detected -> Safe password linking.
    """
    email = "existing.password.user@domain.com"
    password = "OriginalPassword123!"
    sub = "google-sub-link-999"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register standard password account
        reg = await client.post("/api/auth/register", json={
            "name": "Pre-existing User",
            "email": email,
            "mobile_number": "9898989898",
            "password": password,
        })
        assert reg.status_code == 200

    # User attempts Google sign-in
    async def mock_exchange(code):
        return {"access_token": "mock-access-token"}

    async def mock_user_info(token):
        return {
            "sub": sub,
            "email": email,
            "name": "Pre-existing User",
            "email_verified": True,
        }

    monkeypatch.setattr(google_oauth_service, "exchange_code", mock_exchange)
    monkeypatch.setattr(google_oauth_service, "get_user_info", mock_user_info)
    state = google_oauth_service.generate_state()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        res = await client.get(f"/api/auth/google/callback?code=code&state={state}")
        assert res.status_code == 302
        # Redirects to account linking prompt with query parameters
        location = res.headers["location"]
        assert "mode=link_google" in location
        assert "existing.password.user%40domain.com" in location

    # User completes explicit linking with their password
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        link_resp = await client.post("/api/auth/link-google", json={
            "email": email,
            "password": password,
            "pending_sub": sub,
            "provider_email": email,
        })
        assert link_resp.status_code == 200
        assert link_resp.json()["authenticated"] is True
        assert link_resp.json()["google_linked"] is True

        # User now has both password and Google identity linked to ONE single User
        identities = (await db_session.execute(
            select(AuthIdentity).where(AuthIdentity.provider_email == email)
        )).scalars().all()
        providers = {i.provider for i in identities}
        assert "password" in providers
        assert "google" in providers


@pytest.mark.asyncio
async def test_new_user_redirect(db_session):
    """New registration redirects user context to onboarding."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/auth/register", json={
            "name": "New Onboarding User",
            "email": "new.redirect@domain.com",
            "mobile_number": "9870001122",
            "password": "Password123!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["onboarding_completed"] is False
        assert data["onboarding_step"] == 1


@pytest.mark.asyncio
async def test_existing_user_redirect(db_session):
    """Returning user who completed onboarding has onboarding_completed True."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        reg = await client.post("/api/auth/register", json={
            "name": "Completed Onboarding User",
            "email": "completed.ob@domain.com",
            "mobile_number": "9870003344",
            "password": "Password123!",
        })
        assert reg.status_code == 200
        citizen_id = reg.json()["citizen_id"]

        # Complete onboarding for citizen in database
        citizen = await db_session.get(Citizen, citizen_id)
        citizen.onboarding_completed = True
        citizen.onboarding_step = 4
        await db_session.commit()

        # Login returning user
        login_resp = await client.post("/api/auth/login", json={
            "email": "completed.ob@domain.com",
            "password": "Password123!",
        })
        assert login_resp.status_code == 200
        assert login_resp.json()["onboarding_completed"] is True


@pytest.mark.asyncio
async def test_deployment_readiness_endpoint(db_session):
    """Deployment readiness checks derive strictly from actual live system state."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/deployment/readiness")
        assert resp.status_code == 200
        data = resp.json()
        assert "checks" in data
        assert "DATABASE" in data["checks"]
        assert data["checks"]["DATABASE"]["status"] == "READY"
        assert "AUTH" in data["checks"]
        assert data["checks"]["AUTH"]["status"] == "READY"
        assert "GOOGLE_OAUTH" in data["checks"]
        assert data["checks"]["GOOGLE_OAUTH"]["status"] in ("READY", "CONFIG REQUIRED")

