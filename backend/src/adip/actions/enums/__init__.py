"""Enumerations for the Action Manager.

Defines all enum types used across action domain models,
contracts, and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class ActionType(StrEnum):
    """Type of action to be executed.

    Values:
    - MANUAL: Action requiring human intervention
    - AUTOMATED: Fully automated action
    - APPROVAL: Action requiring approval before execution
    - NOTIFICATION: Notification-only action
    - WORKFLOW: Multi-step workflow action
    - EXTERNAL_INTEGRATION: Action invoking an external system
    - EMERGENCY: Emergency override action
    """

    MANUAL = "MANUAL"
    AUTOMATED = "AUTOMATED"
    APPROVAL = "APPROVAL"
    NOTIFICATION = "NOTIFICATION"
    WORKFLOW = "WORKFLOW"
    EXTERNAL_INTEGRATION = "EXTERNAL_INTEGRATION"
    EMERGENCY = "EMERGENCY"


class ActionPriority(StrEnum):
    """Priority level for an action.

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


class ExecutionReadiness(StrEnum):
    """Readiness status for action execution.

    Values:
    - READY: Ready for execution
    - BLOCKED: Blocked — cannot proceed
    - WAITING: Waiting for dependencies or conditions
    - SCHEDULED: Scheduled for future execution
    """

    READY = "READY"
    BLOCKED = "BLOCKED"
    WAITING = "WAITING"
    SCHEDULED = "SCHEDULED"
