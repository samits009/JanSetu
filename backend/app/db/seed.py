"""
JanSetu Development Database Seed

Creates the Ramesh Kumar demo scenario with:
- Deterministic citizen UUID for VITE_DEMO_CITIZEN_ID
- Household, employment, locations
- Documents and evidence
- Multiple welfare schemes with eligibility rules
- Benefits (active, at-risk)
- A sample application with ApplicationRequirement instances
"""
import asyncio
import os
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models import (
    Citizen, Household, HouseholdMember, Employment, Location,
    Document, Evidence, Scheme, SchemeEligibilityRule, SchemeVersion,
    Benefit, BenefitRisk, WelfareApplication, ApplicationRequirement
)
from app.domain.enums import SchemeCategory, ApplicationStatus, BenefitStatus
from dotenv import load_dotenv

load_dotenv()

# ── Deterministic UUIDs for demo stability ──────────────────────────
RAMESH_UUID = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
BOCW_SCHEME_UUID = uuid.UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901")
ONORC_SCHEME_UUID = uuid.UUID("c3d4e5f6-a7b8-9012-cdef-123456789012")
EDUCATION_SCHEME_UUID = uuid.UUID("d4e5f6a7-b8c9-0123-defa-234567890123")
UP_WORKER_SCHEME_UUID = uuid.UUID("e5f6a7b8-c9d0-1234-efab-345678901234")


async def seed_database(db_url: str = None):
    if not db_url:
        db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set")
        return

    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(text("SELECT COUNT(*) FROM citizens"))
        count = result.scalar()
        if count > 0:
            print("Database already seeded. Drop tables first to re-seed.")
            return

        # ── 1. Citizen ────────────────────────────────────────────
        ramesh = Citizen(
            id=RAMESH_UUID,
            name="Ramesh Kumar",
            phone="9876543210",
            dob=date(1994, 1, 1)
        )
        session.add(ramesh)
        await session.flush()

        # ── 2. Household ──────────────────────────────────────────
        household = Household(
            head_citizen_id=ramesh.id,
            annual_income=144000  # ₹12,000 × 12
        )
        session.add(household)
        await session.flush()

        member_self = HouseholdMember(
            household_id=household.id,
            citizen_id=ramesh.id,
            relationship_to_head="SELF"
        )
        session.add(member_self)

        # ── 3. Employment ─────────────────────────────────────────
        employment = Employment(
            citizen_id=ramesh.id,
            occupation="Construction Worker",
            employer_name="L&T Construction",
            is_current=True,
            start_date=date(2023, 6, 1)
        )
        session.add(employment)

        # ── 4. Locations ──────────────────────────────────────────
        home_loc = Location(
            citizen_id=ramesh.id,
            location_type="HOME",
            district="Gorakhpur",
            state="Uttar Pradesh",
            pincode="273001",
            is_active=True
        )
        current_loc = Location(
            citizen_id=ramesh.id,
            location_type="CURRENT",
            district="New Delhi",
            state="Delhi",
            pincode="110001",
            is_active=True
        )
        session.add_all([home_loc, current_loc])

        # ── 5. Documents ──────────────────────────────────────────
        doc_aadhaar = Document(
            citizen_id=ramesh.id,
            document_type="AADHAAR",
            document_number="XXXX-XXXX-1234",
            verification_status="VERIFIED",
            extracted_data={"name": "Ramesh Kumar", "dob": "1994-01-01", "address": "Gorakhpur, UP"}
        )
        doc_worker = Document(
            citizen_id=ramesh.id,
            document_type="BOCW_CARD",
            document_number="BOCW-UP-2023-4567",
            verification_status="VERIFIED",
            extracted_data={"occupation": "Construction Worker", "registration_date": "2023-06-15"}
        )
        doc_ration = Document(
            citizen_id=ramesh.id,
            document_type="RATION_CARD",
            document_number="RC-UP-78901",
            verification_status="VERIFIED",
            extracted_data={"household_size": 4, "category": "BPL"}
        )
        doc_passbook = Document(
            citizen_id=ramesh.id,
            document_type="BANK_PASSBOOK",
            document_number="SBI-12345678",
            verification_status="VERIFIED",
            extracted_data={"bank": "SBI", "ifsc": "SBIN0001234"}
        )
        doc_prev_emp = Document(
            citizen_id=ramesh.id,
            document_type="PREVIOUS_EMPLOYMENT_CERTIFICATE",
            verification_status="VERIFIED",
            extracted_data={"employer": "ABC Builders", "duration_months": 18}
        )
        session.add_all([doc_aadhaar, doc_worker, doc_ration, doc_passbook, doc_prev_emp])
        await session.flush()

        # ── 6. Evidence ───────────────────────────────────────────
        ev_identity = Evidence(
            citizen_id=ramesh.id,
            document_id=doc_aadhaar.id,
            evidence_type="IDENTITY",
            data={"verified_name": "Ramesh Kumar", "dob": "1994-01-01"},
            confidence="HIGH"
        )
        ev_occupation = Evidence(
            citizen_id=ramesh.id,
            document_id=doc_worker.id,
            evidence_type="OCCUPATION",
            data={"occupation": "construction_worker", "registered": True},
            confidence="HIGH"
        )
        ev_income = Evidence(
            citizen_id=ramesh.id,
            document_id=doc_ration.id,
            evidence_type="INCOME",
            data={"ration_category": "BPL", "annual_income": 144000},
            confidence="HIGH"
        )
        ev_employment = Evidence(
            citizen_id=ramesh.id,
            document_id=doc_prev_emp.id,
            evidence_type="EMPLOYMENT",
            data={"employer": "ABC Builders", "duration_months": 18},
            confidence="HIGH"
        )
        ev_bank = Evidence(
            citizen_id=ramesh.id,
            document_id=doc_passbook.id,
            evidence_type="BANK_ACCOUNT",
            data={"bank": "SBI", "verified": True},
            confidence="HIGH"
        )
        session.add_all([ev_identity, ev_occupation, ev_income, ev_employment, ev_bank])
        await session.flush()

        # ── 7. Schemes ────────────────────────────────────────────

        # BOCW Worker Welfare (state-level, UP-specific for testing portability)
        bocw_scheme = Scheme(
            id=BOCW_SCHEME_UUID,
            official_name="BOCW Worker Welfare Board",
            authority="Ministry of Labour",
            level="STATE",
            state="Uttar Pradesh",
            category=SchemeCategory.EMPLOYMENT,
            description="Benefits for registered construction workers including pension, health, and education assistance.",
            benefit_amount=3000,
            benefit_description="Monthly assistance for construction workers",
            official_source="bocw.gov.in",
            requirement_definitions=[
                {"id": "req_identity", "name": "Identity Proof", "type": "IDENTITY"},
                {"id": "req_occupation", "name": "Construction Worker Registration", "type": "OCCUPATION"},
                {"id": "req_employment", "name": "Employment Evidence (90+ days)", "type": "EMPLOYMENT"},
            ]
        )

        # ONORC (central, portable)
        onorc_scheme = Scheme(
            id=ONORC_SCHEME_UUID,
            official_name="One Nation One Ration Card",
            authority="Ministry of Consumer Affairs",
            level="CENTRAL",
            state=None,
            category=SchemeCategory.NUTRITION,
            description="Portable ration entitlement across India.",
            benefit_amount=0,
            benefit_description="Subsidized food grains available at any fair price shop nationwide",
            official_source="impds.nic.in",
            requirement_definitions=[
                {"id": "req_identity", "name": "Identity Proof", "type": "IDENTITY"},
                {"id": "req_ration", "name": "Ration Card", "type": "INCOME"},
            ]
        )

        # Education Assistance (Delhi-specific)
        education_scheme = Scheme(
            id=EDUCATION_SCHEME_UUID,
            official_name="Worker Child Education Assistance",
            authority="Delhi Labour Department",
            level="STATE",
            state="Delhi",
            category=SchemeCategory.EDUCATION,
            description="Education support for children of registered construction workers in Delhi.",
            benefit_amount=12000,
            benefit_description="Annual education assistance of ₹12,000 per child",
            official_source="delhi.gov.in",
            requirement_definitions=[
                {"id": "req_identity", "name": "Identity Proof", "type": "IDENTITY"},
                {"id": "req_occupation", "name": "Worker Registration", "type": "OCCUPATION"},
                {"id": "req_income", "name": "Income Proof", "type": "INCOME"},
            ]
        )

        # UP Worker Assistance (state-level, UP-specific)
        up_worker_scheme = Scheme(
            id=UP_WORKER_SCHEME_UUID,
            official_name="UP Construction Worker Assistance",
            authority="UP Labour Department",
            level="STATE",
            state="Uttar Pradesh",
            category=SchemeCategory.EMPLOYMENT,
            description="Financial assistance for construction workers registered in UP.",
            benefit_amount=5000,
            benefit_description="Quarterly financial assistance for UP-registered workers",
            official_source="uplabour.gov.in",
            requirement_definitions=[
                {"id": "req_identity", "name": "Identity Proof", "type": "IDENTITY"},
                {"id": "req_occupation", "name": "Worker Registration", "type": "OCCUPATION"},
            ]
        )

        session.add_all([bocw_scheme, onorc_scheme, education_scheme, up_worker_scheme])
        await session.flush()
        
        # ── 7.5 Scheme Versions ────────────────────────────────────
        
        bocw_version = SchemeVersion(scheme_id=BOCW_SCHEME_UUID, version_number=1, verification_status="VERIFIED", requirement_definitions=bocw_scheme.requirement_definitions)
        onorc_version = SchemeVersion(scheme_id=ONORC_SCHEME_UUID, version_number=1, verification_status="VERIFIED", requirement_definitions=onorc_scheme.requirement_definitions)
        education_version = SchemeVersion(scheme_id=EDUCATION_SCHEME_UUID, version_number=1, verification_status="VERIFIED", requirement_definitions=education_scheme.requirement_definitions)
        up_worker_version = SchemeVersion(scheme_id=UP_WORKER_SCHEME_UUID, version_number=1, verification_status="VERIFIED", requirement_definitions=up_worker_scheme.requirement_definitions)

        session.add_all([bocw_version, onorc_version, education_version, up_worker_version])
        await session.flush()
        
        bocw_scheme.current_version_id = bocw_version.id
        onorc_scheme.current_version_id = onorc_version.id
        education_scheme.current_version_id = education_version.id
        up_worker_scheme.current_version_id = up_worker_version.id
        
        await session.flush()

        # ── 8. Eligibility Rules ──────────────────────────────────

        # BOCW: age >= 18, occupation == Construction Worker
        bocw_rule_age = SchemeEligibilityRule(
            version_id=bocw_version.id,
            scheme_id=BOCW_SCHEME_UUID,
            rule_type="AGE",
            operator=">=",
            value=18
        )
        bocw_rule_occupation = SchemeEligibilityRule(
            version_id=bocw_version.id,
            scheme_id=BOCW_SCHEME_UUID,
            rule_type="OCCUPATION",
            operator="==",
            value="Construction Worker"
        )

        # ONORC: income <= 250000
        onorc_rule_income = SchemeEligibilityRule(
            version_id=onorc_version.id,
            scheme_id=ONORC_SCHEME_UUID,
            rule_type="INCOME",
            operator="<=",
            value=250000
        )

        # Education: age >= 18, occupation == Construction Worker
        edu_rule_age = SchemeEligibilityRule(
            version_id=education_version.id,
            scheme_id=EDUCATION_SCHEME_UUID,
            rule_type="AGE",
            operator=">=",
            value=18
        )
        edu_rule_occupation = SchemeEligibilityRule(
            version_id=education_version.id,
            scheme_id=EDUCATION_SCHEME_UUID,
            rule_type="OCCUPATION",
            operator="==",
            value="Construction Worker"
        )

        # UP Worker: occupation == Construction Worker, state == Uttar Pradesh
        up_rule_occupation = SchemeEligibilityRule(
            version_id=up_worker_version.id,
            scheme_id=UP_WORKER_SCHEME_UUID,
            rule_type="OCCUPATION",
            operator="==",
            value="Construction Worker"
        )
        up_rule_state = SchemeEligibilityRule(
            version_id=up_worker_version.id,
            scheme_id=UP_WORKER_SCHEME_UUID,
            rule_type="STATE",
            operator="==",
            value="Uttar Pradesh"
        )

        session.add_all([
            bocw_rule_age, bocw_rule_occupation,
            onorc_rule_income,
            edu_rule_age, edu_rule_occupation,
            up_rule_occupation, up_rule_state,
        ])
        await session.flush()

        # ── 9. Benefits (Ramesh's active/at-risk benefits) ────────

        benefit_onorc = Benefit(
            citizen_id=ramesh.id,
            scheme_id=ONORC_SCHEME_UUID,
            scheme_version_id=onorc_version.id,
            status=BenefitStatus.ACTIVE,
            next_renewal_date=None  # Central, auto-renewed
        )
        benefit_bocw = Benefit(
            citizen_id=ramesh.id,
            scheme_id=BOCW_SCHEME_UUID,
            scheme_version_id=bocw_version.id,
            status=BenefitStatus.ACTIVE,
            next_renewal_date=date(2026, 9, 21)  # 12 days from now
        )
        benefit_up_worker = Benefit(
            citizen_id=ramesh.id,
            scheme_id=UP_WORKER_SCHEME_UUID,
            scheme_version_id=up_worker_version.id,
            status=BenefitStatus.AT_RISK,
        )
        session.add_all([benefit_onorc, benefit_bocw, benefit_up_worker])
        await session.flush()

        # ── 10. Benefit Risks ─────────────────────────────────────

        risk_bocw = BenefitRisk(
            benefit_id=benefit_bocw.id,
            risk_type="RENEWAL_EXPIRING",
            description="BOCW membership renewal due in 12 days. Failure to renew will result in loss of benefits.",
            is_resolved=False
        )
        risk_up = BenefitRisk(
            benefit_id=benefit_up_worker.id,
            risk_type="LOCATION_CHANGE",
            description="UP-linked worker assistance may not continue after migration to Delhi.",
            is_resolved=False
        )
        session.add_all([risk_bocw, risk_up])
        await session.flush()

        # ── 11. Sample Application (BOCW renewal — REQUIRES_EVIDENCE) ──

        app_bocw = WelfareApplication(
            citizen_id=ramesh.id,
            scheme_id=BOCW_SCHEME_UUID,
            scheme_version_id=bocw_version.id,
            status=ApplicationStatus.REQUIRES_EVIDENCE,
            rejection_reason="Additional employment proof is required to verify continuous work history.",
            government_reference_id="MOCK-GOV-BOCW001",
            snapshot={
                "eligibility_result": {"status": "eligible", "confidence": "high"},
                "timestamp": "2026-09-08T10:00:00Z"
            }
        )
        session.add(app_bocw)
        await session.flush()

        # ── 12. ApplicationRequirement (linked to application, NOT scheme) ──
        # This is the corrected lifecycle:
        # Scheme defines requirement_definitions (JSONB)
        # → Application is created
        # → ApplicationRequirement rows are created with application_id

        app_req_identity = ApplicationRequirement(
            application_id=app_bocw.id,
            requirement_type="IDENTITY",
            description="Identity Proof (Aadhaar)",
            is_mandatory=True
        )
        app_req_occupation = ApplicationRequirement(
            application_id=app_bocw.id,
            requirement_type="OCCUPATION",
            description="Construction Worker Registration (BOCW Card)",
            is_mandatory=True
        )
        app_req_employment = ApplicationRequirement(
            application_id=app_bocw.id,
            requirement_type="EMPLOYMENT",
            description="Employment Evidence (90+ days continuous work history)",
            is_mandatory=True
        )
        session.add_all([app_req_identity, app_req_occupation, app_req_employment])
        await session.flush()

        # ── Commit ────────────────────────────────────────────────
        await session.commit()

        print("=" * 60)
        print("Database seeded successfully.")
        print(f"  Ramesh UUID: {RAMESH_UUID}")
        print(f"  Use VITE_DEMO_CITIZEN_ID={RAMESH_UUID}")
        print(f"  BOCW Scheme:      {BOCW_SCHEME_UUID}")
        print(f"  ONORC Scheme:     {ONORC_SCHEME_UUID}")
        print(f"  Education Scheme: {EDUCATION_SCHEME_UUID}")
        print(f"  UP Worker Scheme: {UP_WORKER_SCHEME_UUID}")
        print(f"  BOCW Application: {app_bocw.id}")
        print(f"  Benefits: ONORC(ACTIVE), BOCW(ACTIVE+risk), UP Worker(AT_RISK)")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
