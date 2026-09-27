import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.scheme import Scheme, SchemeTranslation, RequirementTranslation

SCHEME_TRANSLATIONS = {
    "Delhi BOCW": {
        "hi": {
            "official_name": "दिल्ली भवन एवं अन्य सन्निर्माण कर्मकार कल्याण (BOCW)",
            "description": "दिल्ली में पंजीकृत निर्माण श्रमिकों और उनके परिवारों के लिए वित्तीय सहायता, मातृत्व एवं पेंशन लाभ।",
            "benefit_description": "₹3,000 त्रैमासिक वित्तीय सहायता एवं पेंशन सुरक्षा",
        },
        "en": {
            "official_name": "Delhi Building & Construction Workers (BOCW)",
            "description": "Financial assistance, pension, and maternity protection for registered construction workers in Delhi.",
            "benefit_description": "₹3,000 quarterly financial assistance",
        }
    },
    "One Nation One Ration Card": {
        "hi": {
            "official_name": "एक देश एक राशन कार्ड (ONORC - PDS)",
            "description": "राष्ट्रीय खाद्य सुरक्षा अधिनियम के तहत पूरे भारत में किसी भी उचित मूल्य की दुकान से राशन पोर्टेबिलिटी।",
            "benefit_description": "देश भर में किसी भी राशन डीलर से रियायती खाद्यान्न",
        },
        "en": {
            "official_name": "One Nation One Ration Card (ONORC)",
            "description": "Nationwide food grain portability under National Food Security Act across all fair price shops.",
            "benefit_description": "Subsidized food grains available at any fair price shop nationwide",
        }
    },
    "UP BOCW": {
        "hi": {
            "official_name": "उत्तर प्रदेश भवन एवं अन्य सन्निर्माण कर्मकार कल्याण बोर्ड",
            "description": "उत्तर प्रदेश में पंजीकृत निर्माण श्रमिकों के लिए कल्याणकारी योजनाएं एवं सहायता।",
            "benefit_description": "चिकित्सा सहायता एवं वार्षिक छात्रवृत्ति",
        },
        "en": {
            "official_name": "Uttar Pradesh BOCW Board",
            "description": "Welfare assistance and medical protection for registered construction workers in UP.",
            "benefit_description": "Medical assistance and annual educational scholarships",
        }
    }
}

REQUIREMENT_TRANSLATIONS = [
    {
        "requirement_name": "Worker Certificate",
        "hi": {"label": "श्रमिक पंजीकरण प्रमाण पत्र (BOCW)", "description": "दिल्ली या संबंधित राज्य का वैध निर्माण श्रमिक कार्ड"},
        "en": {"label": "Worker Certificate", "description": "Valid BOCW registration card"}
    },
    {
        "requirement_name": "Ration Card",
        "hi": {"label": "राशन कार्ड (राष्ट्रीय खाद्य सुरक्षा)", "description": "राज्य सरकार द्वारा जारी वैध डिजिटल या भौतिक राशन कार्ड"},
        "en": {"label": "Ration Card", "description": "State issued valid Ration Card"}
    },
    {
        "requirement_name": "Aadhaar Card",
        "hi": {"label": "आधार कार्ड (पहचान व पता प्रमाण)", "description": "UIDAI द्वारा जारी 12 अंकों का विशिष्ट पहचान पत्र"},
        "en": {"label": "Aadhaar Card", "description": "12-digit UIDAI unique identification card"}
    },
    {
        "requirement_name": "Bank Passbook",
        "hi": {"label": "बैंक पासबुक / DBT खाता विवरण", "description": "आधार से जुड़े बैंक खाते की पासबुक का प्रथम पृष्ठ"},
        "en": {"label": "Bank Passbook", "description": "First page of Aadhaar-linked active bank account"}
    }
]

async def seed_translations():
    async with async_session_maker() as session:
        # 1. Scheme Translations
        schemes_res = await session.execute(select(Scheme))
        schemes = schemes_res.scalars().all()
        for scheme in schemes:
            trans_data = SCHEME_TRANSLATIONS.get(scheme.official_name)
            if trans_data:
                for lang, data in trans_data.items():
                    existing = (await session.execute(
                        select(SchemeTranslation).where(
                            SchemeTranslation.scheme_id == scheme.id,
                            SchemeTranslation.language == lang
                        )
                    )).scalar_one_or_none()

                    if not existing:
                        tr = SchemeTranslation(
                            scheme_id=scheme.id,
                            language=lang,
                            official_name=data["official_name"],
                            description=data["description"],
                            benefit_description=data["benefit_description"],
                            source_language="en",
                            is_authoritative=True,
                        )
                        session.add(tr)
                    else:
                        existing.official_name = data["official_name"]
                        existing.description = data["description"]
                        existing.benefit_description = data["benefit_description"]

        # 2. Requirement Translations
        for req in REQUIREMENT_TRANSLATIONS:
            req_name = req["requirement_name"]
            for lang, data in [("hi", req["hi"]), ("en", req["en"])]:
                existing_req = (await session.execute(
                    select(RequirementTranslation).where(
                        RequirementTranslation.requirement_name == req_name,
                        RequirementTranslation.language == lang
                    )
                )).scalar_one_or_none()

                if not existing_req:
                    rt = RequirementTranslation(
                        requirement_name=req_name,
                        language=lang,
                        label=data["label"],
                        description=data["description"]
                    )
                    session.add(rt)
                else:
                    existing_req.label = data["label"]
                    existing_req.description = data["description"]

        await session.commit()
        print("Successfully seeded scheme and requirement translations!")

if __name__ == "__main__":
    asyncio.run(seed_translations())
