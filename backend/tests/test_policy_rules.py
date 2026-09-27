import pytest
from app.services.policy_engine import PolicyRuleEngine
from app.models.citizen import Citizen, Household, HouseholdMember
from app.models.scheme import SchemeEligibilityRule
import datetime

def test_policy_engine_age():
    engine = PolicyRuleEngine()
    dob = datetime.date.today() - datetime.timedelta(days=20 * 365)
    citizen = Citizen(dob=dob)
    
    rule = SchemeEligibilityRule(rule_type="AGE", operator=">=", value=18)
    assert engine.evaluate_rule(rule, citizen) == "TRUE"
    
    rule_fail = SchemeEligibilityRule(rule_type="AGE", operator="<", value=18)
    assert engine.evaluate_rule(rule_fail, citizen) == "FALSE"
    
    citizen_unknown = Citizen(dob=None)
    assert engine.evaluate_rule(rule, citizen_unknown) == "UNKNOWN"
