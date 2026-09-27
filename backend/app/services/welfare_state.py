from typing import Dict, Any, Optional
from app.repositories.citizen import CitizenRepository
from app.services.scheme_registry import SchemeRegistryService
from app.services.eligibility import EligibilityService

class WelfareStateService:
    def __init__(self, citizen_repo: CitizenRepository, scheme_registry: SchemeRegistryService, eligibility_service: EligibilityService):
        self.citizen_repo = citizen_repo
        self.scheme_registry = scheme_registry
        self.eligibility_service = eligibility_service

    async def evaluate(self, citizen_id: Any, language: Optional[str] = None) -> Dict[str, Any]:
        citizen = await self.citizen_repo.get_full_welfare_context(citizen_id)
        if not citizen:
            raise ValueError("Citizen not found")

        state = {
            "citizen_summary": {"name": citizen.name, "id": str(citizen.id)},
            "active_benefits": [],
            "action_required": [],
            "new_opportunities": [],
            "at_risk": [],
            "needs_verification": [],
            "pending_applications": [],
            "document_gaps": [],
            "recommended_actions": []
        }

        # Existing benefits
        for benefit in citizen.benefits:
            if benefit.risks:
                state["at_risk"].append(benefit)
            elif benefit.status == "ACTIVE":
                state["active_benefits"].append(benefit)

        # Applications
        for app in citizen.applications:
            if app.status in ["UNDER_REVIEW", "SUBMITTED", "AWAITING_CONSENT", "DRAFTED"]:
                state["pending_applications"].append(app)
            elif app.status in ["REQUIRES_EVIDENCE", "REJECTED"]:
                state["action_required"].append(app)

        # Opportunities
        # Get all verified schemes, evaluate eligibility
        all_schemes = await self.scheme_registry.list_verified_schemes()
        
        # Don't check schemes they already applied for or have benefits for
        existing_scheme_ids = {b.scheme_id for b in citizen.benefits} | {a.scheme_id for a in citizen.applications}

        for scheme in all_schemes:
            if scheme.id in existing_scheme_ids:
                continue

            eval_result = self.eligibility_service.evaluate(citizen, scheme)
            if eval_result["status"] == "eligible":
                matched_rules = []
                why_it_applies = []
                if scheme.current_version and scheme.current_version.rules:
                    for r in scheme.current_version.rules:
                        matched_rules.append(f"{r.rule_type}: {r.operator} {r.value}")
                        if language == "hi":
                            if r.rule_type == "OCCUPATION":
                                why_it_applies.append(f"सत्यापित व्यवसाय ({r.value}) के आधार पर निर्माण श्रमिक पात्रता सिद्ध होती है")
                            elif r.rule_type == "STATE":
                                why_it_applies.append(f"वर्तमान निवास राज्य ({r.value}) के अंतर्गत योजना सीधे लागू होती है")
                            elif r.rule_type == "INCOME":
                                why_it_applies.append(f"पारिवारिक आय सीमा (<= ₹{r.value}) के भीतर होने से पूर्ण पात्रता प्राप्त है")
                            elif r.rule_type == "AGE":
                                why_it_applies.append(f"आयु सीमा मानदंड ({r.operator} {r.value} वर्ष) पूर्ण है")
                        else:
                            if r.rule_type == "OCCUPATION":
                                why_it_applies.append(f"Matched active occupation as {r.value}")
                            elif r.rule_type == "STATE":
                                why_it_applies.append(f"Eligible in your current residence state ({r.value})")
                            elif r.rule_type == "INCOME":
                                why_it_applies.append(f"Income within the entitled threshold (<= ₹{r.value})")
                            elif r.rule_type == "AGE":
                                why_it_applies.append(f"Meets eligible age criteria ({r.operator} {r.value} yrs)")

                if not why_it_applies:
                    why_it_applies = (
                        ["नागरिक प्रोफ़ाइल द्वारा योजना के सभी अनिवार्य पात्रता मानदंड पूर्ण रूप से सत्यापित हैं"]
                        if language == "hi" else
                        ["All mandatory scheme eligibility criteria fully satisfied by citizen profile"]
                    )

                state["new_opportunities"].append({
                    "scheme": scheme,
                    "confidence": eval_result["confidence"],
                    "matched_rules": matched_rules,
                    "why_it_applies": why_it_applies
                })
            elif eval_result["status"] == "unknown":
                state["needs_verification"].append({
                    "scheme": scheme,
                    "missing_data": eval_result["missing_data"]
                })
                # Add to document gaps
                for missing in eval_result["missing_data"]:
                    state["document_gaps"].append(missing)

        return state

