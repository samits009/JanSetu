import pytest
from app.repositories.citizen import CitizenRepository
from app.models.citizen import Citizen

@pytest.mark.asyncio
async def test_citizen_repository_create_and_get(db_session):
    repo = CitizenRepository(db_session)
    citizen = await repo.create(name="Test Citizen", phone="1234567890")
    assert citizen.id is not None

    fetched = await repo.get_by_id(citizen.id)
    assert fetched is not None
    assert fetched.name == "Test Citizen"
