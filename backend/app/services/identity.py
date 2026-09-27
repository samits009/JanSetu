from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class IdentityPrincipal:
    identity_id: UUID
    role: str
    citizen_id: Optional[UUID]
    verification_state: str
    user_id: Optional[UUID] = None
    preferred_language: str = "hi"


class IdentityProvider(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> IdentityPrincipal: ...

    @abstractmethod
    async def get_identity(self, token: str) -> IdentityPrincipal: ...

    @abstractmethod
    async def logout(self, token: str) -> None: ...

    async def verify_identity(self, principal: IdentityPrincipal) -> bool:
        return principal.verification_state in {"IDENTITY_CLAIMED", "IDENTITY_VERIFIED"}


class RealIdentityProvider(IdentityProvider):
    async def authenticate(self, token: str) -> IdentityPrincipal:
        raise NotImplementedError("Real identity provider is not configured")

    async def get_identity(self, token: str) -> IdentityPrincipal:
        raise NotImplementedError("Real identity provider is not configured")

    async def logout(self, token: str) -> None:
        raise NotImplementedError("Real identity provider is not configured")
