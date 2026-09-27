import asyncio
import os
import uuid
from datetime import date
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.models.scheme import Scheme, SchemeVersion, SchemeEligibilityRule, SchemeSource
from app.domain.enums import SchemeCategory, VerificationStatus, SourceType, JurisdictionLevel

# Pre-defined UUIDs for deterministic reference
SCHEMES_DATA = [
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555551"),
        "official_name": "National Means-cum-Merit Scholarship Scheme (NMMSS)",
        "authority": "Department of School Education & Literacy, Ministry of Education",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.EDUCATION,
        "description": "Central scholarship for meritorious students from economically weaker sections studying in class 9 through 12 in state/govt-aided schools.",
        "benefit_amount": 12000,
        "benefit_description": "₹12,000 per annum (₹1,000 per month deposited directly into student's bank account).",
        "official_source": "scholarships.gov.in (National Scholarship Portal)",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_income", "name": "Income Certificate (≤ ₹3.5 Lakhs)", "type": "INCOME"},
            {"id": "req_marksheet", "name": "Class 8 Marksheet (Min 55% marks)", "type": "ACADEMIC"},
            {"id": "req_school", "name": "Government/Govt-Aided School Enrollment Certificate", "type": "EDUCATION"},
            {"id": "req_bank", "name": "Student Bank Passbook", "type": "BANK_ACCOUNT"}
        ],
        "rules": [
            {"rule_type": "OCCUPATION", "operator": "==", "value": "student"},
            {"rule_type": "INCOME", "operator": "<=", "value": 350000},
            {"rule_type": "AGE", "operator": "<=", "value": 19}
        ]
    },
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555552"),
        "official_name": "Post-Matric Scholarship for SC/ST/OBC Students",
        "authority": "Ministry of Social Justice and Empowerment",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.EDUCATION,
        "description": "Comprehensive scholarship covering 100% compulsory non-refundable fees and monthly living allowance for higher education (Class 11 to PhD).",
        "benefit_amount": 13500,
        "benefit_description": "100% Tuition fee waiver + annual maintenance allowance up to ₹13,500.",
        "official_source": "scholarships.gov.in",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_caste", "name": "Caste Certificate (SC/ST/OBC)", "type": "SOCIAL_CATEGORY"},
            {"id": "req_income", "name": "Income Certificate (≤ ₹2.5 Lakhs)", "type": "INCOME"},
            {"id": "req_admission", "name": "College / Higher Secondary Admission Receipt", "type": "EDUCATION"},
            {"id": "req_bank", "name": "Aadhaar-seeded Bank Passbook", "type": "BANK_ACCOUNT"}
        ],
        "rules": [
            {"rule_type": "OCCUPATION", "operator": "==", "value": "student"},
            {"rule_type": "INCOME", "operator": "<=", "value": 250000}
        ]
    },
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555553"),
        "official_name": "AICTE Pragati Scholarship for Girl Students",
        "authority": "All India Council for Technical Education (AICTE)",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.EDUCATION,
        "description": "Empowers female students admitted to 1st year of technical degree/diploma programs in AICTE-approved institutions with tuition and equipment support.",
        "benefit_amount": 50000,
        "benefit_description": "₹50,000 per annum towards college fee, computer/laptop purchase, books, and stationeries.",
        "official_source": "aicte-india.org",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_gender", "name": "Female Candidate Verification", "type": "GENDER"},
            {"id": "req_aicte_admission", "name": "AICTE Technical College Admission Letter", "type": "EDUCATION"},
            {"id": "req_income", "name": "Family Income Certificate (≤ ₹8.0 Lakhs)", "type": "INCOME"},
            {"id": "req_bank", "name": "Student Bank Passbook", "type": "BANK_ACCOUNT"}
        ],
        "rules": [
            {"rule_type": "OCCUPATION", "operator": "==", "value": "student"},
            {"rule_type": "GENDER", "operator": "==", "value": "female"},
            {"rule_type": "INCOME", "operator": "<=", "value": 800000}
        ]
    },
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555554"),
        "official_name": "PM-USP Central Sector Scholarship for College and University Students",
        "authority": "Department of Higher Education, Ministry of Education",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.EDUCATION,
        "description": "Financial assistance for meritorious students who scored in the top 20th percentile in Class 12 board examinations and are pursuing regular degree courses.",
        "benefit_amount": 12000,
        "benefit_description": "₹12,000 per annum for graduation (first 3 years) and ₹20,000 per annum at post-graduation level.",
        "official_source": "scholarships.gov.in",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_marksheet_12", "name": "Class 12 Board Marksheet (Top Percentile)", "type": "ACADEMIC"},
            {"id": "req_income", "name": "Income Certificate (≤ ₹4.5 Lakhs)", "type": "INCOME"},
            {"id": "req_college_enrollment", "name": "Regular Degree Enrollment Verification", "type": "EDUCATION"},
            {"id": "req_bank", "name": "Student Bank Passbook", "type": "BANK_ACCOUNT"}
        ],
        "rules": [
            {"rule_type": "OCCUPATION", "operator": "==", "value": "student"},
            {"rule_type": "INCOME", "operator": "<=", "value": 450000},
            {"rule_type": "AGE", "operator": "<=", "value": 25}
        ]
    },
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555555"),
        "official_name": "Begum Hazrat Mahal National Scholarship",
        "authority": "Maulana Azad Education Foundation, Ministry of Minority Affairs",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.EDUCATION,
        "description": "Merit scholarship for girl students belonging to national minority communities (Muslims, Christians, Sikhs, Buddhists, Jains, Parsis) studying in classes 9 to 12.",
        "benefit_amount": 10000,
        "benefit_description": "₹6,000 per year for classes 9-10; ₹12,000 per year for classes 11-12.",
        "official_source": "scholarships.gov.in",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_minority_cert", "name": "Minority Community Certificate / Self-Declaration", "type": "MINORITY"},
            {"id": "req_income", "name": "Income Certificate (≤ ₹2.0 Lakhs)", "type": "INCOME"},
            {"id": "req_marksheet", "name": "Previous Class Marksheet (Min 50% marks)", "type": "ACADEMIC"},
            {"id": "req_school", "name": "School Verification Certificate", "type": "EDUCATION"}
        ],
        "rules": [
            {"rule_type": "OCCUPATION", "operator": "==", "value": "student"},
            {"rule_type": "GENDER", "operator": "==", "value": "female"},
            {"rule_type": "INCOME", "operator": "<=", "value": 200000}
        ]
    },
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555556"),
        "official_name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
        "authority": "National Health Authority",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.HEALTH,
        "description": "World's largest health assurance scheme providing comprehensive cashless health coverage for secondary and tertiary hospitalization.",
        "benefit_amount": 500000,
        "benefit_description": "Cashless health cover up to ₹5,00,000 per family per year across empaneled public and private hospitals.",
        "official_source": "pmjay.gov.in",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_ration", "name": "Ration Card / SECC Name Match", "type": "INCOME"}
        ],
        "rules": [
            {"rule_type": "INCOME", "operator": "<=", "value": 250000}
        ]
    },
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555557"),
        "official_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "authority": "Ministry of Agriculture & Farmers Welfare",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.EMPLOYMENT,
        "description": "Income support scheme providing direct cash assistance to small and marginal farmer families to procure agricultural inputs.",
        "benefit_amount": 6000,
        "benefit_description": "₹6,000 per year paid in three equal installments of ₹2,000 directly into Aadhaar-seeded bank accounts.",
        "official_source": "pmkisan.gov.in",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_land", "name": "Land Record (Khatauni / RoR)", "type": "LAND_RECORD"},
            {"id": "req_bank", "name": "Bank Passbook", "type": "BANK_ACCOUNT"}
        ],
        "rules": [
            {"rule_type": "OCCUPATION", "operator": "==", "value": "farmer"}
        ]
    },
    {
        "id": uuid.UUID("11111111-2222-3333-4444-555555555558"),
        "official_name": "Atal Pension Yojana (APY)",
        "authority": "Pension Fund Regulatory and Development Authority (PFRDA)",
        "level": "CENTRAL",
        "state": None,
        "category": SchemeCategory.PENSION,
        "description": "Guaranteed minimum monthly pension scheme for citizens in the unorganized sector upon reaching the age of 60.",
        "benefit_amount": 5000,
        "benefit_description": "Guaranteed pension of ₹1,000, ₹2,000, ₹3,000, ₹4,000, or ₹5,000 per month based on contribution.",
        "official_source": "npscra.nsdl.co.in",
        "requirements": [
            {"id": "req_identity", "name": "Aadhaar Card", "type": "IDENTITY"},
            {"id": "req_bank", "name": "Savings Bank Account", "type": "BANK_ACCOUNT"}
        ],
        "rules": [
            {"rule_type": "AGE", "operator": ">=", "value": 18},
            {"rule_type": "AGE", "operator": "<=", "value": 40}
        ]
    }
]

async def seed_comprehensive_schemes(db_url: Optional[str] = None):
    target_url = db_url or os.environ.get("DATABASE_URL")
    if not target_url:
        print("DATABASE_URL not found!")
        return

    engine = create_async_engine(target_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create standard fixture source if not existing
        source_stmt = select(SchemeSource).where(SchemeSource.authority == "National Portal of India")
        source = (await session.execute(source_stmt)).scalars().first()
        if not source:
            source = SchemeSource(
                id=uuid.uuid4(),
                authority="National Portal of India",
                source_url="https://www.india.gov.in",
                source_type=SourceType.PORTAL,
                jurisdiction=JurisdictionLevel.CENTRAL,
                active=True
            )
            session.add(source)
            await session.flush()

        inserted_count = 0
        updated_count = 0

        for item in SCHEMES_DATA:
            stmt = select(Scheme).where(Scheme.official_name == item["official_name"])
            existing = (await session.execute(stmt)).scalars().first()

            if existing:
                print(f"Scheme already exists: {item['official_name']}")
                continue

            # Create Scheme
            new_scheme = Scheme(
                id=item["id"],
                official_name=item["official_name"],
                authority=item["authority"],
                level=item["level"],
                state=item["state"],
                category=item["category"],
                description=item["description"],
                benefit_amount=item["benefit_amount"],
                benefit_description=item["benefit_description"],
                official_source=item["official_source"],
                requirement_definitions=item["requirements"]
            )
            session.add(new_scheme)
            await session.flush()

            # Create SchemeVersion
            new_version = SchemeVersion(
                id=uuid.uuid4(),
                scheme_id=new_scheme.id,
                version_number=1,
                verification_status=VerificationStatus.VERIFIED,
                requirement_definitions=item["requirements"],
                source_id=source.id
            )
            session.add(new_version)
            await session.flush()

            # Update current_version_id
            new_scheme.current_version_id = new_version.id

            # Add Eligibility Rules
            for r in item["rules"]:
                rule = SchemeEligibilityRule(
                    id=uuid.uuid4(),
                    scheme_id=new_scheme.id,
                    version_id=new_version.id,
                    rule_type=r["rule_type"],
                    operator=r["operator"],
                    value=r["value"],
                    is_mandatory=True
                )
                session.add(rule)

            inserted_count += 1
            print(f"Added Scheme: {item['official_name']} ({item['category'].value})")

        await session.commit()
        print(f"\nSuccessfully seeded {inserted_count} new national schemes into database!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_comprehensive_schemes())
