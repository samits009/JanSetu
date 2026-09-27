from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, DateTime, Integer
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base, TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False) # 'AADHAAR', 'BOCW_CARD', 'RATION_CARD'
    document_number = Column(String)
    file_url = Column(String)
    extracted_data = Column(JSONB)
    verification_status = Column(String, default="PENDING") # 'PENDING', 'VERIFIED', 'REJECTED'
    storage_reference = Column(String, nullable=True)
    content_hash = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="UPLOADED", index=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    extraction_method = Column(String, nullable=True)
    processing_provider = Column(String, nullable=True)
    processing_model = Column(String, nullable=True)
    prompt_version = Column(String, nullable=True)
    
    citizen = relationship("Citizen", back_populates="documents")
    evidence = relationship("Evidence", back_populates="document")


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    evidence_type = Column(String, nullable=False) # 'IDENTITY', 'INCOME', 'OCCUPATION'
    data = Column(JSONB, nullable=False) # The actual extracted/verified fact
    confidence = Column(String, default="HIGH")
    claim_type = Column(String, nullable=True)
    claim_value = Column(JSONB, nullable=True)
    verification_status = Column(String, nullable=False, default="PENDING")
    provenance = Column(JSONB, nullable=True)
    
    citizen = relationship("Citizen")
    document = relationship("Document", back_populates="evidence")
    requirement_links = relationship("EvidenceRequirementLink", back_populates="evidence")


class EvidenceRequirementLink(Base, TimestampMixin):
    __tablename__ = "evidence_requirement_links"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), nullable=False, index=True)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("application_requirements.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("welfare_applications.id"), nullable=True, index=True) # If linked for a specific app
    
    evidence = relationship("Evidence", back_populates="requirement_links")
    requirement = relationship("ApplicationRequirement", back_populates="evidence_links")
