from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from app.domain.enums import JurisdictionLevel, SourceType, VerificationStatus, PortabilityState

class ExtractedRule(BaseModel):
    rule_type: str
    operator: str
    value: Any

class ExtractedRequirement(BaseModel):
    name: str
    requirement_type: str
    description: Optional[str] = None

class ExtractedBenefit(BaseModel):
    benefit_type: str
    amount: Optional[float] = None
    description: Optional[str] = None

class ExtractedJurisdiction(BaseModel):
    level: JurisdictionLevel
    country: Optional[str] = "India"
    state: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None

class SchemeExtractionResult(BaseModel):
    official_name: str
    category: str
    description: str
    rules: List[ExtractedRule] = []
    requirements: List[ExtractedRequirement] = []
    benefits: List[ExtractedBenefit] = []
    jurisdictions: List[ExtractedJurisdiction] = []
    
    portability: PortabilityState = PortabilityState.NON_PORTABLE
    renewal_required: bool = False
    renewal_period_days: Optional[int] = None
    
    # Source Provenance (Required by Phase 5A)
    source_type: SourceType = SourceType.FIXTURE
    source_reference: Optional[str] = None
    authority: Optional[str] = None
    retrieved_at: Optional[str] = None
    content_hash: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.UNKNOWN
    
    # Confidence metrics
    confidence_score: float = Field(default=1.0, description="0.0 to 1.0 confidence")
    needs_human_review: bool = False
