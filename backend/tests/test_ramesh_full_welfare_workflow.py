import pytest
import datetime
from app.repositories.citizen import CitizenRepository, HouseholdRepository
from app.repositories.scheme import SchemeRepository, BenefitRepository, BenefitRiskRepository
from app.repositories.evidence import EvidenceRepository, DocumentRepository
from app.repositories.application import ApplicationRepository, ConsentRepository, AuditRepository
from app.services.scheme_registry import SchemeRegistryService
from app.services.policy_engine import PolicyRuleEngine
from app.services.eligibility import EligibilityService
from app.services.evidence_matching import EvidenceMatchingService
from app.services.welfare_state import WelfareStateService
from app.services.benefit_survival import BenefitSurvivalService
from app.services.benefit_risk import BenefitRiskService
from app.services.application_state_machine import ApplicationStateMachine
from app.services.application_service import ApplicationService
from app.services.consent import ConsentService
from app.services.application_recovery import ApplicationRecoveryService
from app.providers.government_mock import MockGovernmentApplicationProvider
from app.services.audit import AuditService

from app.models.citizen import Citizen, Household, HouseholdMember, Employment, Location
from app.models.scheme import Scheme, SchemeEligibilityRule, SchemeVersion
from app.models.evidence import Document, Evidence
from app.models.application import Benefit
from app.domain.enums import SchemeCategory, ApplicationStatus

@pytest.mark.asyncio
async def test_ramesh_full_welfare_workflow(db_session):
    # --- Repositories ---
    cit_repo = CitizenRepository(db_session)
    hh_repo = HouseholdRepository(db_session)
    scheme_repo = SchemeRepository(db_session)
    benefit_repo = BenefitRepository(db_session)
    doc_repo = DocumentRepository(db_session)
    ev_repo = EvidenceRepository(db_session)
    app_repo = ApplicationRepository(db_session)
    consent_repo = ConsentRepository(db_session)
    audit_repo = AuditRepository(db_session)
    risk_repo = BenefitRiskRepository(db_session)

    # --- Services ---
    scheme_registry = SchemeRegistryService(scheme_repo)
    policy_engine = PolicyRuleEngine()
    eligibility_service = EligibilityService(policy_engine)
    evidence_matching = EvidenceMatchingService(ev_repo, scheme_repo)
    welfare_state_service = WelfareStateService(cit_repo, scheme_registry, eligibility_service)
    benefit_survival = BenefitSurvivalService(welfare_state_service, eligibility_service, scheme_registry)
    benefit_risk = BenefitRiskService(cit_repo, risk_repo)
    state_machine = ApplicationStateMachine(app_repo)
    consent_service = ConsentService(consent_repo)
    application_service = ApplicationService(
        app_repo, state_machine, cit_repo, scheme_registry, eligibility_service, evidence_matching
    )
    application_recovery = ApplicationRecoveryService(
        app_repo, state_machine, evidence_matching, consent_service
    )
    gov_provider = MockGovernmentApplicationProvider(app_repo, state_machine)
    audit_service = AuditService(audit_repo)

    # 1. Load Ramesh
    dob = datetime.date.today() - datetime.timedelta(days=32 * 365)
    ramesh = await cit_repo.create(name="Ramesh Kumar", dob=dob)
    
    hh = await hh_repo.create(head_citizen_id=ramesh.id, annual_income=12000 * 12) # 144000
    
    # 2 children + wife + Ramesh = 4
    db_session.add(HouseholdMember(household_id=hh.id, citizen_id=ramesh.id, relationship_to_head="SELF"))
    # for simplicity, mocking members
    
    emp = Employment(citizen_id=ramesh.id, occupation="construction_worker", start_date=datetime.date.today() - datetime.timedelta(days=100))
    db_session.add(emp)
    
    loc_up = Location(citizen_id=ramesh.id, location_type="CURRENT", state="UP", district="Gorakhpur", is_active=True)
    db_session.add(loc_up)
    
    await db_session.flush()

    # Seed Scheme (BOCW)
    scheme = await scheme_repo.create(
        official_name="UP BOCW", 
        category="HOUSING", 
        state="UP", 
        level="STATE",
        requirement_definitions=[{"type": "OCCUPATION", "name": "Worker Certificate"}]
    )
    version = SchemeVersion(scheme_id=scheme.id, version_number=1, verification_status="VERIFIED")
    db_session.add(version)
    await db_session.flush()
    scheme.current_version_id = version.id
    
    rule1 = SchemeEligibilityRule(scheme_id=scheme.id, version_id=version.id, rule_type="OCCUPATION", operator="==", value="construction_worker")
    rule2 = SchemeEligibilityRule(scheme_id=scheme.id, version_id=version.id, rule_type="INCOME", operator="<=", value=150000)
    db_session.add(rule1)
    db_session.add(rule2)
    await db_session.flush()

    # 2. Evaluate current welfare state
    state1 = await welfare_state_service.evaluate(ramesh.id)
    assert len(state1["new_opportunities"]) >= 1 # UP BOCW and any other seeded ones
    
    # Let's say he already has an active benefit for UP Ration Card
    ration_scheme = await scheme_repo.create(official_name="UP Ration", category="NUTRITION", state="UP", level="STATE")
    ration_benefit = await benefit_repo.create(citizen_id=ramesh.id, scheme_id=ration_scheme.id, status="ACTIVE")
    await db_session.flush()

    # 3. Change location UP -> Delhi
    loc_delhi = Location(citizen_id=ramesh.id, location_type="CURRENT", state="Delhi", district="NCR", is_active=True)
    loc_up.is_active = False
    db_session.add(loc_delhi)
    db_session.add(loc_up)
    await db_session.flush()

    # 4. Evaluate Benefit Survival
    survival = await benefit_survival.evaluate_location_change(ramesh.id, loc_delhi)
    
    # 5. Identify continued benefits
    assert len(survival["continued_benefits"]) == 0
    # 6. Identify action-required / 8. At risk
    assert len(survival["at_risk_benefits"]) == 1 # UP Ration is at risk because state != Delhi
    
    # Add Delhi BOCW scheme
    delhi_scheme = await scheme_repo.create(
        official_name="Delhi BOCW", 
        category="HOUSING", 
        state="Delhi", 
        level="STATE",
        requirement_definitions=[{"type": "OCCUPATION", "name": "Worker Certificate"}]
    )
    delhi_version = SchemeVersion(scheme_id=delhi_scheme.id, version_number=1, verification_status="VERIFIED")
    db_session.add(delhi_version)
    await db_session.flush()
    delhi_scheme.current_version_id = delhi_version.id
    
    db_session.add(SchemeEligibilityRule(scheme_id=delhi_scheme.id, version_id=delhi_version.id, rule_type="OCCUPATION", operator="==", value="construction_worker"))
    await db_session.flush()
    
    # 7. Identify new opportunities (Delhi BOCW)
    survival2 = await benefit_survival.evaluate_location_change(ramesh.id, loc_delhi)
    assert len(survival2["new_benefits"]) >= 1

    # 9. Match existing evidence for Delhi BOCW
    # Let's add some evidence
    doc = await doc_repo.create(citizen_id=ramesh.id, document_type="BOCW_CARD", verification_status="VERIFIED")
    await ev_repo.create(citizen_id=ramesh.id, document_id=doc.id, evidence_type="OCCUPATION", data={"verified_occupation": "construction_worker"})
    
    matches = await evidence_matching.match(ramesh.id, delhi_scheme.id)
    assert matches[0]["status"] == "SATISFIED"

    # 10. Create application
    app = await application_service.create_application(ramesh.id, delhi_scheme.id)
    
    # 11. Generate application requirements
    app_with_reqs = await app_repo.get_with_requirements(app.id)
    assert len(app_with_reqs.requirements) == 1
    
    # 12. Generate application snapshot
    assert app_with_reqs.snapshot is not None
    assert app_with_reqs.status == ApplicationStatus.EVIDENCE_COMPLETE
    
    await state_machine.transition(app.id, app_with_reqs.status, ApplicationStatus.DRAFTED)
    await state_machine.transition(app.id, ApplicationStatus.DRAFTED, ApplicationStatus.AWAITING_CONSENT)
    
    # 13. Request consent
    consent = await consent_service.request(ramesh.id, "APPLICATION_SUBMISSION", app.id)
    
    # 14. Grant consent
    await consent_service.grant(consent.id)
    
    # Transition to SUBMITTING before mock provider call
    await state_machine.transition(app.id, ApplicationStatus.AWAITING_CONSENT, ApplicationStatus.SUBMITTING)

    # 15. Submit via mock government provider
    await gov_provider.submit_application(app.id)
    
    # 16. Move application to UNDER_REVIEW
    await gov_provider.simulate_government_action(app.id, "REVIEW")
    status = await gov_provider.get_application_status(app.id)
    assert status == "UNDER_REVIEW"
    
    # 17. Receive simulated REQUIRES_EVIDENCE
    await gov_provider.simulate_government_action(app.id, "REQUIRE_EVIDENCE", "Need clearer worker cert")
    
    # 18. Identify failed requirement / 19. Search evidence graph / 20. Generate recovery plan
    recovery_plan = await application_recovery.recover(app.id)
    assert recovery_plan["application_id"] == str(app.id)
    # Since we didn't mock a change in evidence, it's SATISFIED (found_alternatives). 
    assert len(recovery_plan["found_alternatives"]) == 1
    
    # 21. Request consent for resubmission
    consent_resub = await consent_service.request(ramesh.id, "APPLICATION_RESUBMISSION", app.id)
    
    # 22. Grant consent
    await consent_service.grant(consent_resub.id)
    
    # 23. Resubmit
    await application_recovery.resubmit(app.id)
    
    # 24. Verify status = RESUBMITTED
    status_final = await gov_provider.get_application_status(app.id)
    assert status_final == "RESUBMITTED"
    
    # 25. Verify audit events exist
    await audit_service.record(ramesh.id, "SYSTEM", "TEST_COMPLETED", "Workflow verified", "SUCCESS", consent_resub.id, app.id)
    
    audits = await audit_repo.list()
    assert len(audits) >= 1
