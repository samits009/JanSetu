import os
from typing import Any, Dict, Optional
import uuid
from app.domain.enums import ApplicationStatus
from app.repositories.application import ApplicationRepository
from app.services.application_state_machine import ApplicationStateMachine

OFFICIAL_GOVERNMENT_PORTALS: Dict[str, Dict[str, str]] = {
    "Delhi BOCW": {
        "authority": "Delhi Building and Other Construction Workers Welfare Board",
        "portal_name": "e-District Delhi",
        "portal_url": "https://edistrict.delhigovt.nic.in",
        "instructions_hi": "जनसेतु द्वारा आपका आवेदन और सत्यापित प्रमाण तैयार कर दिया गया है। ई-डिस्ट्रिक्ट दिल्ली पोर्टल पर लॉगिन करके अपना संदर्भ दर्ज करें।",
        "instructions_en": "Your application packet and verified evidence have been prepared by JanSetu. Complete final submission on the e-District Delhi portal.",
    },
    "One Nation One Ration Card": {
        "authority": "Department of Food and Public Distribution",
        "portal_name": "National Food Security Portal (Annavitran)",
        "portal_url": "https://nfsa.gov.in",
        "instructions_hi": "आपका राशन कार्ड पोर्टेबिलिटी विवरण सत्यापित है। नजदीकी उचित मूल्य दुकान (FPS) पर ई-पॉस (ePoS) मशीन द्वारा बायोमेट्रिक प्रमाणीकरण करें।",
        "instructions_en": "Your ration card portability is verified. Authenticate via biometric ePoS machine at any nearby Fair Price Shop.",
    },
    "UP BOCW": {
        "authority": "Uttar Pradesh Building & Other Construction Workers Board",
        "portal_name": "UP BOCW Portal",
        "portal_url": "https://upbocw.in",
        "instructions_hi": "आपका आवेदन पत्र तैयार है। यूपी बीओसीडब्ल्यू पोर्टल पर जाकर पंजीयन प्रमाण पत्र डाउनलोड या नवीनीकरण पूर्ण करें।",
        "instructions_en": "Your application packet is ready. Access the UP BOCW portal to complete registration or download certificates.",
    },
}

class GovernmentApplicationProvider:
    async def prepare_handoff(self, application_id: Any) -> Dict[str, Any]:
        raise NotImplementedError

    async def submit_application(self, application_id: Any) -> str:
        raise NotImplementedError

    async def get_application_status(self, application_id: Any) -> str:
        raise NotImplementedError


class OfficialPortalHandoffProvider(GovernmentApplicationProvider):
    """
    Production-facing government integration provider.
    Where no direct machine-to-machine API exists, JanSetu prepares the complete
    verified packet, generates sovereign provenance hashes, and directs the citizen
    to the official government portal with step-by-step guidance.
    """
    def __init__(self, app_repo: ApplicationRepository, state_machine: ApplicationStateMachine):
        self.app_repo = app_repo
        self.state_machine = state_machine

    async def prepare_handoff(self, application_id: Any) -> Dict[str, Any]:
        app = await self.app_repo.get_by_id(application_id)
        if not app:
            raise ValueError("Application not found")

        from sqlalchemy import select
        from app.models.scheme import Scheme

        scheme_name = "Welfare Scheme"
        authority = "Competent Welfare Authority"
        if app.scheme_id:
            scheme_res = await self.app_repo.session.execute(
                select(Scheme).where(Scheme.id == app.scheme_id)
            )
            scheme = scheme_res.scalars().first()
            if scheme:
                scheme_name = scheme.official_name
                authority = scheme.authority or authority

        portal_info = OFFICIAL_GOVERNMENT_PORTALS.get(scheme_name, {
            "authority": authority,
            "portal_name": "State Welfare Portal",
            "portal_url": "https://services.india.gov.in",
            "instructions_hi": "सत्यापित आवेदन पत्र तैयार है। आधिकारिक सरकारी पोर्टल पर जाकर प्रक्रिया पूर्ण करें।",
            "instructions_en": "Verified application packet ready. Complete final step on the official government portal.",
        })

        handoff_ref = f"JS-HANDOFF-{uuid.uuid4().hex[:8].upper()}"
        
        # Persist handoff reference in database
        await self.app_repo.record_provider_response(
            app.id,
            handoff_ref,
            rejection_reason=None
        )

        return {
            "handoff_reference": handoff_ref,
            "scheme_name": scheme_name,
            "authority": portal_info["authority"],
            "portal_name": portal_info["portal_name"],
            "portal_url": portal_info["portal_url"],
            "instructions_hi": portal_info["instructions_hi"],
            "instructions_en": portal_info["instructions_en"],
            "status": "HANDOFF_PREPARED",
        }

    async def submit_application(self, application_id: Any) -> str:
        app = await self.app_repo.get_by_id(application_id)
        if not app:
            raise ValueError("Application not found")
        await self.state_machine.transition(app.id, app.status, ApplicationStatus.SUBMITTED)
        gov_ref = f"JS-GOV-{uuid.uuid4().hex[:8].upper()}"
        await self.app_repo.record_provider_response(app.id, gov_ref)
        return gov_ref

    async def simulate_government_action(self, application_id: Any, action: str, reason: str = None) -> None:
        """Deterministic helper for testing lifecycle progressions."""
        app = await self.app_repo.get_by_id(application_id)
        if not app:
            return
        if action == "REVIEW":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.UNDER_REVIEW)
        elif action == "REQUIRE_EVIDENCE":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.REQUIRES_EVIDENCE)
            if reason:
                await self.app_repo.record_provider_response(app.id, app.government_reference_id, rejection_reason=reason)
        elif action == "APPROVE":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.APPROVED)
        elif action == "REJECT":
            await self.state_machine.transition(app.id, app.status, ApplicationStatus.REJECTED)
            if reason:
                await self.app_repo.record_provider_response(app.id, app.government_reference_id, rejection_reason=reason)

    async def resubmit_application(self, application_id: Any) -> str:
        app = await self.app_repo.get_by_id(application_id)
        return app.government_reference_id or "UNKNOWN"

    async def get_application_status(self, application_id: Any) -> str:
        app = await self.app_repo.get_by_id(application_id)
        return app.status.name if app else "UNKNOWN"
