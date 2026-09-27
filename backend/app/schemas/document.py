from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    document_id: UUID
    status: str
    document_type: str
    uploaded_at: datetime
    duplicate_detected: bool = False

class DocumentClaimResponse(BaseModel):
    field: str
    value: Any
    confidence: str
    source_location: str
    extraction_method: str

class DocumentDetailResponse(BaseModel):
    id: UUID
    document_type: str
    document_number: Optional[str] = None
    status: str
    verification_status: str
    storage_reference: Optional[str] = None
    content_hash: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    extraction_method: Optional[str] = None
    processing_provider: Optional[str] = None
    processing_model: Optional[str] = None
    prompt_version: Optional[str] = None
    extracted_data: Dict[str, Any] = {}
    evidence: List["EvidenceResponse"] = []

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: UUID
    document_type: str
    document_number: Optional[str] = None
    verification_status: str
    extracted_data: Dict[str, Any] = {}
    status: str = "UPLOADED"
    uploaded_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class EvidenceResponse(BaseModel):
    id: UUID
    document_id: UUID
    evidence_type: str
    data: Dict[str, Any]
    confidence: str
    claim_type: Optional[str] = None
    claim_value: Optional[Dict[str, Any]] = None
    verification_status: str = "PENDING"
    provenance: Dict[str, Any] = {}
    
    model_config = ConfigDict(from_attributes=True)
