"""Centralised application constants and enumerations.

Every named value that appears in more than one place — or that describes
a bounded domain concept — lives here instead of as a magic string or
literal scattered across the codebase.

Import directly::

    from adip.core.constants import (
        Environment, WorkflowStatus, RulePriority,
        ConfidenceLevel, ActionStatus, LogLevel,
        Role,
    )
"""

from __future__ import annotations

from enum import Enum, StrEnum

# ── User roles ───────────────────────────────────────────────────────────

class Role(StrEnum):
    """Pre-defined roles ordered from highest to lowest privilege."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


# ── Workflow ─────────────────────────────────────────────────────────────

class WorkflowStatus(StrEnum):
    """Lifecycle states for a workflow run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


# ── Rule engine ──────────────────────────────────────────────────────────

class RulePriority(StrEnum):
    """Evaluation priority (critical first)."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ── Confidence / scoring ─────────────────────────────────────────────────

class ConfidenceLevel(float, Enum):
    """Standardised confidence brackets for AI and heuristic results."""

    CERTAIN = 1.0
    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.7
    LOW = 0.4
    VERY_LOW = 0.15
    UNCERTAIN = 0.05
    NONE = 0.0


# ── Action management ────────────────────────────────────────────────────

class ActionStatus(StrEnum):
    """Lifecycle states for a queued or executed action."""

    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


# ── Logging ──────────────────────────────────────────────────────────────

class LogLevel(StrEnum):
    """Log severity levels mirroring Python's ``logging`` module."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(StrEnum):
    """Structured-logging output format."""

    JSON = "json"
    CONSOLE = "console"


# ── Environment ──────────────────────────────────────────────────────────

class Environment(StrEnum):
    """Deployment environment identifiers."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


# ── Application metadata ────────────────────────────────────────────────

APP_NAME = "ADIP"
"""Human-readable application name."""

APP_VERSION = "0.1.0"
"""Current semantic version."""

API_PREFIX = "/api/v1"
"""Default URL prefix for all REST endpoints."""

DEFAULT_PAGE_SIZE = 20
"""Default number of items per page when none is specified."""

MAX_PAGE_SIZE = 100
"""Hard upper limit for page size to prevent abuse."""

DEFAULT_POOL_SIZE = 10
"""Default database connection pool size."""
