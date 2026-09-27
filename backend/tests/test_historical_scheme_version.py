import pytest
from app.models.citizen import Citizen
from app.models.scheme import Scheme, SchemeVersion, SchemeEligibilityRule, SchemeSource
from app.models.application import WelfareApplication
from app.domain.enums import ApplicationStatus, VerificationStatus

@pytest.mark.asyncio
async def test_historical_application_version_lock(db_session):
    # 1. Create a Scheme and V1
    scheme = Scheme(
        official_name="Historical Lock Scheme",
        category="EDUCATION",
        level="CENTRAL"
    )
    db_session.add(scheme)
    await db_session.flush()

    v1 = SchemeVersion(
        scheme_id=scheme.id,
        version_number=1,
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(v1)
    await db_session.flush()
    scheme.current_version_id = v1.id
    await db_session.flush()

    # 2. Create Citizen and Application linked to V1
    citizen = Citizen(name="Old Applicant")
    db_session.add(citizen)
    await db_session.flush()

    app1 = WelfareApplication(
        citizen_id=citizen.id,
        scheme_id=scheme.id,
        scheme_version_id=scheme.current_version_id,
        status=ApplicationStatus.APPROVED
    )
    db_session.add(app1)
    await db_session.flush()

    # 3. Create V2 of Scheme (e.g. policy change)
    v2 = SchemeVersion(
        scheme_id=scheme.id,
        version_number=2,
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(v2)
    await db_session.flush()
    scheme.current_version_id = v2.id
    await db_session.flush()

    # 4. Create new Application linked to V2
    citizen2 = Citizen(name="New Applicant")
    db_session.add(citizen2)
    await db_session.flush()

    app2 = WelfareApplication(
        citizen_id=citizen2.id,
        scheme_id=scheme.id,
        scheme_version_id=scheme.current_version_id,
        status=ApplicationStatus.SUBMITTED
    )
    db_session.add(app2)
    await db_session.flush()

    # 5. Verify Isolation
    assert app1.scheme_version_id == v1.id
    assert app2.scheme_version_id == v2.id
    assert scheme.current_version_id == v2.id
