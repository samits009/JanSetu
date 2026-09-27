from typing import List, Dict, Any, Optional
import datetime
from app.models.scheme import SchemeEligibilityRule
from app.models.citizen import Citizen, Household, Employment, Location

class PolicyRuleEngine:
    def __init__(self):
        # We only support deterministic python native operators
        self.supported_operators = ['==', '!=', '>', '>=', '<', '<=', 'in', 'not_in']
        self.supported_types = ['AGE', 'INCOME', 'OCCUPATION', 'STATE', 'DISTRICT', 'RESIDENCY', 'HOUSEHOLD_SIZE', 'EMPLOYMENT_DURATION', 'DEPENDENT_STATUS', 'DOCUMENT_EXISTS']

    def evaluate_rule(self, rule: SchemeEligibilityRule, citizen: Citizen) -> str:
        """
        Evaluates a single rule against a citizen's facts.
        Returns "TRUE", "FALSE", or "UNKNOWN"
        """
        rule_type = rule.rule_type
        operator = rule.operator
        value = rule.value

        try:
            if rule_type == 'AGE':
                if citizen.dob is None:
                    return "UNKNOWN"
                # Calculate age
                today = datetime.date.today()
                age = today.year - citizen.dob.year - ((today.month, today.day) < (citizen.dob.month, citizen.dob.day))
                return self._compare(age, operator, int(value))

            elif rule_type == 'INCOME':
                # Household income
                if not citizen.households:
                    return "UNKNOWN"
                household = citizen.households[0].household
                if household.annual_income is None:
                    return "UNKNOWN"
                return self._compare(household.annual_income, operator, float(value))

            elif rule_type == 'OCCUPATION':
                if not citizen.employments:
                    return "UNKNOWN"
                # Check current employment
                current_employments = [e for e in citizen.employments if e.is_current]
                if not current_employments:
                    return "UNKNOWN"
                # For simplicity, just check the first current employment
                return self._compare(current_employments[0].occupation, operator, value)

            elif rule_type == 'STATE':
                if not citizen.locations:
                    return "UNKNOWN"
                current_locations = [loc for loc in citizen.locations if loc.is_active and loc.location_type == 'CURRENT']
                if not current_locations:
                    return "UNKNOWN"
                return self._compare(current_locations[0].state, operator, value)

            elif rule_type == 'DISTRICT':
                if not citizen.locations:
                    return "UNKNOWN"
                current_locations = [loc for loc in citizen.locations if loc.is_active and loc.location_type == 'CURRENT']
                if not current_locations:
                    return "UNKNOWN"
                return self._compare(current_locations[0].district, operator, value)

            elif rule_type == 'HOUSEHOLD_SIZE':
                if not citizen.households:
                    return "UNKNOWN"
                household = citizen.households[0].household
                # the list of members
                size = len(household.members) if household.members else 0
                if size == 0:
                    return "UNKNOWN"
                return self._compare(size, operator, int(value))
                
            elif rule_type == 'EMPLOYMENT_DURATION':
                 # calculate duration in days of current employment
                if not citizen.employments:
                    return "UNKNOWN"
                current_employments = [e for e in citizen.employments if e.is_current]
                if not current_employments or not current_employments[0].start_date:
                    return "UNKNOWN"
                today = datetime.date.today()
                duration = (today - current_employments[0].start_date).days
                return self._compare(duration, operator, int(value))

        except Exception:
            return "UNKNOWN"
            
        return "UNKNOWN"

    def _compare(self, actual: Any, operator: str, expected: Any) -> str:
        if operator == '==':
            return "TRUE" if actual == expected else "FALSE"
        elif operator == '!=':
            return "TRUE" if actual != expected else "FALSE"
        elif operator == '>':
            return "TRUE" if actual > expected else "FALSE"
        elif operator == '>=':
            return "TRUE" if actual >= expected else "FALSE"
        elif operator == '<':
            return "TRUE" if actual < expected else "FALSE"
        elif operator == '<=':
            return "TRUE" if actual <= expected else "FALSE"
        elif operator == 'in':
            return "TRUE" if actual in expected else "FALSE"
        elif operator == 'not_in':
            return "TRUE" if actual not in expected else "FALSE"
        return "UNKNOWN"
