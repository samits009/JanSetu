import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, Request, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import AuthSession, Identity, User
from app.models.citizen import Citizen
from app.services.identity import IdentityPrincipal, IdentityProvider
from app.services.password import hash_password, verify_password

SESSION_COOKIE = "jansetu_session"
SESSION_TTL = timedelta(hours=24)


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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
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
        result = await self.session.execute(select(AuthSession).where(AuthSession.token_hash == token_hash))
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
        preferred_language: str = "hi"
    ) -> Tuple[str, IdentityPrincipal, User]:
        """Register a new citizen user with credentials, identity, and session."""
        if not email and not phone:
            raise HTTPException(status_code=400, detail="Either email or phone number is required")

        # Check existing user
        conditions = []
        if email:
            conditions.append(User.email == email.strip().lower())
        if phone:
            conditions.append(User.phone == phone.strip())

        existing_user = (await self.session.execute(
            select(User).where(or_(*conditions))
        )).scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="A user with this email or phone already exists")

        # 1. Create Citizen
        citizen = Citizen(
            name=name.strip(),
            phone=phone.strip() if phone else None,
        )
        self.session.add(citizen)
        await self.session.flush()

        # 2. Create Identity
        identity = Identity(
            citizen_id=citizen.id,
            role="CITIZEN",
            verification_state="IDENTITY_CLAIMED",
            active=True
        )
        self.session.add(identity)
        await self.session.flush()

        # 3. Create User with hashed password
        pwd_hash = hash_password(password)
        user = User(
            email=email.strip().lower() if email else None,
            phone=phone.strip() if phone else None,
            password_hash=pwd_hash,
            citizen_id=citizen.id,
            identity_id=identity.id,
            preferred_language=preferred_language or "hi",
            is_active=True
        )
        self.session.add(user)
        await self.session.flush()

        # 4. Create Session
        token = secrets.token_urlsafe(32)
        auth_session = AuthSession(
            identity_id=identity.id,
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        )
        self.session.add(auth_session)
        await self.session.flush()

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
        """Authenticate user by email or phone and password, creating a new session."""
        identifier = username.strip().lower()
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.identity), selectinload(User.citizen))
            .where(or_(User.email == identifier, User.phone == username.strip()))
        )
        user = result.scalars().first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")

        identity = user.identity
        if not identity:
            identity = Identity(
                citizen_id=user.citizen_id,
                role="CITIZEN",
                verification_state="IDENTITY_CLAIMED",
                active=True
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
        # Record last login timestamp
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

