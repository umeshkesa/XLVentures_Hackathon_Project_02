"""MemoryHealth — health check model for the Memory Platform.

Tracks overall and per-component health status, latency, error
counts, and domain/tier health for monitoring and observability.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class MemoryHealth(BaseModel):
    """Aggregated health status of the Memory Manager platform."""

    overall_status: str = Field(
        default="HEALTHY",
        description="Overall health: HEALTHY, DEGRADED, or UNHEALTHY",
    )
    router_status: str = Field(
        default="HEALTHY",
        description="MemoryRouter health",
    )
    coordinator_status: str = Field(
        default="HEALTHY",
        description="MemoryCoordinator health",
    )
    lifecycle_status: str = Field(
        default="HEALTHY",
        description="LifecycleManager health",
    )
    policy_status: str = Field(
        default="HEALTHY",
        description="PolicyEngine health",
    )
    cache_status: str = Field(
        default="HEALTHY",
        description="CacheManager health",
    )
    storage_status: dict[str, str] = Field(
        default_factory=lambda: {"HOT": "HEALTHY", "WARM": "HEALTHY", "COLD": "HEALTHY"},
        description="Per-tier storage health",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average operation latency in milliseconds",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    operations_per_minute: float = Field(
        default=0.0,
        ge=0.0,
        description="Throughput in operations per minute",
    )
    error_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Error rate as a fraction (0.0–1.0)",
    )
    last_successful_operation: str = Field(
        default="",
        description="Description of the last successful operation",
    )
    last_checked_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the health check was last performed",
    )
    domain_health: dict[str, str] = Field(
        default_factory=dict,
        description="Per-domain health status",
    )
    tier_health: dict[str, str] = Field(
        default_factory=lambda: {"HOT": "HEALTHY", "WARM": "HEALTHY", "COLD": "HEALTHY"},
        description="Per-tier health status",
    )

    def is_healthy(self) -> bool:
        """Return True if overall status is HEALTHY."""
        return self.overall_status == "HEALTHY"
