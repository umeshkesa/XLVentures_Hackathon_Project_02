"""Workflow Engine enums."""

from __future__ import annotations

from enum import StrEnum


class WorkflowStatus(StrEnum):
    """Lifecycle states of a workflow execution."""
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    GRAPH_BUILT = "GRAPH_BUILT"
    SCHEDULED = "SCHEDULED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskExecutionStatus(StrEnum):
    """Runtime status of an individual workflow task."""
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"


class ExecutionMode(StrEnum):
    """How tasks within a group are executed."""
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    CONDITIONAL = "CONDITIONAL"


class RetryPolicy(StrEnum):
    """Strategy for retrying failed tasks."""
    NEVER = "NEVER"
    IMMEDIATE = "IMMEDIATE"
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"
    FIXED_DELAY = "FIXED_DELAY"
