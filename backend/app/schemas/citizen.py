from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from uuid import UUID

class LocationResponse(BaseModel):
    state: str
    district: str
    is_active: bool
    location_type: str
    
    model_config = ConfigDict(from_attributes=True)

class EmploymentResponse(BaseModel):
    occupation: str
    is_active: bool
    employer_name: Optional[str] = None
    employment_status: Optional[str] = None
    annual_income: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class CitizenProfile(BaseModel):
    id: UUID
    name: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    onboarding_completed: Optional[bool] = False
    onboarding_step: Optional[int] = 1
    locations: List[LocationResponse]
    employments: List[EmploymentResponse]
    
    model_config = ConfigDict(from_attributes=True)

class CitizenResponse(BaseModel):
    profile: CitizenProfile


class OnboardingRequest(BaseModel):
    name: Optional[str] = None
    # Accept both 'dob' and 'date_of_birth' from frontend
    dob: Optional[date] = Field(None, alias="dob")
    date_of_birth: Optional[date] = Field(None)
    gender: Optional[str] = None
    phone: Optional[str] = None
    
    current_state: str
    current_district: str
    permanent_state: Optional[str] = None
    permanent_district: Optional[str] = None
    
    occupation: str
    employment_status: Optional[str] = "EMPLOYED"
    annual_income: Optional[int] = 0
    employer_name: Optional[str] = None

    # Accept both 'household_members_count' and 'household_members' from frontend
    household_members_count: Optional[int] = Field(None)
    household_members: Optional[int] = Field(None)
    has_spouse: Optional[bool] = False
    children_count: Optional[int] = Field(None)
    dependents: Optional[int] = Field(None)  # frontend alias for children_count

    model_config = ConfigDict(populate_by_name=True)

    def model_post_init(self, __context) -> None:
        # Resolve aliases: prefer explicit field, fall back to alias
        if self.dob is None and self.date_of_birth is not None:
            self.dob = self.date_of_birth
        if self.household_members_count is None and self.household_members is not None:
            self.household_members_count = self.household_members
        if self.children_count is None and self.dependents is not None:
            self.children_count = self.dependents


class OnboardingStepRequest(BaseModel):
    step: int = Field(..., ge=1, le=4)
    # Step 1: Personal
    name: Optional[str] = None
    dob: Optional[date] = Field(None, alias="dob")
    date_of_birth: Optional[date] = Field(None)
    gender: Optional[str] = None
    phone: Optional[str] = None

    # Step 2: Location
    current_state: Optional[str] = None
    current_district: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_district: Optional[str] = None

    # Step 3: Employment
    occupation: Optional[str] = None
    employment_status: Optional[str] = None
    annual_income: Optional[int] = None
    employer_name: Optional[str] = None

    # Step 4: Household
    household_members_count: Optional[int] = Field(None)
    household_members: Optional[int] = Field(None)
    has_spouse: Optional[bool] = False
    children_count: Optional[int] = Field(None)
    dependents: Optional[int] = Field(None)

    model_config = ConfigDict(populate_by_name=True)

    def model_post_init(self, __context) -> None:
        if self.dob is None and self.date_of_birth is not None:
            self.dob = self.date_of_birth
        if self.household_members_count is None and self.household_members is not None:
            self.household_members_count = self.household_members
        if self.children_count is None and self.dependents is not None:
            self.children_count = self.dependents



