"""
Common Schemas
==============
Shared Pydantic models used across multiple endpoints —
standard response envelopes, pagination, and error formats.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Simple message response for operations without specific return data."""

    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[Any]
    total: int
    skip: int = 0
    limit: int = 20

    @property
    def has_next(self) -> bool:
        """Whether there are more pages after this one."""
        return (self.skip + self.limit) < self.total

    @property
    def has_prev(self) -> bool:
        """Whether there is a previous page."""
        return self.skip > 0


class ErrorResponse(BaseModel):
    """Standard error response format returned by exception handlers."""

    success: bool = False
    message: str
    detail: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(examples=["healthy"])
    service: str
    version: str
    timestamp: str
    checks: Optional[dict[str, Any]] = None
