"""
User schemas
============
Pydantic model describing the (single, login-free) current user.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    """Identity of the current user attached to each request."""

    user_id: Optional[int] = None
    username: Optional[str] = None
