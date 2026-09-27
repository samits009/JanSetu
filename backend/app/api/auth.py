from typing import Optional
from urllib.parse import quote_plus
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.citizen import Citizen
from app.models.identity import User
from app.schemas.auth import AuthResponse, LinkGoogleRequest, LoginRequest, RegisterRequest
from app.services.authentication import (
    AuthenticationService,
    GoogleAccountCollisionException,
    SESSION_COOKIE,
    SESSION_TTL,
    set_auth_cookie,
)
from app.services.authorization import get_current_identity
from app.services.google_oauth import google_oauth_service
from app.services.identity import IdentityPrincipal
from app.services.rate_limiter import auth_rate_limiter, google_rate_limiter
from app.repositories.application import AuditRepository
from app.services.audit import AuditService

router = APIRouter()


def _is_request_secure(request: Request) -> bool:
    """Determines if the incoming request is over HTTPS or behind an HTTPS proxy."""
    if request.url.scheme == "https":
        return True
    if request.headers.get("x-forwarded-proto") == "https":
        return True
    return False


def response_for(
    principal: IdentityPrincipal,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    mobile_number: Optional[str] = None,
    email_verified: bool = False,
    mobile_verified: bool = False,
    onboarding_completed: bool = False,
    onboarding_step: int = 1,
    token: Optional[str] = None,
    google_linked: bool = False,
) -> AuthResponse:
    effective_mobile = mobile_number or phone
    requires_mobile = not bool(effective_mobile)
    return AuthResponse(
        authenticated=True,
        user_id=principal.user_id,
        identity_id=principal.identity_id,
        role=principal.role,
        citizen_id=principal.citizen_id,
        verification_state=principal.verification_state,
        citizen_name=name,
        email=email,
        phone=effective_mobile,
        mobile_number=effective_mobile,
        preferred_language=principal.preferred_language or "hi",
        email_verified=email_verified,
        mobile_verified=mobile_verified,
        requires_mobile=requires_mobile,
        google_linked=google_linked,
        onboarding_completed=onboarding_completed,
        onboarding_step=onboarding_step,
        session_token=token,
        token=token,
    )


@router.post("/register", response_model=AuthResponse)
async def register(
    req: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Register a new JanSetu account (Path A).
    Validates name, email from any legitimate domain, Indian mobile number, and password.
    Creates user, citizen, identity, auth identity, and session in a single database transaction.
    """
    auth_rate_limiter.check(request, "register")
    auth_svc = AuthenticationService(db)

    mobile = req.get_mobile()
    token, principal, user = await auth_svc.register(
        name=req.name,
        password=req.password,
        email=req.email,
        phone=mobile,
        preferred_language=req.preferred_language,
    )

    if principal.citizen_id:
        audit = AuditService(AuditRepository(db))
        await audit.record(principal.citizen_id, "CITIZEN", "REGISTER", "Citizen registration", "SUCCESS")
        await audit.record(principal.citizen_id, "SYSTEM", "SESSION_CREATED", "Registration session", "SUCCESS")

    set_auth_cookie(response, token, is_secure=_is_request_secure(request))

    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None
    return response_for(
        principal,
        req.name,
        user.email,
        phone=user.phone,
        mobile_number=user.mobile_number,
        email_verified=user.email_verified,
        mobile_verified=user.mobile_verified,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Login with Email OR Mobile Number and password.
    Resolves identifier type and authenticates against authoritative PostgreSQL credentials.
    """
    auth_rate_limiter.check(request, "login")
    auth_svc = AuthenticationService(db)

    token, principal, user = await auth_svc.login(
        username=req.get_identifier(),
        password=req.password,
    )
    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None
    if principal.citizen_id:
        audit = AuditService(AuditRepository(db))
        await audit.record(principal.citizen_id, "CITIZEN", "LOGIN", "Citizen login", "SUCCESS")
        await audit.record(principal.citizen_id, "SYSTEM", "SESSION_CREATED", "Login session", "SUCCESS")

    set_auth_cookie(response, token, is_secure=_is_request_secure(request))

    return response_for(
        principal,
        citizen.name if citizen else None,
        user.email,
        phone=user.phone,
        mobile_number=user.mobile_number,
        email_verified=user.email_verified,
        mobile_verified=user.mobile_verified,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=token,
    )


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiates Google OAuth 2.0 Authorization Code flow.
    Generates cryptographically secure state and redirects the browser to real Google Sign-In.
    """
    google_rate_limiter.check(request, "google_login")
    frontend_url = google_oauth_service.frontend_url

    if not google_oauth_service.is_configured():
        # Inform frontend that Google credentials must be set
        return RedirectResponse(
            url=f"{frontend_url}/login?error=google_config_missing",
            status_code=302,
        )

    state = google_oauth_service.generate_state()
    auth_url = google_oauth_service.get_authorization_url(state)
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Google OAuth 2.0 redirect callback endpoint.
    1. Validates CSRF state nonce.
    2. Securely exchanges authorization code for tokens.
    3. Retrieves verified identity claims from Google OpenID Connect.
    4. Finds, creates, or initiates safe account-linking.
    5. Sets HTTP-only session cookie and redirects user to JanSetu app.
    """
    google_rate_limiter.check(request, "google_callback")
    frontend_url = google_oauth_service.frontend_url

    # Check for OAuth provider errors (e.g. user cancelled)
    if error:
        return RedirectResponse(
            url=f"{frontend_url}/login?error=google_cancelled",
            status_code=302,
        )

    if not code or not state:
        return RedirectResponse(
            url=f"{frontend_url}/login?error=invalid_request",
            status_code=302,
        )

    # Validate state against CSRF
    if not google_oauth_service.validate_state(state):
        return RedirectResponse(
            url=f"{frontend_url}/login?error=invalid_state",
            status_code=302,
        )

    try:
        token_data = await google_oauth_service.exchange_code(code)
        user_info = await google_oauth_service.get_user_info(token_data["access_token"])
    except HTTPException as exc:
        return RedirectResponse(
            url=f"{frontend_url}/login?error=google_auth_failed&detail={quote_plus(str(exc.detail))}",
            status_code=302,
        )
    except Exception as exc:
        return RedirectResponse(
            url=f"{frontend_url}/login?error=google_auth_failed",
            status_code=302,
        )

    auth_svc = AuthenticationService(db)
    try:
        session_token, principal, user, redirect_path = await auth_svc.handle_google_login(
            sub=user_info["sub"],
            email=user_info["email"],
            name=user_info["name"],
            email_verified=user_info["email_verified"],
        )
        if principal.citizen_id:
            audit = AuditService(AuditRepository(db))
            await audit.record(principal.citizen_id, "CITIZEN", "GOOGLE_LOGIN", "Google authentication", "SUCCESS")

        target_url = f"{frontend_url}{redirect_path}"
        response = RedirectResponse(url=target_url, status_code=302)
        set_auth_cookie(response, session_token, is_secure=_is_request_secure(request))
        return response

    except GoogleAccountCollisionException as collision:
        # Safe Account Linking: An account with this email exists.
        # Direct the user to verify ownership via password to complete linking.
        encoded_email = quote_plus(collision.email)
        encoded_sub = quote_plus(collision.pending_sub)
        return RedirectResponse(
            url=f"{frontend_url}/login?mode=link_google&error=account_linking_required&email={encoded_email}&pending_sub={encoded_sub}",
            status_code=302,
        )


@router.post("/link-google", response_model=AuthResponse)
async def link_google(
    req: LinkGoogleRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Safely link an existing password-authenticated account with a Google identity.
    Requires password verification to prevent unauthorized account takeover.
    """
    auth_rate_limiter.check(request, "link_google")
    auth_svc = AuthenticationService(db)

    token, principal, user = await auth_svc.link_google_account(
        email=req.email,
        password=req.password,
        pending_sub=req.pending_sub,
        provider_email=req.provider_email,
    )
    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None

    if principal.citizen_id:
        audit = AuditService(AuditRepository(db))
        await audit.record(principal.citizen_id, "CITIZEN", "ACCOUNT_LINKED", "Linked Google identity", "SUCCESS")

    set_auth_cookie(response, token, is_secure=_is_request_secure(request))

    return response_for(
        principal,
        citizen.name if citizen else None,
        user.email,
        phone=user.phone,
        mobile_number=user.mobile_number,
        email_verified=user.email_verified,
        mobile_verified=user.mobile_verified,
        google_linked=True,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=token,
    )


@router.get("/me", response_model=AuthResponse)
async def me(
    request: Request,
    principal: IdentityPrincipal = Depends(get_current_identity),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Hydrates current authenticated user context strictly from server-side session.
    Never trusts client-supplied user_id or citizen_id.
    """
    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None
    user = await db.get(User, principal.user_id) if principal.user_id else None

    if user and user.preferred_language:
        principal.preferred_language = user.preferred_language

    current_token = request.cookies.get(SESSION_COOKIE)
    if not current_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            current_token = auth_header[7:].strip()

    return response_for(
        principal,
        citizen.name if citizen else None,
        user.email if user else None,
        phone=user.phone if user else None,
        mobile_number=user.mobile_number if user else None,
        email_verified=user.email_verified if user else False,
        mobile_verified=user.mobile_verified if user else False,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=current_token,
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    """Logs out user, revokes server session, and clears session cookie."""
    principal = None
    try:
        principal = await AuthenticationService(db).current(request)
    except Exception:
        pass

    await AuthenticationService(db).logout(request)

    if principal and principal.citizen_id:
        await AuditService(AuditRepository(db)).record(
            principal.citizen_id, "SYSTEM", "LOGOUT", "Session logout", "SUCCESS"
        )
        await AuditService(AuditRepository(db)).record(
            principal.citizen_id, "SYSTEM", "SESSION_REVOKED", "Session logout", "SUCCESS"
        )

    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"authenticated": False}


@router.post("/demo-login", response_model=AuthResponse)
async def demo_login(
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Development fallback for automated test harness compatibility.
    Disabled in production (503 / 404 when DEV_DEMO_AUTH is false).
    """
    token, principal = await AuthenticationService(db).demo_login()
    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None
    user = await db.get(User, principal.user_id) if principal.user_id else None

    if principal.citizen_id:
        audit = AuditService(AuditRepository(db))
        await audit.record(principal.citizen_id, "SYSTEM", "LOGIN", "Demo authentication", "SUCCESS")
        await audit.record(principal.citizen_id, "SYSTEM", "SESSION_CREATED", "Demo authentication", "SUCCESS")

    set_auth_cookie(response, token, is_secure=False)
    return response_for(
        principal,
        citizen.name if citizen else None,
        user.email if user else None,
        phone=user.phone if user else None,
        mobile_number=user.mobile_number if user else None,
        email_verified=user.email_verified if user else False,
        mobile_verified=user.mobile_verified if user else False,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=token,
    )
