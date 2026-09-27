from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from .benefit import BenefitSummary

class NewOpportunity(BaseModel):
    id: UUID
    scheme_name: str
    category: str
    amount: Optional[float] = None
    why_it_applies: List[str] = []
    matched_rules: List[str] = []
    missing_evidence: List[str] = []
    readiness_percentage: int = 100
    verification_status: Optional[str] = "VERIFIED"

class ActionRequired(BaseModel):
    benefit_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    title: str
    description: str
    action_type: str # RENEWAL, EVIDENCE_REQUIRED, CONSENT_REQUIRED, RECOVERY
    urgency: str # HIGH, MEDIUM, LOW

class RecommendedAction(BaseModel):
    title: str
    description: str

class WelfareStateResponse(BaseModel):
    active_benefits: List[BenefitSummary]
    action_required: List[ActionRequired]
    new_opportunities: List[NewOpportunity]
    at_risk: List[BenefitSummary]
    needs_verification: List[Any] = []
    pending_applications: List[Any] = []
    document_gaps: List[Any] = []
    recommended_actions: List[RecommendedAction] = []
    citizen_summary: Dict[str, Any] = {}
    evidence_readiness_score: int = 80

