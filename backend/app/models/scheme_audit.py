from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy import Uuid as UUID, JSON as JSONB
import uuid
from datetime import datetime
from app.db.base import Base, TimestampMixin


class SchemeAuditEvent(Base, TimestampMixin):
    """
    Audit trail specifically for Scheme Intelligence operations.
    Separate from citizen-focused AuditEvent to keep concerns clean.
    """
    __tablename__ = "scheme_audit_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    actor = Column(String, nullable=False)          # e.g. 'mock-admin', 'system'
    action = Column(String, nullable=False)          # e.g. 'SCHEME_VERSION_PUBLISHED'
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"), nullable=True, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("scheme_versions.id"), nullable=True, index=True)
    result = Column(String, nullable=True)           # 'SUCCESS', 'FAILED'
    details = Column(JSONB, nullable=True)           # No secrets ever stored here
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)
