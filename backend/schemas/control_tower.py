"""
Control Tower Schemas
=====================
Pydantic models for governance settings, monitoring statistics, and audit logs.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ControlTowerSettings(BaseModel):
    """Governance settings toggled in the Control Tower."""

    pii_masking: bool = Field(default=False, description="Mask PII in client queries")
    dosage_disclaimer: bool = Field(default=True, description="Append safety disclaimers for dosage queries")
    toxicity_guardrail: bool = Field(default=True, description="Block toxic queries")
    source_verification: bool = Field(default=True, description="Verify sources have references")


class AuditLogEntry(BaseModel):
    """Single query audit trail entry."""

    id: str
    timestamp: datetime
    user_query: str
    masked_query: Optional[str] = None
    policies_applied: List[str] = Field(default_factory=list)
    compliance_status: str = Field(default="PASSED")  # PASSED, WARNING, BLOCKED
    details: Optional[str] = None


class ServiceHealth(BaseModel):
    """Live health probe result for one subsystem."""

    name: str
    healthy: bool
    latency_ms: Optional[float] = None
    detail: Optional[str] = None


class ControlTowerStats(BaseModel):
    """System performance telemetry and metrics."""

    cpu_usage: float
    memory_usage: float
    active_sessions: int
    db_health: str = Field(default="Healthy")
    ollama_availability: str = Field(default="Available")
    total_queries: int
    avg_latency_ms: float
    latency_history: List[int] = Field(default_factory=list)
    token_history: List[int] = Field(default_factory=list)
    total_tokens: int = 0
    peak_tokens: int = 0
    services: List[ServiceHealth] = Field(default_factory=list)
    timestamp: datetime
