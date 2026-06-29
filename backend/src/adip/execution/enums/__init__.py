"""Enumerations for the Action Engine.

Defines all enum types used across execution domain models,
contracts, and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class ExecutionState(StrEnum):
    """State of an execution task or session.

    Values:
    - PENDING: Awaiting execution
    - READY: Ready to begin execution
    - RUNNING: Currently executing
    - WAITING: Waiting for dependencies or conditions
    - PAUSED: Execution paused
    - COMPLETED: Execution finished successfully
    - FAILED: Execution failed
    - CANCELLED: Execution cancelled
    - ROLLING_BACK: Rolling back changes
    - ROLLED_BACK: Changes rolled back
    """

    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"


class ExecutionMode(StrEnum):
    """Mode of execution.

    Values:
    - LIVE: Actual execution in production
    - SIMULATION: Simulated execution without side effects
    - DRY_RUN: Dry run — validate without executing
    - TEST: Test execution in a test environment
    """

    LIVE = "LIVE"
    SIMULATION = "SIMULATION"
    DRY_RUN = "DRY_RUN"
    TEST = "TEST"


class ExecutionPriority(StrEnum):
    """Priority level for an execution request.

    Values:
    - CRITICAL: Critical priority — immediate execution required
    - HIGH: High priority
    - MEDIUM: Medium priority
    - LOW: Low priority
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
