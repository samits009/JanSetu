from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, Integer, Date, Boolean
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base, TimestampMixin
from app.domain.enums import ApplicationStatus, BenefitStatus

class Benefit(Base, TimestampMixin):
    __tablename__ = "benefits"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"), nullable=False, index=True)
    scheme_version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=True, index=True)
    status = Column(SQLEnum(BenefitStatus, name="benefit_status_enum"), nullable=False)
    next_renewal_date = Column(Date, nullable=True)
    
    citizen = relationship("Citizen", back_populates="benefits")
    scheme = relationship("Scheme")
    scheme_version = relationship("SchemeVersion")
    risks = relationship("BenefitRisk", back_populates="benefit")


class BenefitRisk(Base, TimestampMixin):
    __tablename__ = "benefit_risks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    benefit_id = Column(UUID(as_uuid=True), ForeignKey("benefits.id"), nullable=False, index=True)
    risk_type = Column(String, nullable=False) # 'LOCATION_CHANGE', 'INCOME_CHANGE'
    description = Column(String)
    is_resolved = Column(Boolean, default=False)
    
    benefit = relationship("Benefit", back_populates="risks")


class WelfareApplication(Base, TimestampMixin):
    __tablename__ = "welfare_applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"), nullable=False, index=True)
    scheme_version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=True, index=True)
    status = Column(SQLEnum(ApplicationStatus, name="application_status_enum"), default=ApplicationStatus.DISCOVERED, nullable=False, index=True)
    
    # Snapshot of eligibility/evidence state at time of submission
    snapshot = Column(JSONB, nullable=True) 
    
    # Fields for rejection recovery
    rejection_reason = Column(String, nullable=True)
    government_reference_id = Column(String, nullable=True)
    
    citizen = relationship("Citizen", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")
    scheme_version = relationship("SchemeVersion", back_populates="applications")
    requirements = relationship("ApplicationRequirement", back_populates="application")
    # Applications will also have backrefs from EvidenceRequirementLink, Consent, AgentAction

class ApplicationRequirement(Base, TimestampMixin):
    __tablename__ = "application_requirements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("welfare_applications.id"), nullable=False, index=True)
    requirement_type = Column(String, nullable=False) # 'IDENTITY_PROOF', 'INCOME_PROOF', 'OCCUPATION_PROOF'
    description = Column(String)
    is_mandatory = Column(Boolean, default=True)
    
    application = relationship("WelfareApplication", back_populates="requirements")
    evidence_links = relationship("EvidenceRequirementLink", back_populates="requirement")
