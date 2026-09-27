from typing import Any, List, Optional
from pydantic import BaseModel, Field


class DocumentClaim(BaseModel):
    field: str = Field(min_length=1)
    value: Any
    confidence: str
    source_location: str
    extraction_method: str
    source_reference: Optional[str] = None


class DocumentExtraction(BaseModel):
    claims: List[DocumentClaim]
    extraction_method: str
    provider: str = "MOCK"
    model: str = ""
    prompt_version: str = "v1"


class GeminiExtractionSchema(BaseModel):
    """Pydantic schema for structured Gemini document extraction output."""
    document_type: str = Field(description="The type of document (e.g., AADHAAR, BOCW_CARD)")
    claims: List[DocumentClaim] = Field(description="List of extracted claims with confidence")
