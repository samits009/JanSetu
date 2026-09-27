from __future__ import annotations
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.domain.enums import (
    SchemeCategory, VerificationStatus, SourceType, JurisdictionLevel, PortabilityState
)


# ─── Source ────────────────────────────────────────────────────────────────────

class SchemeSourceResponse(BaseModel):
    id: UUID
    authority: str
    source_type: SourceType
    source_reference: Optional[str] = None
    source_url: Optional[str] = None  # Only non-internal, public URLs
    jurisdiction: Optional[JurisdictionLevel] = None
    active: bool
    last_checked: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Eligibility Rules ─────────────────────────────────────────────────────────

class SchemeRuleResponse(BaseModel):
    id: UUID
    rule_type: str
    operator: str
    value: Any
    is_mandatory: bool
    raw_policy_text: Optional[str] = None
    source_reference: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Requirements ──────────────────────────────────────────────────────────────

class SchemeRequirementResponse(BaseModel):
    """A requirement definition from the SchemeVersion snapshot."""
    name: str
    requirement_type: str = Field(alias="type", default="DOCUMENT")
    description: Optional[str] = None
    is_mandatory: Optional[bool] = True

    model_config = {"from_attributes": True, "populate_by_name": True}


# ─── Benefits ─────────────────────────────────────────────────────────────────

class SchemeBenefitResponse(BaseModel):
    id: UUID
    benefit_type: str
    amount: Optional[int] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Version ──────────────────────────────────────────────────────────────────

class SchemeVersionResponse(BaseModel):
    id: UUID
    scheme_id: UUID
    version_number: int
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    verification_status: VerificationStatus
    content_hash: Optional[str] = None
    published_at: Optional[datetime] = None
    source_id: Optional[UUID] = None
    source: Optional[SchemeSourceResponse] = None
    rules: List[SchemeRuleResponse] = Field(default_factory=list)
    requirements: List[SchemeRequirementResponse] = Field(default_factory=list)
    benefits: List[SchemeBenefitResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Scheme Summary (list view) ────────────────────────────────────────────────

class SchemeSummaryResponse(BaseModel):
    id: UUID
    official_name: str
    category: SchemeCategory
    level: Optional[str] = None
    state: Optional[str] = None
    description: Optional[str] = None
    current_version_id: Optional[UUID] = None
    verification_status: Optional[VerificationStatus] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Scheme Detail ─────────────────────────────────────────────────────────────

class SchemeDetailResponse(BaseModel):
    id: UUID
    official_name: str
    authority: Optional[str] = None
    category: SchemeCategory
    level: Optional[str] = None
    state: Optional[str] = None
    description: Optional[str] = None
    current_version_id: Optional[UUID] = None
    current_version: Optional[SchemeVersionResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Paginated list ────────────────────────────────────────────────────────────

class PaginatedSchemeResponse(BaseModel):
    items: List[SchemeSummaryResponse]
    page: int
    page_size: int
    total: int
    has_next: bool


# ─── Refresh ──────────────────────────────────────────────────────────────────

class SchemeRefreshResponse(BaseModel):
    scheme_id: UUID
    material_change: bool
    candidate_version_id: Optional[UUID] = None
    candidate_version_number: Optional[int] = None
    verification_status: Optional[VerificationStatus] = None
    message: str


# ─── Review ───────────────────────────────────────────────────────────────────

class SchemeReviewResponse(BaseModel):
    version_id: UUID
    verification_status: VerificationStatus
    message: str


# ─── Version Comparison ───────────────────────────────────────────────────────

class VersionFieldChange(BaseModel):
    field: str
    old_value: Any
    new_value: Any
    category: str  # e.g. 'RULE', 'REQUIREMENT', 'BENEFIT', 'PORTABILITY', 'RENEWAL'


class SchemeVersionComparisonResponse(BaseModel):
    version_a_id: UUID
    version_b_id: UUID
    material_change: bool
    changes: List[VersionFieldChange]
