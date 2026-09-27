from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from .document import EvidenceResponse

class ApplicationRequirementResponse(BaseModel):
    id: UUID
    requirement_type: str
    description: str
    is_mandatory: bool
    
    model_config = ConfigDict(from_attributes=True)

class ApplicationCreateRequest(BaseModel):
    citizen_id: Optional[UUID] = None
    scheme_id: UUID

class ApplicationResponse(BaseModel):
    id: UUID
    scheme_id: UUID
    scheme_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TimelineEntry(BaseModel):
    status: str
    timestamp: datetime

class ApplicationDetailResponse(BaseModel):
    id: UUID
    scheme_id: UUID
    scheme_name: str
    status: str
    requirements: List[ApplicationRequirementResponse]
    rejection_reason: Optional[str] = None
    government_reference_id: Optional[str] = None
    timeline: List[TimelineEntry] = []

class RecoveryPlanResponse(BaseModel):
    application_id: UUID
    original_rejection_reason: str
    missing_requirements: List[ApplicationRequirementResponse]
    suggested_evidence: List[EvidenceResponse]
    can_recover: bool
