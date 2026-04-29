"""
Predictify Pydantic Models — User
Schemas for user profile operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


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
    avatar_url: Optional[str] = None
    hourly_rate_usd: Optional[float] = Field(None, ge=10, le=500)
    currency: Optional[Literal["USD", "EUR", "GBP", "INR"]] = None
    theme: Optional[Literal["light", "dark", "system"]] = None
    timezone: Optional[str] = None
