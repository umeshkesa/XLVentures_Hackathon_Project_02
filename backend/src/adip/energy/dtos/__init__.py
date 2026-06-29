"""Data Transfer Objects for the Energy Domain Package.

DTOs provide clean separation between API contracts and
internal domain models, enabling API evolution without
affecting internal logic.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.energy.enums import (
    AlarmSeverity,
    AlarmStatus,
    AssetStatus,
    AssetType,
    EnergyDomain,
    HealthState,
    IncidentPriority,
    MaintenanceType,
    SensorType,
    WorkOrderStatus,
)


class EnergyAssetDTO(BaseModel):
    """DTO for energy asset API operations.

    Lightweight DTO for asset creation and update endpoints.
    """

    asset_id: UUID4 | None = Field(
        default=None,
        description="Asset identifier (assigned by system if omitted)",
    )
    external_id: str = Field(
        default="",
        description="External identifier from source system",
    )
    name: str = Field(
        default="",
        description="Human-readable asset name",
    )
    asset_type: AssetType = Field(
        description="Type of energy asset",
    )
    domain: EnergyDomain = Field(
        default=EnergyDomain.ELECTRICITY,
        description="Utility domain this asset belongs to",
    )
    status: AssetStatus = Field(
        default=AssetStatus.ACTIVE,
        description="Operational status of the asset",
    )
    location: str = Field(
        default="",
        description="Geographic or logical location",
    )
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="Latitude coordinate",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="Longitude coordinate",
    )
    rated_capacity: float | None = Field(
        default=None,
        ge=0.0,
        description="Rated capacity in appropriate units",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising the asset",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional asset metadata",
    )


class SensorDTO(BaseModel):
    """DTO for sensor API operations.

    Lightweight DTO for sensor creation and update endpoints.
    """

    sensor_id: UUID4 | None = Field(
        default=None,
        description="Sensor identifier (assigned by system if omitted)",
    )
    asset_id: UUID4 = Field(
        description="The asset this sensor is attached to",
    )
    external_id: str = Field(
        default="",
        description="External identifier from source system",
    )
    name: str = Field(
        default="",
        description="Human-readable sensor name",
    )
    sensor_type: SensorType = Field(
        description="Type of measurement this sensor provides",
    )
    unit: str = Field(
        default="",
        description="Measurement unit",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the sensor is currently active",
    )
    sampling_interval_seconds: int = Field(
        default=60,
        ge=1,
        description="Sampling interval in seconds",
    )
    location: str = Field(
        default="",
        description="Specific location on or near the asset",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional sensor metadata",
    )


class DigitalTwinDTO(BaseModel):
    """DTO for digital twin API operations.

    Lightweight DTO for digital twin creation and update endpoints.
    """

    twin_id: UUID4 | None = Field(
        default=None,
        description="Twin identifier (assigned by system if omitted)",
    )
    asset_id: UUID4 = Field(
        description="The physical asset this twin represents",
    )
    twin_type: str = Field(
        default="simulation",
        description="Type of twin (simulation, monitoring, predictive)",
    )
    model_version: str = Field(
        default="1.0.0",
        description="Version of the digital twin model",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Twin model parameters",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the digital twin is active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional digital twin metadata",
    )


class AlarmDTO(BaseModel):
    """DTO for alarm API operations.

    Lightweight DTO for alarm creation and update endpoints.
    """

    alarm_id: UUID4 | None = Field(
        default=None,
        description="Alarm identifier (assigned by system if omitted)",
    )
    asset_id: UUID4 = Field(
        description="The asset this alarm relates to",
    )
    external_id: str = Field(
        default="",
        description="External alarm identifier",
    )
    name: str = Field(
        default="",
        description="Alarm name or title",
    )
    description: str = Field(
        default="",
        description="Detailed description of the alarm condition",
    )
    severity: AlarmSeverity = Field(
        default=AlarmSeverity.WARNING,
        description="Severity of the alarm",
    )
    status: AlarmStatus = Field(
        default=AlarmStatus.ACTIVE,
        description="Current status of the alarm",
    )
    source: str = Field(
        default="",
        description="Source of the alarm",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional alarm metadata",
    )


class IncidentDTO(BaseModel):
    """DTO for incident API operations.

    Lightweight DTO for incident creation and update endpoints.
    """

    incident_id: UUID4 | None = Field(
        default=None,
        description="Incident identifier (assigned by system if omitted)",
    )
    external_id: str = Field(
        default="",
        description="External incident identifier",
    )
    title: str = Field(
        default="",
        description="Incident title",
    )
    description: str = Field(
        default="",
        description="Detailed description of the incident",
    )
    asset_ids: list[UUID4] = Field(
        default_factory=list,
        description="Assets involved in the incident",
    )
    alarm_ids: list[UUID4] = Field(
        default_factory=list,
        description="Related alarm identifiers",
    )
    priority: IncidentPriority = Field(
        default=IncidentPriority.MEDIUM,
        description="Priority of the incident",
    )
    impact_area: str = Field(
        default="",
        description="Area affected by the incident",
    )
    customers_affected: int = Field(
        default=0,
        ge=0,
        description="Number of customers affected",
    )
    reported_by: str = Field(
        default="",
        description="User or system that reported the incident",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional incident metadata",
    )
