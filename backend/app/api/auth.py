from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.models.citizen import Citizen
from app.models.identity import User
from app.schemas.auth import AuthResponse, RegisterRequest, LoginRequest
from app.services.authentication import AuthenticationService, SESSION_COOKIE, SESSION_TTL
from app.services.authorization import get_current_identity
from app.services.identity import IdentityPrincipal
from app.repositories.application import AuditRepository
from app.services.audit import AuditService

router = APIRouter()


def response_for(
    principal: IdentityPrincipal,
    name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    onboarding_completed: bool = False,
    onboarding_step: int = 1,
    token: str | None = None,
) -> AuthResponse:
    return AuthResponse(
        authenticated=True,
        user_id=principal.user_id,
        identity_id=principal.identity_id,
        role=principal.role,
        citizen_id=principal.citizen_id,
        verification_state=principal.verification_state,
        citizen_name=name,
        email=email,
        phone=phone,
        preferred_language=principal.preferred_language or "hi",
        onboarding_completed=onboarding_completed,
        onboarding_step=onboarding_step,
        session_token=token,
        token=token,
    )


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, response: Response, db: AsyncSession = Depends(get_async_db)):
    auth_svc = AuthenticationService(db)
    token, principal, user = await auth_svc.register(
        name=req.name,
        password=req.password,
        email=req.email,
        phone=req.phone,
        preferred_language=req.preferred_language,
    )
    if principal.citizen_id:
        audit = AuditService(AuditRepository(db))
        await audit.record(principal.citizen_id, "CITIZEN", "REGISTER", "Citizen registration", "SUCCESS")
        await audit.record(principal.citizen_id, "SYSTEM", "SESSION_CREATED", "Registration session", "SUCCESS")

    response.set_cookie(
        SESSION_COOKIE, 
        token, 
        httponly=True, 
        samesite="lax", 
        secure=False, 
        max_age=int(SESSION_TTL.total_seconds())
    )
    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None
    return response_for(
        principal,
        req.name,
        user.email,
        user.phone,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_async_db)):
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

    response.set_cookie(
        SESSION_COOKIE, 
        token, 
        httponly=True, 
        samesite="lax", 
        secure=False, 
        max_age=int(SESSION_TTL.total_seconds())
    )
    return response_for(
        principal,
        citizen.name if citizen else None,
        user.email,
        user.phone,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=token,
    )


@router.post("/demo-login", response_model=AuthResponse)
async def demo_login(response: Response, db: AsyncSession = Depends(get_async_db)):
    token, principal = await AuthenticationService(db).demo_login()
    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None
    user = await db.get(User, principal.user_id) if principal.user_id else None
    if principal.citizen_id:
        audit = AuditService(AuditRepository(db))
        await audit.record(principal.citizen_id, "SYSTEM", "LOGIN", "Demo authentication", "SUCCESS")
        await audit.record(principal.citizen_id, "SYSTEM", "SESSION_CREATED", "Demo authentication", "SUCCESS")
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=False, max_age=int(SESSION_TTL.total_seconds()))
    return response_for(
        principal,
        citizen.name if citizen else None,
        user.email if user else None,
        user.phone if user else None,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=token,
    )


@router.get("/me", response_model=AuthResponse)
async def me(request: Request, principal: IdentityPrincipal = Depends(get_current_identity), db: AsyncSession = Depends(get_async_db)):
    citizen = await db.get(Citizen, principal.citizen_id) if principal.citizen_id else None
    user = await db.get(User, principal.user_id) if principal.user_id else None
    # Always reflect the live preferred_language from PostgreSQL — not the session snapshot.
    # This ensures a language change via PUT /me/preferences is immediately visible.
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
        user.phone if user else None,
        onboarding_completed=citizen.onboarding_completed if citizen else False,
        onboarding_step=citizen.onboarding_step if citizen else 1,
        token=current_token,
    )


@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_async_db)):
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
    response.delete_cookie(SESSION_COOKIE)
    return {"authenticated": False}

