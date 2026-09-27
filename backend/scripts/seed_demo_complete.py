"""
Seed comprehensive demo citizen data into RDS PostgreSQL for live UI showcase.
Populates citizen profile, employment, location, household, documents, evidence,
active benefits, and applications for suresh_demo2026@jansetu.in and demo@jansetu.in.
"""
import asyncio
import os
import uuid
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select, text

from app.models import (
    Citizen, Household, HouseholdMember, Employment, Location,
    Document, Evidence, Scheme, SchemeVersion,
    Benefit, BenefitRisk, WelfareApplication, ApplicationRequirement
)
from app.models.identity import User, Identity, AuthIdentity
from app.domain.enums import ApplicationStatus, BenefitStatus
from app.services.password import hash_password

DB_URL = "postgresql+asyncpg://jansetu_admin:jansetu198182@jansetu-db.c7ois8uec6yb.ap-southeast-2.rds.amazonaws.com:5432/jansetu_prod?ssl=require"

TARGET_USERS = [
    ("suresh_demo2026@jansetu.in", "+919876543210", "Suresh Kumar Demo"),
    ("demo@jansetu.in", "+919812345678", "Aarav Sharma Demo"),
]

async def seed():
    engine = create_async_engine(DB_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get existing schemes
        schemes_res = await session.execute(
            select(Scheme).options(selectinload(Scheme.current_version))
        )
        schemes = schemes_res.scalars().all()
        print(f"Loaded {len(schemes)} schemes from DB.")

        scheme_map = {s.official_name: s for s in schemes}
        first_scheme = schemes[0] if schemes else None
        second_scheme = schemes[1] if len(schemes) > 1 else first_scheme

        for email, phone, full_name in TARGET_USERS:
            # 1. Check or create User
            u_res = await session.execute(select(User).where(User.email == email))
            user = u_res.scalars().first()

            if not user:
                citizen = Citizen(
                    id=uuid.uuid4(),
                    name=full_name,
                    phone=phone,
                    dob=date(1994, 5, 15),
                    onboarding_completed=True,
                    onboarding_step=4,
                )
                session.add(citizen)
                await session.flush()

                identity = Identity(
                    id=uuid.uuid4(),
                    citizen_id=citizen.id,
                    role="CITIZEN",
                    verification_state="IDENTITY_VERIFIED",
                    active=True,
                )
                session.add(identity)
                await session.flush()

                user = User(
                    id=uuid.uuid4(),
                    email=email,
                    phone=phone,
                    mobile_number=phone,
                    password_hash=hash_password("DemoPassword123!"),
                    citizen_id=citizen.id,
                    identity_id=identity.id,
                    preferred_language="hi",
                    is_active=True,
                    email_verified=True,
                    mobile_verified=True,
                    account_status="ACTIVE",
                )
                session.add(user)
                await session.flush()

                auth_id = AuthIdentity(
                    user_id=user.id,
                    provider="password",
                    provider_subject=email,
                    provider_email=email,
                )
                session.add(auth_id)
                await session.flush()
                print(f"Created new user {email}")
            else:
                # Update existing citizen
                citizen = await session.get(Citizen, user.citizen_id)
                if citizen:
                    citizen.onboarding_completed = True
                    citizen.onboarding_step = 4
                    citizen.dob = date(1994, 5, 15)
                user.email_verified = True
                user.mobile_verified = True
                print(f"Updated existing user {email}")

            cid = user.citizen_id

            # 2. Household
            hh_res = await session.execute(select(Household).where(Household.head_citizen_id == cid))
            hh = hh_res.scalars().first()
            if not hh:
                hh = Household(head_citizen_id=cid, annual_income=144000)
                session.add(hh)
                await session.flush()
                session.add(HouseholdMember(household_id=hh.id, citizen_id=cid, relationship_to_head="SELF"))

            # 3. Employment
            emp_res = await session.execute(select(Employment).where(Employment.citizen_id == cid))
            if not emp_res.scalars().first():
                session.add(Employment(
                    citizen_id=cid,
                    occupation="Construction Mason / BOCW Worker",
                    employer_name="National Infrastructure Consortium",
                    is_current=True,
                    start_date=date(2023, 1, 10),
                ))

            # 4. Locations
            loc_res = await session.execute(select(Location).where(Location.citizen_id == cid))
            if not loc_res.scalars().first():
                session.add_all([
                    Location(
                        citizen_id=cid,
                        location_type="HOME",
                        district="Gorakhpur",
                        state="Uttar Pradesh",
                        pincode="273001",
                        is_active=True,
                    ),
                    Location(
                        citizen_id=cid,
                        location_type="CURRENT",
                        district="South Delhi",
                        state="Delhi",
                        pincode="110017",
                        is_active=True,
                    ),
                ])

            # 5. Documents
            doc_res = await session.execute(select(Document).where(Document.citizen_id == cid))
            existing_docs = doc_res.scalars().all()
            if not existing_docs:
                d1 = Document(
                    citizen_id=cid,
                    document_type="AADHAAR",
                    document_number="XXXX-XXXX-9812",
                    verification_status="VERIFIED",
                    extracted_data={"name": full_name, "dob": "1994-05-15", "gender": "M"},
                )
                d2 = Document(
                    citizen_id=cid,
                    document_type="BOCW_CARD",
                    document_number="BOCW-2024-DEL-49102",
                    verification_status="VERIFIED",
                    extracted_data={"trade": "Masonry", "board": "BOCW Welfare Board"},
                )
                d3 = Document(
                    citizen_id=cid,
                    document_type="RATION_CARD",
                    document_number="RC-NFSA-782103",
                    verification_status="VERIFIED",
                    extracted_data={"type": "PHH", "members_count": 4},
                )
                d4 = Document(
                    citizen_id=cid,
                    document_type="BANK_PASSBOOK",
                    document_number="SBI-8829104",
                    verification_status="VERIFIED",
                    extracted_data={"bank": "State Bank of India", "ifsc": "SBIN0001042"},
                )
                session.add_all([d1, d2, d3, d4])
                await session.flush()

                # 6. Evidence
                session.add_all([
                    Evidence(citizen_id=cid, document_id=d1.id, evidence_type="IDENTITY", data={"verified": True, "method": "UIDAI"}),
                    Evidence(citizen_id=cid, document_id=d2.id, evidence_type="OCCUPATION", data={"verified": True, "trade": "Masonry"}),
                    Evidence(citizen_id=cid, document_id=d3.id, evidence_type="FOOD_SECURITY", data={"ration_eligible": True}),
                    Evidence(citizen_id=cid, document_id=d4.id, evidence_type="DIRECT_BENEFIT_TRANSFER", data={"dbt_enabled": True}),
                ])

            # 7. Benefits
            b_res = await session.execute(select(Benefit).where(Benefit.citizen_id == cid))
            if not b_res.scalars().first() and first_scheme:
                first_version_id = first_scheme.current_version.id if first_scheme.current_version else None
                b1 = Benefit(
                    citizen_id=cid,
                    scheme_id=first_scheme.id,
                    scheme_version_id=first_version_id,
                    status=BenefitStatus.ACTIVE,
                    next_renewal_date=date(2026, 10, 15),
                )
                session.add(b1)
                await session.flush()

                risk1 = BenefitRisk(
                    benefit_id=b1.id,
                    risk_type="RENEWAL_EXPIRING",
                    description="Welfare entitlement annual renewal due within 30 days. Auto-continuity enabled.",
                    is_resolved=False,
                )
                session.add(risk1)

                if second_scheme and second_scheme.id != first_scheme.id:
                    sec_version_id = second_scheme.current_version.id if second_scheme.current_version else None
                    b2 = Benefit(
                        citizen_id=cid,
                        scheme_id=second_scheme.id,
                        scheme_version_id=sec_version_id,
                        status=BenefitStatus.ACTIVE,
                    )
                    session.add(b2)

            # 8. Welfare Application
            app_res = await session.execute(select(WelfareApplication).where(WelfareApplication.citizen_id == cid))
            if not app_res.scalars().first() and first_scheme:
                first_version_id = first_scheme.current_version.id if first_scheme.current_version else None
                app = WelfareApplication(
                    citizen_id=cid,
                    scheme_id=first_scheme.id,
                    scheme_version_id=first_version_id,
                    status=ApplicationStatus.REQUIRES_EVIDENCE,
                    rejection_reason="Annual renewal verification: continuous informal work certificate is requested.",
                    government_reference_id=f"JANSETU-{uuid.uuid4().hex[:8].upper()}",
                    snapshot={"eligibility_result": {"status": "eligible", "confidence": "high"}},
                )
                session.add(app)
                await session.flush()

                session.add_all([
                    ApplicationRequirement(
                        application_id=app.id,
                        requirement_type="IDENTITY",
                        description="Aadhaar Biometric Verification",
                        is_mandatory=True,
                    ),
                    ApplicationRequirement(
                        application_id=app.id,
                        requirement_type="EMPLOYMENT",
                        description="90-Day Construction Work Continuous Attestation",
                        is_mandatory=True,
                    ),
                ])

        await session.commit()
        print("Demo data seeded and verified successfully in RDS!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
