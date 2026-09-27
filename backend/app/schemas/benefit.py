from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID

class RequirementEvaluation(BaseModel):
    id: str
    name: str
    type: str
    is_satisfied: bool
    linked_evidence_id: Optional[UUID] = None
    reason: Optional[str] = None
    
class EvidenceDetail(BaseModel):
    id: UUID
    type: str
    document_type: str
    confidence: str
    
class BenefitSummary(BaseModel):
    id: UUID
    scheme_id: UUID
    scheme_name: str
    status: str
    amount: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class BenefitResponse(BaseModel):
    benefits: List[BenefitSummary]
    
class BenefitDetailResponse(BaseModel):
    id: UUID
    scheme_id: UUID
    scheme_name: str
    status: str
    eligibility_status: str # ELIGIBLE, INELIGIBLE, UNKNOWN
    satisfied_requirements: List[RequirementEvaluation]
    missing_requirements: List[RequirementEvaluation]
    supporting_evidence: List[EvidenceDetail]
    reasons: List[str]
    application_status: Optional[str] = None
    application_id: Optional[UUID] = None
