from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base, TimestampMixin
from app.domain.enums import ConsentAction

class Consent(Base, TimestampMixin):
    __tablename__ = "consents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("welfare_applications.id"), nullable=True, index=True)
    action = Column(SQLEnum(ConsentAction, name="consent_action_enum"), nullable=False)
    is_granted = Column(Boolean, nullable=False, default=False)
    purpose = Column(String, nullable=False)
    ip_address = Column(String)
    
    citizen = relationship("Citizen")
    application = relationship("WelfareApplication")


class AgentAction(Base, TimestampMixin):
    __tablename__ = "agent_actions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("welfare_applications.id"), nullable=True, index=True)
    action_type = Column(String, nullable=False) # 'PREPARED_RECOVERY', 'EXTRACTED_EVIDENCE'
    details = Column(JSONB)
    status = Column(String) # 'SUCCESS', 'FAILED'
    
    citizen = relationship("Citizen")
    application = relationship("WelfareApplication")


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    actor = Column(String, nullable=False) # 'AGENT', 'CITIZEN', 'SYSTEM'
    action = Column(String, nullable=False)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("welfare_applications.id"), nullable=True, index=True)
    consent_id = Column(UUID(as_uuid=True), ForeignKey("consents.id"), nullable=True)
    data_used = Column(JSONB)
    result = Column(String)
    
    citizen = relationship("Citizen")
    application = relationship("WelfareApplication")
    consent = relationship("Consent")
