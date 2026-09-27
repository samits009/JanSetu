from typing import Dict, Any, List
from app.models.citizen import Citizen
from app.models.scheme import Scheme
from app.services.policy_engine import PolicyRuleEngine

class EligibilityService:
    def __init__(self, policy_engine: PolicyRuleEngine):
        self.policy_engine = policy_engine

    def evaluate(self, citizen: Citizen, scheme: Scheme) -> Dict[str, Any]:
        """
        Evaluates a citizen's eligibility for a given scheme based on rules.
        """
        result = {
            "status": "unknown",
            "confidence": "high",
            "failed_rules": [],
            "missing_data": []
        }

        if not scheme.current_version or not scheme.current_version.rules:
            # If no rules exist, we can't determine eligibility
            return result

        any_failed = False
        any_unknown = False

        for rule in scheme.current_version.rules:
            eval_result = self.policy_engine.evaluate_rule(rule, citizen)
            if eval_result == "FALSE":
                any_failed = True
                result["failed_rules"].append({
                    "rule_id": str(rule.id),
                    "rule_type": rule.rule_type,
                    "reason": f"Failed {rule.rule_type} check: expected {rule.operator} {rule.value}"
                })
            elif eval_result == "UNKNOWN":
                any_unknown = True
                result["missing_data"].append({
                    "rule_id": str(rule.id),
                    "rule_type": rule.rule_type,
                    "reason": f"Missing data for {rule.rule_type}"
                })

        if any_failed:
            result["status"] = "not_eligible"
        elif any_unknown:
            result["status"] = "unknown"
            result["confidence"] = "low"
        else:
            result["status"] = "eligible"

        return result
