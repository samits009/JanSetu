from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: Optional[str] = Field(None, max_length=120)
    mobile_number: Optional[str] = Field(None, min_length=10, max_length=20)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: Optional[str] = Field(None, min_length=8, max_length=128)
    preferred_language: str = Field("hi", max_length=10)

    def get_mobile(self) -> Optional[str]:
        return self.mobile_number or self.phone

    @field_validator("confirm_password")
    @classmethod
    def check_passwords_match(cls, v, info):
        if v is not None and "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=120)
    email: Optional[str] = Field(None, min_length=3, max_length=120)
    mobile_number: Optional[str] = Field(None, min_length=3, max_length=120)
    phone: Optional[str] = Field(None, min_length=3, max_length=120)
    password: str = Field(..., min_length=1, max_length=128)

    def get_identifier(self) -> str:
        return self.username or self.email or self.mobile_number or self.phone or ""


class LinkGoogleRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=1, max_length=128)
    pending_sub: str = Field(..., min_length=1, max_length=128)
    provider_email: Optional[str] = Field(None, max_length=120)


class AuthResponse(BaseModel):
    authenticated: bool
    user_id: Optional[UUID] = None
    identity_id: Optional[UUID] = None
    role: Optional[str] = None
    citizen_id: Optional[UUID] = None
    verification_state: Optional[str] = None
    citizen_name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = "hi"
    email_verified: Optional[bool] = False
    mobile_verified: Optional[bool] = False
    requires_mobile: Optional[bool] = False
    google_linked: Optional[bool] = False
    onboarding_completed: Optional[bool] = False
    onboarding_step: Optional[int] = 1
    session_token: Optional[str] = None
    token: Optional[str] = None
