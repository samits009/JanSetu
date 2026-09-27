import pytest
from app.services.eligibility import EligibilityService
from app.services.policy_engine import PolicyRuleEngine
from app.models.citizen import Citizen
from app.models.scheme import Scheme, SchemeEligibilityRule, SchemeVersion
import datetime

def test_eligibility_service():
    engine = PolicyRuleEngine()
    service = EligibilityService(engine)
    
    dob = datetime.date.today() - datetime.timedelta(days=20 * 365)
    citizen = Citizen(dob=dob)
    
    scheme = Scheme()
    version = SchemeVersion()
    rule = SchemeEligibilityRule(rule_type="AGE", operator=">=", value=18)
    version.rules = [rule]
    scheme.current_version = version
    
    result = service.evaluate(citizen, scheme)
    assert result["status"] == "eligible"
