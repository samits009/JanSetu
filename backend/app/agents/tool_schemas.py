from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ToolResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    reason: str
    next_action: Optional[str] = None
    requires_consent: bool = False
    workflow_state: Optional[str] = None

class AgentExecutionTrace(BaseModel):
    timestamp: str
    tool: str
    purpose: str
    status: str
    safe_input_summary: Dict[str, Any]
    safe_result_summary: Dict[str, Any]
    duration_ms: int
    consent_state: str
