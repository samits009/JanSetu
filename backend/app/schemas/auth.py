from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: Optional[str] = Field(None, max_length=120)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    password: str = Field(..., min_length=8, max_length=128)
    preferred_language: str = Field("hi", max_length=10)


class LoginRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=120)
    email: Optional[str] = Field(None, min_length=3, max_length=120)
    password: str = Field(..., min_length=1, max_length=128)

    def get_identifier(self) -> str:
        return self.username or self.email or ""


class AuthResponse(BaseModel):
    authenticated: bool
    user_id: Optional[UUID] = None
    identity_id: Optional[UUID] = None
    role: Optional[str] = None
    citizen_id: Optional[UUID] = None
    verification_state: Optional[str] = None
    citizen_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = "hi"
    onboarding_completed: Optional[bool] = False
    onboarding_step: Optional[int] = 1

