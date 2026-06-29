"""Registry Framework event models.

Events follow the standard ADIP eventing contract with a base
RegistryEvent and concrete event types for each registry operation.
All events carry enterprise fields (event_id, timestamp, correlation_id,
payload) for tracing and audit.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.registry.enums import RegistryLifecycleStatus, RegistryScope, RegistryType

EventVersion: str = "1.0.0"


class RegistryEvent(BaseModel):
    """Base event for all registry operations.

    Provides standard enterprise event fields shared by every
    concrete registry event.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    entry_id: UUID4 = Field(
        description="The registry entry this event relates to",
    )
    registry_type: RegistryType = Field(
        description="The type of registry involved",
    )
    scope: RegistryScope = Field(
        default=RegistryScope.GLOBAL,
        description="The scope of the entry involved",
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


class EntryRegistered(RegistryEvent):
    """Emitted when a new entry is registered in the registry."""

    version: str = Field(
        default="1.0.0",
        description="The initial entry version",
    )
    registered_by: str = Field(
        default="",
        description="The user or system that registered the entry",
    )


class EntryUpdated(RegistryEvent):
    """Emitted when an existing registry entry is updated."""

    previous_version: str = Field(
        default="",
        description="The entry version before the update",
    )
    new_version: str = Field(
        default="1.0.0",
        description="The entry version after the update",
    )
    updated_by: str = Field(
        default="",
        description="The user or system that updated the entry",
    )


class EntryValidated(RegistryEvent):
    """Emitted when a registry entry passes validation."""

    validation_results: list[str] = Field(
        default_factory=list,
        description="Validation check results",
    )
    valid: bool = Field(
        default=True,
        description="Whether the entry passed all validation checks",
    )


class EntryActivated(RegistryEvent):
    """Emitted when a registry entry is activated."""

    previous_status: RegistryLifecycleStatus = Field(
        description="The lifecycle status before activation",
    )
    activated_by: str = Field(
        default="",
        description="The user or system that activated the entry",
    )


class EntryDeprecated(RegistryEvent):
    """Emitted when a registry entry is deprecated."""

    reason: str = Field(
        default="",
        description="Reason for deprecation",
    )
    replacement_entry_id: UUID4 | None = Field(
        default=None,
        description="ID of the replacement entry (if applicable)",
    )


class EntryRemoved(RegistryEvent):
    """Emitted when a registry entry is permanently removed."""

    reason: str = Field(
        default="",
        description="Reason for removal",
    )
    removed_by: str = Field(
        default="",
        description="The user or system that removed the entry",
    )
