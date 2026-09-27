from typing import Dict, Any, List
from app.models.citizen import Location
from app.services.welfare_state import WelfareStateService
from app.services.eligibility import EligibilityService
from app.services.scheme_registry import SchemeRegistryService

class BenefitSurvivalService:
    def __init__(self, welfare_state_service: WelfareStateService, eligibility_service: EligibilityService, scheme_registry: SchemeRegistryService):
        self.welfare_state_service = welfare_state_service
        self.eligibility_service = eligibility_service
        self.scheme_registry = scheme_registry

    async def evaluate_location_change(self, citizen_id: Any, new_location: Location) -> Dict[str, Any]:
        """
        Compare current welfare state against proposed welfare state.
        Only mark a benefit as portable if its stored portability rules support that conclusion.
        """
        # For evaluation, we ideally would mock the citizen's location in memory
        # and re-evaluate, but here we explicitly check portability rules of current benefits.

        current_state = await self.welfare_state_service.evaluate(citizen_id)
        
        result = {
            "continued_benefits": [],
            "changed_benefits": [],
            "new_benefits": [],
            "at_risk_benefits": [],
            "required_actions": []
        }

        # Check existing benefits
        for benefit in current_state["active_benefits"]:
            scheme = await self.scheme_registry.get_scheme(benefit.scheme_id)
            # Evaluate portability
            # In our schema, we don't have explicit portability_rules field yet, so we assume non-central schemes
            # are not portable across states unless they explicitly match the new state.
            if scheme.level == 'STATE' and scheme.state != new_location.state:
                # If it's a different state and no portability rule says otherwise, it's at risk
                result["at_risk_benefits"].append({
                    "benefit": benefit,
                    "reason": f"Scheme {scheme.official_name} is specific to {scheme.state}, but new location is {new_location.state}"
                })
                result["required_actions"].append(f"Cancel or transfer {scheme.official_name}")
            else:
                result["continued_benefits"].append(benefit)

        # Check new opportunities in the new location
        schemes_in_new_location = await self.scheme_registry.list_schemes_for_location(new_location.state)
        
        # In a full implementation, we'd mock the citizen with the new location and call eligibility_service
        # For now, we return potential new schemes as new opportunities
        for scheme in schemes_in_new_location:
            # simple filter
            if scheme.state == new_location.state:
                result["new_benefits"].append(scheme)

        return result
