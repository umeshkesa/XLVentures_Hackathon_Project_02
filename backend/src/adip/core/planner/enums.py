"""Planner lifecycle and policy enumerations."""

from enum import StrEnum

from adip.core.constants import ConfidenceLevel


class Priority(StrEnum):
    """Relative urgency assigned to planning work."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class PlanningStrategy(StrEnum):
    """Requested execution topology for a generated plan."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


class PlannerStatus(StrEnum):
    """Observable lifecycle states of a planning request."""

    PENDING = "pending"
    ANALYZING = "analyzing"
    MATCHING = "matching"
    GENERATING = "generating"
    VALIDATING = "validating"
    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(StrEnum):
    """Lifecycle states exposed by a planned task contract."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


__all__ = [
    "ConfidenceLevel",
    "PlannerStatus",
    "PlanningStrategy",
    "Priority",
    "TaskStatus",
]
