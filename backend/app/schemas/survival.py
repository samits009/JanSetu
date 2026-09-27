from pydantic import BaseModel
from typing import List, Optional
from .welfare import BenefitSummary, NewOpportunity, ActionRequired

class LocationChangeRequest(BaseModel):
    state: str
    district: str

class SurvivalResponse(BaseModel):
    continued_benefits: List[BenefitSummary]
    changed_benefits: List[BenefitSummary]
    new_benefits: List[NewOpportunity]
    at_risk_benefits: List[BenefitSummary]
    required_actions: List[ActionRequired]
