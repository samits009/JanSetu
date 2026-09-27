import pytest
from app.services.scheme_registry import SchemeRegistryService
from app.repositories.scheme import SchemeRepository
from app.models.scheme import Scheme

@pytest.mark.asyncio
async def test_scheme_registry(db_session):
    repo = SchemeRepository(db_session)
    service = SchemeRegistryService(repo)
    
    scheme = await repo.create(official_name="Test Scheme", category="HEALTH")
    fetched = await service.get_scheme(scheme.id)
    assert fetched.official_name == "Test Scheme"
