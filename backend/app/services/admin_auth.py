"""
Admin Authorization Boundary
=============================
This module defines the administrative authorization interface for mutating
scheme intelligence operations (refresh, approve, reject, publish).

IMPORTANT DEVELOPMENT SAFETY RULES:
- Mock admin identity is ONLY allowed when DEV_MOCK_ADMIN_AUTH=true
- In production (DEV_MOCK_ADMIN_AUTH=false), the mock MUST be rejected (fail closed)
- This interface must be replaced by a real identity provider before production deployment

Environment Variables:
    DEV_MOCK_ADMIN_AUTH: Set to 'true' to allow mock admin identity (local dev only)
    ADMIN_TOKEN_HEADER: Optional custom header name (default: X-Admin-Token)
"""
import os
from abc import ABC, abstractmethod
from typing import Optional
from fastapi import HTTPException, Header, Request, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.services.authentication import AuthenticationService, SESSION_COOKIE


MOCK_ADMIN_TOKEN = "mock-admin-token"
DEV_MOCK_ADMIN_AUTH = os.environ.get("DEV_MOCK_ADMIN_AUTH", "false").lower() == "true"


class AdminIdentity(ABC):
    """Interface for admin identity providers. Replace this implementation for production."""
    @abstractmethod
    def authenticate(self, token: Optional[str]) -> str:
        """Returns admin actor string or raises HTTPException."""
        ...


class MockDevAdminIdentity(AdminIdentity):
    """Development-only mock admin. MUST NOT be used in production."""
    def authenticate(self, token: Optional[str]) -> str:
        if not DEV_MOCK_ADMIN_AUTH:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Admin authentication is not configured. "
                    "DEV_MOCK_ADMIN_AUTH is false and no real admin identity provider is available. "
                    "Failing closed to protect production data."
                )
            )
        if token != MOCK_ADMIN_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token"
            )
        return "mock-admin"


# Active identity provider (swap this for production)
_admin_identity_provider: AdminIdentity = MockDevAdminIdentity()


async def get_current_admin(
    request: Request,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    db: AsyncSession = Depends(get_async_db),
) -> str:
    """
    FastAPI dependency: resolves the admin actor string.
    
    Development mode (DEV_MOCK_ADMIN_AUTH=true):
        Accepts the mock-admin-token header.
    
    Production mode (DEV_MOCK_ADMIN_AUTH=false):
        FAILS CLOSED — returns 503 if no real identity provider is configured.
    """
    if request.cookies.get(SESSION_COOKIE):
        try:
            principal = await AuthenticationService(db).current(request)
            if principal.role != "ADMIN":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_403_FORBIDDEN:
                raise
    return _admin_identity_provider.authenticate(x_admin_token)
