from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum as SQLEnum, DateTime, Date
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base, TimestampMixin
from app.domain.enums import (
    SchemeCategory, 
    VerificationStatus, 
    SourceType, 
    JurisdictionLevel,
    PortabilityState
)

class SchemeSource(Base, TimestampMixin):
    __tablename__ = "scheme_sources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    authority = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    source_type = Column(SQLEnum(SourceType, name="source_type_enum"), nullable=False)
    jurisdiction = Column(SQLEnum(JurisdictionLevel, name="jurisdiction_level_enum"), nullable=True)
    crawl_frequency = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    
    versions = relationship("SchemeVersion", back_populates="source")

class Scheme(Base, TimestampMixin):
    __tablename__ = "schemes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    official_name = Column(String, nullable=False, unique=True)
    authority = Column(String)
    level = Column(String) # 'CENTRAL', 'STATE'
    state = Column(String, nullable=True) # If state level
    category = Column(SQLEnum(SchemeCategory, name="scheme_category_enum"), nullable=False)
    description = Column(String)
    benefit_amount = Column(Integer, nullable=True)
    benefit_description = Column(String)
    
    # We leave these here for backward-compat/metadata, but versions hold the truth
    official_source = Column(String)
    requirement_definitions = Column(JSONB, nullable=True) 
    
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id", use_alter=True, name="fk_scheme_current_version"), nullable=True)
    
    versions = relationship("SchemeVersion", back_populates="scheme", foreign_keys="[SchemeVersion.scheme_id]")
    current_version = relationship("SchemeVersion", foreign_keys=[current_version_id], post_update=True)
    applications = relationship("WelfareApplication", back_populates="scheme")
    translations = relationship("SchemeTranslation", back_populates="scheme", cascade="all, delete-orphan")

class SchemeVersion(Base, TimestampMixin):
    __tablename__ = "scheme_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("scheme_sources.id"), nullable=True)
    verification_status = Column(SQLEnum(VerificationStatus, name="verification_status_enum"), default=VerificationStatus.UNKNOWN, nullable=False)
    content_hash = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # The actual rule snapshot for this version
    requirement_definitions = Column(JSONB, nullable=True) 
    
    scheme = relationship("Scheme", back_populates="versions", foreign_keys=[scheme_id])
    source = relationship("SchemeSource", back_populates="versions")
    rules = relationship("SchemeEligibilityRule", back_populates="version", cascade="all, delete-orphan")
    benefits = relationship("SchemeBenefit", back_populates="version", cascade="all, delete-orphan")
    jurisdictions = relationship("SchemeJurisdiction", back_populates="version", cascade="all, delete-orphan")
    portability_rules = relationship("SchemePortabilityRule", back_populates="version", cascade="all, delete-orphan")
    renewal_rules = relationship("SchemeRenewalRule", back_populates="version", cascade="all, delete-orphan")
    applications = relationship("WelfareApplication", back_populates="scheme_version")


class SchemeEligibilityRule(Base, TimestampMixin):
    __tablename__ = "scheme_eligibility_rules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=False, index=True)
    
    # Keeping old scheme_id for backward compat in queries until fully migrated, though version_id is primary
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"), nullable=False, index=True)
    
    rule_type = Column(String, nullable=False) # 'AGE', 'INCOME', 'OCCUPATION', 'LOCATION'
    operator = Column(String, nullable=False) # 'GREATER_THAN', 'EQUALS', 'IN'
    value = Column(JSONB, nullable=False) # Can hold array or scalar
    is_mandatory = Column(Boolean, default=True)
    
    raw_policy_text = Column(String, nullable=True)
    source_reference = Column(String, nullable=True)
    
    version = relationship("SchemeVersion", back_populates="rules")
    scheme = relationship("Scheme", viewonly=True)


class SchemeBenefit(Base, TimestampMixin):
    __tablename__ = "scheme_benefits"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=False, index=True)
    benefit_type = Column(String, nullable=False) # e.g. 'CASH', 'IN_KIND', 'INSURANCE'
    amount = Column(Integer, nullable=True)
    description = Column(String)
    
    version = relationship("SchemeVersion", back_populates="benefits")


class SchemeJurisdiction(Base, TimestampMixin):
    __tablename__ = "scheme_jurisdictions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=False, index=True)
    level = Column(SQLEnum(JurisdictionLevel, name="jurisdiction_level_enum"), nullable=False)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    local_body = Column(String, nullable=True)
    
    version = relationship("SchemeVersion", back_populates="jurisdictions")


class SchemePortabilityRule(Base, TimestampMixin):
    __tablename__ = "scheme_portability_rules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=False, index=True)
    portability_state = Column(SQLEnum(PortabilityState, name="portability_state_enum"), nullable=False)
    conditions = Column(String, nullable=True)
    
    version = relationship("SchemeVersion", back_populates="portability_rules")


class SchemeRenewalRule(Base, TimestampMixin):
    __tablename__ = "scheme_renewal_rules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=False, index=True)
    renewal_required = Column(Boolean, default=False)
    renewal_period_days = Column(Integer, nullable=True)
    grace_period_days = Column(Integer, nullable=True)
    deadline_rule = Column(String, nullable=True)
    required_evidence = Column(JSONB, nullable=True)
    
    version = relationship("SchemeVersion", back_populates="renewal_rules")


class SchemeTranslation(Base, TimestampMixin):
    __tablename__ = "scheme_translations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False, index=True)  # 'en', 'hi'
    official_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    benefit_description = Column(String, nullable=True)
    source_language = Column(String(10), default="en", nullable=False)
    is_authoritative = Column(Boolean, default=True, nullable=False)

    scheme = relationship("Scheme", back_populates="translations")


class RequirementTranslation(Base, TimestampMixin):
    __tablename__ = "requirement_translations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    requirement_name = Column(String, nullable=False, index=True)  # e.g. 'Worker Certificate', 'Ration Card'
    language = Column(String(10), nullable=False, index=True)  # 'en', 'hi'
    label = Column(String, nullable=False)
    description = Column(String, nullable=True)

