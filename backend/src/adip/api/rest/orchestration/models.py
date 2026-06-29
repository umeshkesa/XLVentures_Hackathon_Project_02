"""Orchestration models — ApiSession, ApiDecision, APISecurityContext, APIFeatureFlags.

Phase 3.5 enhancements:
  - ApiDecision: quality_score, compliance_status, diagnostics, performance_profile,
    endpoint_health, governance_result, replay_package, export_package,
    pipeline_version, manifest, documentation_metadata
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from adip.api.rest.enums import (
    ComplianceStatus,
    HealthStatus,
    OperationStatus,
    ReadinessStatus,
)


class ApiSession(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    route: str = Field(default="", description="Request route path")
    method: str = Field(default="GET", description="HTTP method")
    status: OperationStatus = Field(default=OperationStatus.PENDING)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = Field(default=None)
    correlation_id: str | None = Field(default=None)
    api_version: str = Field(default="v1")


class ApiDecision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    session_id: UUID | None = Field(default=None)
    success: bool = Field(default=True)
    status_code: int = Field(default=200)
    response: dict[str, Any] = Field(default_factory=dict)
    validation_passed: bool = Field(default=True)
    processing_time_ms: float = Field(default=0.0)
    api_version: str = Field(default="v1")

    # Phase 3.5 — Enterprise refinement
    http_status: int = Field(default=200, description="HTTP status code (alias)")
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    compliance_status: ComplianceStatus = Field(default=ComplianceStatus.PENDING)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    performance_profile: dict[str, Any] = Field(default_factory=dict)
    endpoint_health: HealthStatus = Field(default=HealthStatus.HEALTHY)
    governance_result: dict[str, Any] = Field(default_factory=dict)
    replay_package: dict[str, Any] = Field(default_factory=dict)
    export_package: dict[str, Any] = Field(default_factory=dict)
    pipeline_version: str | None = Field(default=None)
    manifest: dict[str, Any] = Field(default_factory=dict)
    documentation_metadata: dict[str, Any] = Field(default_factory=dict)
    readiness_status: ReadinessStatus = Field(default=ReadinessStatus.NOT_READY)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class APISecurityContext(BaseModel):
    user_id: str | None = Field(default=None)
    tenant_id: str | None = Field(default=None)
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    auth_metadata: dict[str, Any] = Field(default_factory=dict)

    def is_authenticated(self) -> bool:
        return self.user_id is not None

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions


class APIFeatureFlag(BaseModel):
    name: str = Field(description="Feature flag name")
    enabled: bool = Field(default=False)
    api_version: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class APIFeatureFlags(BaseModel):
    flags: list[APIFeatureFlag] = Field(default_factory=list)

    def is_enabled(self, name: str) -> bool:
        for flag in self.flags:
            if flag.name == name:
                return flag.enabled
        return False

    def enable(self, name: str) -> None:
        for flag in self.flags:
            if flag.name == name:
                flag.enabled = True
                return
        self.flags.append(APIFeatureFlag(name=name, enabled=True))

    def disable(self, name: str) -> None:
        for flag in self.flags:
            if flag.name == name:
                flag.enabled = False
                return
        self.flags.append(APIFeatureFlag(name=name, enabled=False))

    def list_enabled(self) -> list[str]:
        return [f.name for f in self.flags if f.enabled]
