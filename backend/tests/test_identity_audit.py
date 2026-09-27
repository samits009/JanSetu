import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from app.main import app
from app.models.audit import AuditEvent
from app.db.seed import RAMESH_UUID


@pytest.mark.asyncio
async def test_identity_events_are_audited(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/auth/demo-login")
        await client.post("/api/auth/logout")
    actions = (await db_session.execute(
        select(AuditEvent.action).where(AuditEvent.citizen_id == RAMESH_UUID)
    )).scalars().all()
    assert "LOGIN" in actions
    assert "SESSION_CREATED" in actions
    assert "LOGOUT" in actions
    assert "SESSION_REVOKED" in actions
