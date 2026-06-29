"""Rule Manager event models.

Events follow the standard ADIP eventing contract with a base
RuleEvent and concrete event types for each rule operation. All
events carry enterprise fields (event_id, timestamp, correlation_id,
payload) for tracing and audit.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.rules.enums import RuleDomain, RuleLifecycleStatus, RuleType

EventVersion: str = "1.0.0"


class RuleEvent(BaseModel):
    """Base event for all rule operations.

    Provides standard enterprise event fields shared by every
    concrete rule event.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    rule_id: UUID4 = Field(
        description="The rule this event relates to",
    )
    rule_type: RuleType = Field(
        description="The type of rule involved",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The rule domain",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event was emitted",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary event payload data",
    )


class RuleCreated(RuleEvent):
    """Emitted when a new rule is created."""

    version: int = Field(
        default=1,
        ge=1,
        description="The initial rule version",
    )


class RuleUpdated(RuleEvent):
    """Emitted when an existing rule is updated."""

    previous_version: int = Field(
        default=0,
        ge=0,
        description="The rule version before the update",
    )
    new_version: int = Field(
        default=1,
        ge=1,
        description="The rule version after the update",
    )


class RuleActivated(RuleEvent):
    """Emitted when a rule is activated (transitioned to ACTIVE status)."""

    previous_status: RuleLifecycleStatus = Field(
        description="The lifecycle status before activation",
    )
    activated_by: str = Field(
        default="",
        description="The user or system that activated the rule",
    )


class RuleEvaluated(RuleEvent):
    """Emitted when a rule is evaluated."""

    context_id: UUID4 = Field(
        description="The evaluation context identifier",
    )
    matched: bool = Field(
        default=False,
        description="Whether the rule conditions matched",
    )
    decision: str = Field(
        default="",
        description="The decision outcome",
    )
    evaluation_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to evaluate in milliseconds",
    )


class RuleConflictDetected(RuleEvent):
    """Emitted when a rule conflict is detected during evaluation."""

    conflicting_rule_id: UUID4 = Field(
        description="The ID of the conflicting rule",
    )
    conflicting_rule_name: str = Field(
        default="",
        description="The name of the conflicting rule",
    )
    conflict_type: str = Field(
        default="",
        description="The type of conflict (direct_overlap, priority_inversion, circular_dependency)",
    )
    resolution: str = Field(
        default="",
        description="How the conflict was resolved",
    )


class RuleArchived(RuleEvent):
    """Emitted when a rule is archived."""

    reason: str = Field(
        default="",
        description="Reason for archiving",
    )
