"""Event definitions for the Energy Domain Package.

Defines all event types emitted during energy domain operations
for observability, auditing, and integration hooks.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.energy.enums import AlarmSeverity, AssetType, EnergyDomain, SensorType


class EnergyEvent(BaseModel):
    """Base event for energy domain operations.

    All energy events inherit from this base class,
    providing common fields for event correlation.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )


class AssetRegistered(EnergyEvent):
    """Emitted when a new energy asset is registered."""

    asset_id: UUID4 = Field(
        description="The registered asset identifier",
    )
    asset_type: AssetType = Field(
        description="Type of the registered asset",
    )
    domain: EnergyDomain = Field(
        default=EnergyDomain.ELECTRICITY,
        description="Utility domain of the asset",
    )
    name: str = Field(
        default="",
        description="Name of the registered asset",
    )
    external_id: str = Field(
        default="",
        description="External identifier of the asset",
    )


class AssetUpdated(EnergyEvent):
    """Emitted when an energy asset is updated."""

    asset_id: UUID4 = Field(
        description="The updated asset identifier",
    )
    asset_type: AssetType = Field(
        description="Type of the updated asset",
    )
    previous_status: str = Field(
        default="",
        description="Previous status before update",
    )
    new_status: str = Field(
        default="",
        description="New status after update",
    )
    changed_fields: list[str] = Field(
        default_factory=list,
        description="Fields that were changed",
    )


class SensorReadingReceived(EnergyEvent):
    """Emitted when a sensor reading is received."""

    reading_id: UUID4 = Field(
        description="The reading identifier",
    )
    sensor_id: UUID4 = Field(
        description="The sensor that produced the reading",
    )
    asset_id: UUID4 = Field(
        description="The asset the reading relates to",
    )
    sensor_type: SensorType = Field(
        description="Type of sensor reading",
    )
    value: float = Field(
        description="The measured value",
    )
    unit: str = Field(
        default="",
        description="Unit of measurement",
    )
    quality: str = Field(
        default="good",
        description="Quality of the reading",
    )


class AlarmRaised(EnergyEvent):
    """Emitted when an alarm is raised."""

    alarm_id: UUID4 = Field(
        description="The alarm identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset the alarm relates to",
    )
    name: str = Field(
        default="",
        description="Alarm name",
    )
    severity: AlarmSeverity = Field(
        description="Severity of the alarm",
    )
    description: str = Field(
        default="",
        description="Description of the alarm condition",
    )


class IncidentCreated(EnergyEvent):
    """Emitted when an incident is created."""

    incident_id: UUID4 = Field(
        description="The incident identifier",
    )
    title: str = Field(
        default="",
        description="Incident title",
    )
    asset_ids: list[UUID4] = Field(
        default_factory=list,
        description="Assets involved in the incident",
    )
    priority: str = Field(
        default="MEDIUM",
        description="Priority of the incident",
    )
    impact_area: str = Field(
        default="",
        description="Area affected by the incident",
    )


class MaintenanceStarted(EnergyEvent):
    """Emitted when maintenance starts on an asset."""

    record_id: UUID4 = Field(
        description="The maintenance record identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset under maintenance",
    )
    maintenance_type: str = Field(
        description="Type of maintenance being performed",
    )
    work_order_id: UUID4 | None = Field(
        default=None,
        description="Associated work order identifier",
    )
    technician: str = Field(
        default="",
        description="Technician performing the maintenance",
    )


class MaintenanceCompleted(EnergyEvent):
    """Emitted when maintenance is completed on an asset."""

    record_id: UUID4 = Field(
        description="The maintenance record identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset that received maintenance",
    )
    maintenance_type: str = Field(
        description="Type of maintenance performed",
    )
    duration_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Duration of maintenance in hours",
    )
    findings: str = Field(
        default="",
        description="Summary of findings",
    )
