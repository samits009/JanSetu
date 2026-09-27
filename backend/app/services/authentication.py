import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, Request, Response, status
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import AuthIdentity, AuthSession, Identity, User
from app.models.citizen import Citizen
from app.services.identity import IdentityPrincipal, IdentityProvider
from app.services.password import hash_password, verify_password
from app.services.validators import (
    is_email,
    normalize_and_validate_email,
    normalize_and_validate_mobile,
)

SESSION_COOKIE = "jansetu_session"
SESSION_TTL = timedelta(hours=24)


def set_auth_cookie(response: Response, token: str, is_secure: bool = False) -> None:
    """Sets the secure, HTTP-only authentication session cookie."""
    samesite_val = "none" if is_secure else "lax"
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite=samesite_val,
        secure=is_secure,
        max_age=int(SESSION_TTL.total_seconds()),
        path="/",
    )


class GoogleAccountCollisionException(Exception):
    """Raised when a Google sign-in attempts to use an email already associated with a password account."""
    def __init__(self, email: str, pending_sub: str):
        self.email = email
        self.pending_sub = pending_sub
        super().__init__(f"Account collision for email {email}")


class DatabaseIdentityProvider(IdentityProvider):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def authenticate(self, token: str) -> IdentityPrincipal:
        return await self.get_identity(token)

    async def get_identity(self, token: str) -> IdentityPrincipal:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        result = await self.session.execute(
            select(AuthSession)
            .options(selectinload(AuthSession.identity), selectinload(AuthSession.user))
            .where(
                AuthSession.token_hash == token_hash,
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > datetime.now(timezone.utc),
            )
        )
        session = result.scalars().first()
        if not session or not session.identity or not session.identity.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
            )
        identity = session.identity
        user_lang = session.user.preferred_language if session.user else "hi"
        user_id = session.user_id
        return IdentityPrincipal(
            identity_id=identity.id,
            role=identity.role,
            citizen_id=identity.citizen_id,
            verification_state=identity.verification_state,
            user_id=user_id,
            preferred_language=user_lang,
        )

    async def logout(self, token: str) -> None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        result = await self.session.execute(
            select(AuthSession).where(AuthSession.token_hash == token_hash)
        )
        session = result.scalars().first()
        if session:
            session.revoked_at = datetime.now(timezone.utc)
            await self.session.flush()


class AuthenticationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.provider = DatabaseIdentityProvider(session)

    async def register(
        self,
        name: str,
        password: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        preferred_language: str = "hi",
    ) -> Tuple[str, IdentityPrincipal, User]:
        """
        Register a new citizen user with credentials, identity, auth identity, and session.
        Fully transactional with database-enforced uniqueness and Argon2 hashing.
        """
        if not name or len(name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Full name is required (minimum 2 characters)")

        if not password or len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        if not email and not phone:
            raise HTTPException(status_code=400, detail="Email address and mobile number are required")

        normalized_email: Optional[str] = None
        canonical_mobile: Optional[str] = None

        if email:
            normalized_email = normalize_and_validate_email(email)
        if phone:
            canonical_mobile = normalize_and_validate_mobile(phone)

        # Pre-check duplicates with clear messages
        if normalized_email:
            existing_email = (
                await self.session.execute(
                    select(User).where(User.email == normalized_email)
                )
            ).scalars().first()
            if existing_email:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this email address already exists.",
                )

        if canonical_mobile:
            existing_mobile = (
                await self.session.execute(
                    select(User).where(
                        or_(
                            User.mobile_number == canonical_mobile,
                            User.phone == canonical_mobile,
                        )
                    )
                )
            ).scalars().first()
            if existing_mobile:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this mobile number already exists.",
                )

        try:
            # 1. Create Citizen record
            citizen = Citizen(
                name=name.strip(),
                phone=canonical_mobile,
                onboarding_completed=False,
                onboarding_step=1,
            )
            self.session.add(citizen)
            await self.session.flush()

            # 2. Create Identity record
            identity = Identity(
                citizen_id=citizen.id,
                role="CITIZEN",
                verification_state="IDENTITY_CLAIMED",
                active=True,
            )
            self.session.add(identity)
            await self.session.flush()

            # 3. Create User record with Argon2 password hash
            pwd_hash = hash_password(password)
            user = User(
                email=normalized_email,
                phone=canonical_mobile,
                mobile_number=canonical_mobile,
                password_hash=pwd_hash,
                citizen_id=citizen.id,
                identity_id=identity.id,
                preferred_language=preferred_language or "hi",
                is_active=True,
                email_verified=False,
                mobile_verified=False,
                account_status="ACTIVE",
            )
            self.session.add(user)
            await self.session.flush()

            # 4. Create AuthIdentity record for local password provider
            if normalized_email:
                auth_identity = AuthIdentity(
                    user_id=user.id,
                    provider="password",
                    provider_subject=normalized_email,
                    provider_email=normalized_email,
                )
                self.session.add(auth_identity)
                await self.session.flush()

            # 5. Create Session
            token = secrets.token_urlsafe(32)
            auth_session = AuthSession(
                identity_id=identity.id,
                user_id=user.id,
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                expires_at=datetime.now(timezone.utc) + SESSION_TTL,
            )
            self.session.add(auth_session)
            await self.session.flush()

        except IntegrityError as exc:
            await self.session.rollback()
            err_str = str(exc).lower()
            if "users_email" in err_str or "email" in err_str:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this email address already exists.",
                )
            if "mobile" in err_str or "phone" in err_str:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this mobile number already exists.",
                )
            raise HTTPException(
                status_code=400,
                detail="Account creation failed due to duplicate credentials.",
            )

        principal = IdentityPrincipal(
            identity_id=identity.id,
            role=identity.role,
            citizen_id=citizen.id,
            verification_state=identity.verification_state,
            user_id=user.id,
            preferred_language=user.preferred_language,
        )
        return token, principal, user

    async def login(self, username: str, password: str) -> Tuple[str, IdentityPrincipal, User]:
        """
        Authenticate user by email OR mobile number and password, creating a new session.
        Determines identifier type and queries authoritative PostgreSQL database.
        """
        identifier = username.strip()
        if not identifier or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or mobile number and password are required.",
            )

        user: Optional[User] = None

        if is_email(identifier):
            normalized_email = normalize_and_validate_email(identifier)
            result = await self.session.execute(
                select(User)
                .options(selectinload(User.identity), selectinload(User.citizen))
                .where(User.email == normalized_email)
            )
            user = result.scalars().first()
        else:
            # Assume mobile number: normalize and search canonical + raw
            try:
                canonical_mobile = normalize_and_validate_mobile(identifier)
                result = await self.session.execute(
                    select(User)
                    .options(selectinload(User.identity), selectinload(User.citizen))
                    .where(
                        or_(
                            User.mobile_number == canonical_mobile,
                            User.phone == canonical_mobile,
                            User.phone == identifier,
                        )
                    )
                )
                user = result.scalars().first()
            except HTTPException:
                # If identifier is neither valid email nor valid mobile, attempt literal match as fallback
                result = await self.session.execute(
                    select(User)
                    .options(selectinload(User.identity), selectinload(User.citizen))
                    .where(or_(User.email == identifier.lower(), User.phone == identifier))
                )
                user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account was created with Google sign-in. Please use Continue with Google to log in.",
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        identity = user.identity
        if not identity:
            identity = Identity(
                citizen_id=user.citizen_id,
                role="CITIZEN",
                verification_state="IDENTITY_CLAIMED",
                active=True,
            )
            self.session.add(identity)
            await self.session.flush()
            user.identity_id = identity.id

        token = secrets.token_urlsafe(32)
        auth_session = AuthSession(
            identity_id=identity.id,
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        )
        self.session.add(auth_session)
        user.last_login = datetime.now(timezone.utc)
        await self.session.flush()

        principal = IdentityPrincipal(
            identity_id=identity.id,
            role=identity.role,
            citizen_id=user.citizen_id,
            verification_state=identity.verification_state,
            user_id=user.id,
            preferred_language=user.preferred_language,
        )
        return token, principal, user

    async def handle_google_login(
        self,
        sub: str,
        email: str,
        name: str,
        email_verified: bool = True,
    ) -> Tuple[str, IdentityPrincipal, User, str]:
        """
        Handles real Google sign-in / sign-up callback.
        1. Checks if Google identity already exists in auth_identities (Direct Sign-In).
        2. If not, checks if a local account with the same email exists (Collision -> Linking Required).
        3. If no existing account, creates new JanSetu account and routes to Onboarding (First-time Signup).
        Returns: (session_token, principal, user, redirect_path)
        """
        normalized_email = normalize_and_validate_email(email)

        # 1. Check existing Google AuthIdentity by (provider="google", provider_subject=sub)
        result = await self.session.execute(
            select(AuthIdentity)
            .options(
                selectinload(AuthIdentity.user).selectinload(User.identity),
                selectinload(AuthIdentity.user).selectinload(User.citizen),
            )
            .where(
                AuthIdentity.provider == "google",
                AuthIdentity.provider_subject == sub,
            )
        )
        existing_identity = result.scalars().first()

        if existing_identity:
            user = existing_identity.user
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated",
                )

            identity = user.identity
            token = secrets.token_urlsafe(32)
            auth_session = AuthSession(
                identity_id=identity.id,
                user_id=user.id,
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                expires_at=datetime.now(timezone.utc) + SESSION_TTL,
            )
            self.session.add(auth_session)
            user.last_login = datetime.now(timezone.utc)
            await self.session.flush()

            principal = IdentityPrincipal(
                identity_id=identity.id,
                role=identity.role,
                citizen_id=user.citizen_id,
                verification_state=identity.verification_state,
                user_id=user.id,
                preferred_language=user.preferred_language,
            )
            # Route to onboarding if mobile is missing or onboarding incomplete
            redirect_path = (
                "/onboarding"
                if (not user.mobile_number or not user.citizen or not user.citizen.onboarding_completed)
                else "/"
            )
            return token, principal, user, redirect_path

        # 2. Check if a local account exists with this email
        existing_local_user = (
            await self.session.execute(
                select(User).where(User.email == normalized_email)
            )
        ).scalars().first()

        if existing_local_user:
            # Account collision! Prevent automatic merge; require password verification for explicit linking.
            raise GoogleAccountCollisionException(email=normalized_email, pending_sub=sub)

        # 3. First-time Google Signup: Create Citizen, Identity, User, AuthIdentity, AuthSession
        citizen = Citizen(
            name=name.strip() if name else normalized_email.split("@")[0],
            phone=None,
            onboarding_completed=False,
            onboarding_step=1,
        )
        self.session.add(citizen)
        await self.session.flush()

        identity = Identity(
            citizen_id=citizen.id,
            role="CITIZEN",
            verification_state="IDENTITY_CLAIMED",
            active=True,
        )
        self.session.add(identity)
        await self.session.flush()

        user = User(
            email=normalized_email,
            mobile_number=None,
            phone=None,
            password_hash=None,  # Google-only user
            citizen_id=citizen.id,
            identity_id=identity.id,
            preferred_language="hi",
            is_active=True,
            email_verified=email_verified,
            mobile_verified=False,
            account_status="ACTIVE",
        )
        self.session.add(user)
        await self.session.flush()

        auth_identity = AuthIdentity(
            user_id=user.id,
            provider="google",
            provider_subject=sub,
            provider_email=normalized_email,
        )
        self.session.add(auth_identity)
        await self.session.flush()

        token = secrets.token_urlsafe(32)
        auth_session = AuthSession(
            identity_id=identity.id,
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        )
        self.session.add(auth_session)
        user.last_login = datetime.now(timezone.utc)
        await self.session.flush()

        principal = IdentityPrincipal(
            identity_id=identity.id,
            role=identity.role,
            citizen_id=citizen.id,
            verification_state=identity.verification_state,
            user_id=user.id,
            preferred_language=user.preferred_language,
        )
        # Google user must go to onboarding to provide required mobile number
        return token, principal, user, "/onboarding"

    async def link_google_account(
        self,
        email: str,
        password: str,
        pending_sub: str,
        provider_email: Optional[str] = None,
    ) -> Tuple[str, IdentityPrincipal, User]:
        """
        Safely links a Google identity to an existing password-authenticated JanSetu user account.
        Requires verifying the account's existing password.
        """
        normalized_email = normalize_and_validate_email(email)

        result = await self.session.execute(
            select(User)
            .options(selectinload(User.identity), selectinload(User.citizen))
            .where(User.email == normalized_email)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="JanSetu account not found for this email address.",
            )

        if not user.password_hash or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password for the existing JanSetu account.",
            )

        # Check if this Google sub is already linked to another account
        existing_sub = (
            await self.session.execute(
                select(AuthIdentity).where(
                    AuthIdentity.provider == "google",
                    AuthIdentity.provider_subject == pending_sub,
                )
            )
        ).scalars().first()
        if existing_sub and existing_sub.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Google identity is already linked to a different JanSetu account.",
            )

        if not existing_sub:
            auth_id = AuthIdentity(
                user_id=user.id,
                provider="google",
                provider_subject=pending_sub,
                provider_email=provider_email or normalized_email,
            )
            self.session.add(auth_id)
            user.email_verified = True
            await self.session.flush()

        identity = user.identity
        token = secrets.token_urlsafe(32)
        auth_session = AuthSession(
            identity_id=identity.id,
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        )
        self.session.add(auth_session)
        user.last_login = datetime.now(timezone.utc)
        await self.session.flush()

        principal = IdentityPrincipal(
            identity_id=identity.id,
            role=identity.role,
            citizen_id=user.citizen_id,
            verification_state=identity.verification_state,
            user_id=user.id,
            preferred_language=user.preferred_language,
        )
        return token, principal, user

    async def demo_login(self) -> Tuple[str, IdentityPrincipal]:
        """Development fallback for test harness / seeded demo."""
        if os.environ.get("DEV_DEMO_AUTH", "false").lower() != "true":
            raise HTTPException(status_code=404, detail="Demo authentication is disabled")
        citizen_id = UUID(os.environ.get("VITE_DEMO_CITIZEN_ID", "a1b2c3d4-e5f6-7890-abcd-ef1234567890"))
        citizen = await self.session.get(Citizen, citizen_id)
        if not citizen:
            raise HTTPException(status_code=404, detail="Demo citizen not found")
        result = await self.session.execute(select(Identity).where(Identity.citizen_id == citizen_id))
        identity = result.scalars().first()
        if not identity:
            identity = Identity(citizen_id=citizen_id, role="CITIZEN", verification_state="IDENTITY_CLAIMED")
            self.session.add(identity)
            await self.session.flush()

        # Check or create demo user
        result_user = await self.session.execute(select(User).where(User.citizen_id == citizen_id))
        user = result_user.scalars().first()
        if not user:
            user = User(
                email="ramesh@jansetu.in",
                phone="9876543210",
                password_hash=hash_password("DemoPassword123!"),
                citizen_id=citizen.id,
                identity_id=identity.id,
                preferred_language="hi",
            )
            self.session.add(user)
            await self.session.flush()

        token = secrets.token_urlsafe(32)
        auth_session = AuthSession(
            identity_id=identity.id,
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        )
        self.session.add(auth_session)
        await self.session.flush()
        return token, IdentityPrincipal(
            identity.id, identity.role, identity.citizen_id, identity.verification_state, user_id=user.id, preferred_language=user.preferred_language
        )

    async def current(self, request: Request) -> IdentityPrincipal:
        token = request.cookies.get(SESSION_COOKIE)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()
        if not token:
            raise HTTPException(status_code=401, detail="Authentication required")
        return await self.provider.get_identity(token)

    async def logout(self, request: Request) -> None:
        token = request.cookies.get(SESSION_COOKIE)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()
        if token:
            await self.provider.logout(token)
