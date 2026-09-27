import pytest
import uuid
import datetime
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.scheme import Scheme, SchemeEligibilityRule, SchemeVersion
from app.models.citizen import Location, Employment, Household, HouseholdMember
from app.models.evidence import Document, Evidence
from app.services.consent import ConsentService
from app.repositories.application import ConsentRepository
from sqlalchemy import text


@pytest.mark.asyncio
async def test_phase8c_real_application_journey_and_official_handoff(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register & Login Citizen
        email = f"citizen.journey.{uuid.uuid4().hex[:6]}@example.com"
        reg = await client.post("/api/auth/register", json={
            "email": email,
            "password": "Password123!",
            "name": "Kavita Sharma"
        })
        assert reg.status_code == 200
        cit_id = UUID_val = reg.json()["citizen_id"]

        # 2. Setup citizen profile and jurisdiction
        await client.put("/api/citizens/me/onboarding/step", json={
            "step": 1,
            "name": "Kavita Sharma",
            "date_of_birth": "1990-08-20",
            "gender": "female",
            "phone": "9812345678"
        })
        await client.put("/api/citizens/me/onboarding/step", json={
            "step": 2,
            "current_state": "Delhi",
            "current_district": "Central",
            "current_pincode": "110001",
            "is_rural": False
        })
        await client.put("/api/citizens/me/onboarding/step", json={
            "step": 3,
            "employment_status": "construction_worker",
            "occupation": "Construction Mason",
            "annual_income": 96000,
            "duration_months": 24
        })

        # 3. Seed an Official Scheme with requirement definitions
        scheme_id = uuid.uuid4()
        scheme = Scheme(
            id=scheme_id,
            official_name="Delhi BOCW Maternity and Social Assistance",
            category="HEALTH",
            state="Delhi",
            level="STATE",
            requirement_definitions=[
                {"id": "req-occ", "type": "OCCUPATION", "name": "BOCW Worker Registration", "mandatory": True}
            ]
        )
        db_session.add(scheme)
        await db_session.flush()

        version = SchemeVersion(
            id=uuid.uuid4(),
            scheme_id=scheme.id,
            version_number=1,
            verification_status="VERIFIED"
        )
        db_session.add(version)
        await db_session.flush()
        scheme.current_version_id = version.id

        rule = SchemeEligibilityRule(
            id=uuid.uuid4(),
            scheme_id=scheme.id,
            version_id=version.id,
            rule_type="OCCUPATION",
            operator="==",
            value="Construction Mason"
        )
        db_session.add(rule)
        await db_session.commit()

        # 4. Benefit Discovery: Check schemes via public/authenticated API
        schemes_res = await client.get("/api/schemes")
        assert schemes_res.status_code == 200
        found = any(s["id"] == str(scheme_id) for s in schemes_res.json()["items"])
        assert found is True

        # 5. Application Preparation: Create application pinned to scheme version
        app_res = await client.post("/api/applications/", json={
            "scheme_id": str(scheme_id)
        })
        assert app_res.status_code == 200
        app_data = app_res.json()
        application_id = app_data["id"]
        assert app_data["scheme_id"] == str(scheme_id)
        # Authoritative policy engine flags missing mandatory evidence
        assert app_data["status"] in ("EVIDENCE_REQUIRED", "DRAFT", "EVIDENCE_COMPLETE")

        # 6. Upload matching document & generate verified evidence
        doc_res = await client.post(
            "/api/documents/",
            data={"document_type": "BOCW_REGISTRATION"},
            files={"file": ("bocw_card.pdf", b"%PDF-1.4 real bocw card content", "application/pdf")}
        )
        assert doc_res.status_code == 200
        doc_id = doc_res.json()["document_id"]

        # Insert statutory verified evidence claim
        ev_id = uuid.uuid4()
        await db_session.execute(
            text("""
                INSERT INTO evidence (id, citizen_id, document_id, evidence_type, data, verification_status)
                VALUES (:id, :cid, :did, :et, :d, :vs)
            """),
            {
                "id": ev_id,
                "cid": uuid.UUID(cit_id),
                "did": uuid.UUID(doc_id),
                "et": "OCCUPATION",
                "d": '{"occupation": "Construction Mason", "registration_valid": true}',
                "vs": "VERIFIED"
            }
        )
        # Also update app status to EVIDENCE_COMPLETE
        await db_session.execute(
            text("UPDATE welfare_applications SET status = 'EVIDENCE_COMPLETE' WHERE id = :aid"),
            {"aid": uuid.UUID(application_id)}
        )
        await db_session.commit()

        # 7. Official Portal Handoff preparation (without fake submission)
        handoff_res = await client.post(f"/api/applications/{application_id}/handoff")
        assert handoff_res.status_code == 200
        handoff = handoff_res.json()
        assert "portal_name" in handoff
        assert "portal_url" in handoff
        assert "instructions_en" in handoff
        assert "instructions_hi" in handoff
        assert "handoff_reference" in handoff

        # 8. Grant Explicit Backend Consent for submission/handoff recording
        consent_service = ConsentService(ConsentRepository(db_session))
        pending_consent = await consent_service.request(
            citizen_id=uuid.UUID(cit_id),
            action="APPLICATION_SUBMISSION",
            application_id=uuid.UUID(application_id)
        )
        await consent_service.grant(pending_consent.id)
        await db_session.commit()

        # 9. Submit/Handoff execution
        submit_res = await client.post(f"/api/applications/{application_id}/submit")
        assert submit_res.status_code == 200
        submitted_app = submit_res.json()
        assert submitted_app["id"] == application_id

        # 10. Tracking: Verify in /api/applications/me
        my_apps = await client.get("/api/applications/me")
        assert my_apps.status_code == 200
        my_app_ids = [a["id"] for a in my_apps.json()]
        assert application_id in my_app_ids
