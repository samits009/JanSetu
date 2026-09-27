from sqlalchemy import Column, String, Integer, ForeignKey, Date, Boolean, DateTime
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base, TimestampMixin


class Citizen(Base, TimestampMixin):
    __tablename__ = "citizens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True)
    dob = Column(Date, nullable=True)
    gender = Column(String, nullable=True)  # 'male', 'female', 'other'

    # Onboarding progress tracking
    onboarding_completed = Column(Boolean, nullable=False, default=False)
    onboarding_step = Column(Integer, nullable=False, default=1)  # 1-4, last completed step

    # Relationships
    households = relationship("HouseholdMember", back_populates="citizen")
    employments = relationship("Employment", back_populates="citizen")
    locations = relationship("Location", back_populates="citizen")
    documents = relationship("Document", back_populates="citizen")
    applications = relationship("WelfareApplication", back_populates="citizen")
    benefits = relationship("Benefit", back_populates="citizen")


class Household(Base, TimestampMixin):
    __tablename__ = "households"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    head_citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"))
    annual_income = Column(Integer, default=0)
    member_count = Column(Integer, nullable=False, default=1)
    dependents_count = Column(Integer, nullable=False, default=0)
    children_count = Column(Integer, nullable=False, default=0)

    members = relationship("HouseholdMember", back_populates="household")


class HouseholdMember(Base, TimestampMixin):
    __tablename__ = "household_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False)
    relationship_to_head = Column(String)

    household = relationship("Household", back_populates="members")
    citizen = relationship("Citizen", back_populates="households")


class Employment(Base, TimestampMixin):
    __tablename__ = "employments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    occupation = Column(String, nullable=False)
    employment_status = Column(String, nullable=True)  # 'informal_labor', 'salaried', 'self_employed', 'agricultural', 'unemployed'
    employer_name = Column(String)
    annual_income = Column(Integer, nullable=True)
    is_current = Column(Boolean, default=True)
    start_date = Column(Date)
    end_date = Column(Date)

    citizen = relationship("Citizen", back_populates="employments")

    @property
    def is_active(self) -> bool:
        return self.is_current


class Location(Base, TimestampMixin):
    __tablename__ = "locations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("citizens.id"), nullable=False, index=True)
    location_type = Column(String)  # 'HOME', 'CURRENT'
    address_line_1 = Column(String)
    district = Column(String)
    state = Column(String)
    pincode = Column(String)
    is_active = Column(Boolean, default=True)

    citizen = relationship("Citizen", back_populates="locations")

