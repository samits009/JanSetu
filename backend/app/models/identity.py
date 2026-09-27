from datetime import datetime
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.sql import text as sa_text
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
    mobile_number = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth-only users
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), unique=True, nullable=False, index=True)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("identities.id"), unique=True, nullable=True, index=True)
    preferred_language = Column(String, nullable=False, default="hi")
    is_active = Column(Boolean, nullable=False, default=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    mobile_verified = Column(Boolean, nullable=False, default=False)
    account_status = Column(String, nullable=False, default="ACTIVE")  # 'ACTIVE', 'SUSPENDED', 'DEACTIVATED'
    last_login = Column(DateTime(timezone=True), nullable=True)

    citizen = relationship("Citizen")
    identity = relationship("Identity")
    auth_identities = relationship("AuthIdentity", back_populates="user", cascade="all, delete-orphan")


class AuthIdentity(Base):
    __tablename__ = "auth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "provider_subject", name="uq_auth_identities_provider_subject"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String, nullable=False, default="password")  # 'password', 'google'
    provider_subject = Column(String, nullable=False, index=True)
    provider_email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=sa_text("now()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=sa_text("now()"), onupdate=sa_text("now()"), nullable=False)

    user = relationship("User", back_populates="auth_identities")


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
