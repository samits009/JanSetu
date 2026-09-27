from datetime import datetime
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Identity(Base, TimestampMixin):
    __tablename__ = "identities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    role = Column(String, nullable=False, default="CITIZEN")
    verification_state = Column(String, nullable=False, default="UNVERIFIED")
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=True, unique=True, index=True)
    active = Column(Boolean, nullable=False, default=True)
    citizen = relationship("Citizen")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), unique=True, nullable=False, index=True)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"), unique=True, nullable=True, index=True)
    preferred_language = Column(String, nullable=False, default="hi")
    is_active = Column(Boolean, nullable=False, default=True)
    account_status = Column(String, nullable=False, default="ACTIVE")  # 'ACTIVE', 'SUSPENDED', 'DEACTIVATED'
    last_login = Column(DateTime(timezone=True), nullable=True)

    citizen = relationship("Citizen")
    identity = relationship("Identity")


class AuthSession(Base, TimestampMixin):
    __tablename__ = "auth_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    identity = relationship("Identity")
    user = relationship("User")
