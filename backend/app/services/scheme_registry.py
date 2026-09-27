from typing import List, Optional, Any
from app.repositories.scheme import SchemeRepository
from app.models.scheme import Scheme

class SchemeRegistryService:
    def __init__(self, scheme_repo: SchemeRepository):
        self.scheme_repo = scheme_repo

    async def get_scheme(self, scheme_id: Any) -> Scheme:
        return await self.scheme_repo.get_with_rules(scheme_id)

    async def list_schemes(self) -> List[Scheme]:
        return await self.scheme_repo.list()

    async def list_schemes_for_location(self, state: str) -> List[Scheme]:
        return await self.scheme_repo.list_for_location(state)

    async def list_verified_schemes(self) -> List[Scheme]:
        return await self.scheme_repo.list_verified()
