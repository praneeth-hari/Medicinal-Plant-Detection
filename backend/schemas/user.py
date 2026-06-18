"""
User & Authentication Schemas
==============================
Pydantic models for user registration, login responses, and JWT
tokens.  Includes field-level validation for email, username, and
password strength.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    """Shared user fields."""

    username: str = Field(
        ..., min_length=3, max_length=50, examples=["herbalist42"]
    )
    email: str = Field(
        ..., max_length=255, examples=["user@example.com"]
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email format validation."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Username must be alphanumeric with underscores/hyphens."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, "
                "underscores, and hyphens"
            )
        return v.strip()


class UserCreate(UserBase):
    """Schema for user registration.

    Attributes:
        password: Plain-text password (will be hashed server-side).
        role: Assigned role — defaults to 'customer'.
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Must be at least 8 characters with mixed case and a digit",
    )
    role: str = Field(default="customer", pattern="^(customer|developer)$")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password has minimum complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    """Schema returned to clients when reading user data.

    Excludes sensitive fields like ``hashed_password``.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    role: str = "customer"
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """Schema for user login."""

    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(...)


class Token(BaseModel):
    """OAuth2-compatible token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token lifetime in seconds")


class TokenData(BaseModel):
    """Payload extracted from a decoded JWT."""

    user_id: Optional[int] = None
    username: Optional[str] = None
    role: str = "customer"


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
