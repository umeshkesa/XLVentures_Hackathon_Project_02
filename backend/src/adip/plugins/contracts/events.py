"""Plugin Manager event models.

Events follow the standard ADIP eventing contract with a base
PluginEvent and concrete event types for each plugin lifecycle
operation. All events carry enterprise fields (event_id, timestamp,
correlation_id, payload) for tracing and audit.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType

EventVersion: str = "1.0.0"


class PluginEvent(BaseModel):
    """Base event for all plugin operations.

    Provides standard enterprise event fields shared by every
    concrete plugin event.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin this event relates to",
    )
    plugin_type: PluginType = Field(
        description="The type of plugin involved",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="The plugin domain",
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


class PluginDiscovered(PluginEvent):
    """Emitted when a new plugin is discovered."""

    discovery_source: str = Field(
        default="",
        description="Source of discovery (filesystem, registry, manual)",
    )


class PluginValidated(PluginEvent):
    """Emitted when a plugin passes validation."""

    validation_results: list[str] = Field(
        default_factory=list,
        description="Validation check results",
    )


class PluginInstalled(PluginEvent):
    """Emitted when a plugin is installed."""

    version: str = Field(
        default="1.0.0",
        description="The installed plugin version",
    )


class PluginLoaded(PluginEvent):
    """Emitted when a plugin is loaded into memory."""

    load_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to load in milliseconds",
    )


class PluginActivated(PluginEvent):
    """Emitted when a plugin is activated."""

    previous_status: PluginLifecycleStatus = Field(
        description="The lifecycle status before activation",
    )


class PluginSuspended(PluginEvent):
    """Emitted when a plugin is suspended."""

    reason: str = Field(
        default="",
        description="Reason for suspension",
    )


class PluginUnloaded(PluginEvent):
    """Emitted when a plugin is unloaded from memory."""

    unload_reason: str = Field(
        default="",
        description="Reason for unloading",
    )


class PluginRemoved(PluginEvent):
    """Emitted when a plugin is permanently removed."""

    removal_reason: str = Field(
        default="",
        description="Reason for removal",
    )


class SandboxCreated(PluginEvent):
    """Emitted when a sandbox is created for a plugin."""

    sandbox_id: UUID4 = Field(
        description="The sandbox identifier",
    )
    namespace: str = Field(
        default="",
        description="The sandbox namespace",
    )


class SandboxDestroyed(PluginEvent):
    """Emitted when a sandbox is destroyed."""

    sandbox_id: UUID4 = Field(
        description="The sandbox identifier",
    )
    reason: str = Field(
        default="",
        description="Reason for sandbox destruction",
    )
