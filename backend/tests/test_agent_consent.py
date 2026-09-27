import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.models.audit import Consent, AuditEvent
from app.db.seed import RAMESH_UUID

@pytest.mark.asyncio
async def test_agent_consent_contract(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/agent/chat",
            json={"citizen_id": str(RAMESH_UUID), "message": "Mujhe education assistance ke liye apply karna hai."},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requires_consent"] is True
    assert payload["consent_id"]

    consent = await db_session.get(Consent, payload["consent_id"])
    assert consent is not None
    assert consent.is_granted is False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        grant = await client.post(
            f"/api/agent/consent/{payload['consent_id']}/grant",
            json={"action": "GRANT", "application_id": payload["consent_application_id"]},
        )
        repeat = await client.post(
            f"/api/agent/consent/{payload['consent_id']}/grant",
            json={"action": "GRANT"},
        )
        invalid = await client.post(
            "/api/agent/consent/00000000-0000-0000-0000-000000000000/grant",
            json={"action": "GRANT"},
        )

    assert grant.status_code == 200
    assert grant.json() == {"success": True, "granted": True}
    assert repeat.status_code == 200
    assert invalid.status_code == 404

    await db_session.refresh(consent)
    assert consent.is_granted is True

    audit = await db_session.scalar(
        select(AuditEvent).where(
            AuditEvent.consent_id == consent.id,
            AuditEvent.action == "CONSENT_GRANTED",
        )
    )
    assert audit is not None
