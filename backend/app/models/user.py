"""
Predictify Pydantic Models — User
Schemas for user profile operations.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, TypeAdapter, field_validator


class UserProfile(BaseModel):
    """User profile data."""
    id: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    hourly_rate_usd: float = 75.0
    currency: str = "USD"
    theme: str = "system"
    timezone: str = "UTC"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """Request body for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = Field(None, max_length=2048)
    hourly_rate_usd: Optional[float] = Field(None, ge=10, le=500)
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    theme: Optional[Literal["light", "dark", "system"]] = None
    timezone: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, value: Optional[str]) -> Optional[str]:
        # Empty clears the avatar. Nonempty values must be browser-safe HTTP(S).
        if value:
            TypeAdapter(HttpUrl).validate_python(value)
        return value
