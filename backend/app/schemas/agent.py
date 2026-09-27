from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class ExecutionTraceResponse(BaseModel):
    timestamp: str
    tool: str
    purpose: str
    status: str
    safe_input_summary: Dict[str, Any]
    safe_result_summary: Dict[str, Any]
    duration_ms: int
    consent_state: str

class ChatRequest(BaseModel):
    citizen_id: Optional[UUID] = None
    message: str

class ChatResponse(BaseModel):
    message: str
    actions: List[str]
    requires_consent: bool
    consent_id: Optional[UUID] = None
    consent_action: Optional[str] = None
    consent_application_id: Optional[UUID] = None
    workflow_state: Optional[str] = None
    execution_trace: List[ExecutionTraceResponse]

class ConsentRequestPayload(BaseModel):
    action: str
    application_id: Optional[UUID] = None

class ConsentResponse(BaseModel):
    id: UUID
    action: str
    application_id: Optional[UUID] = None
    purpose: str
    data_accessed: List[str]
    destination: str
    status: str
