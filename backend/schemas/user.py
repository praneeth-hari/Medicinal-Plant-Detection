"""
User & Authentication Schemas
==============================

Pydantic models for user registration, login responses, and JWT tokens.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields.

    Attributes:
        username: Unique display name.
        email: Unique email address.
    """

    username: str = Field(..., min_length=3, max_length=150, examples=["herbalist42"])
    email: str = Field(..., max_length=255, examples=["user@example.com"])


class UserCreate(UserBase):
    """Schema for user registration.

    Attributes:
        password: Plain-text password (will be hashed server-side).
    """

    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    """Schema returned to clients when reading user data.

    Excludes sensitive fields like ``hashed_password``.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """OAuth2-compatible token response.

    Attributes:
        access_token: The JWT string.
        token_type: Token scheme, typically ``bearer``.
    """

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Payload extracted from a decoded JWT.

    Attributes:
        user_id: Subject identifier embedded in the token.
        username: Optional username claim.
    """

    user_id: Optional[int] = None
    username: Optional[str] = None
