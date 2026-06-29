"""Domain models for the Energy Domain Package.

Defines all domain models for energy asset management,
sensor telemetry, maintenance, alarms, incidents, and
operational context.
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


class EnergyAsset(BaseModel):
    """An energy asset in the utility infrastructure.

    Represents any physical or logical asset within the energy
    domain, such as transformers, substations, generators,
    meters, and sensors. Supports multi-utility deployments
    through the domain field.
    """

    asset_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique asset identifier",
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
    manufacturer: str = Field(
        default="",
        description="Asset manufacturer",
    )
    model: str = Field(
        default="",
        description="Asset model number",
    )
    serial_number: str = Field(
        default="",
        description="Asset serial number",
    )
    installation_date: datetime | None = Field(
        default=None,
        description="When the asset was installed",
    )
    commission_date: datetime | None = Field(
        default=None,
        description="When the asset was commissioned",
    )
    rated_capacity: float | None = Field(
        default=None,
        ge=0.0,
        description="Rated capacity in appropriate units",
    )
    rated_voltage: float | None = Field(
        default=None,
        ge=0.0,
        description="Rated voltage in kV",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising the asset",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional asset metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the asset record was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the asset record was last updated",
    )


class AssetHierarchy(BaseModel):
    """Hierarchical relationship between energy assets.

    Defines parent-child relationships within the asset
    hierarchy, enabling asset tree traversal and impact
    analysis.
    """

    hierarchy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique hierarchy identifier",
    )
    parent_asset_id: UUID4 = Field(
        description="The parent asset identifier",
    )
    child_asset_id: UUID4 = Field(
        description="The child asset identifier",
    )
    relationship_type: str = Field(
        default="contains",
        description="Type of relationship (contains, feeds, monitors, etc.)",
    )
    level: int = Field(
        default=0,
        ge=0,
        description="Hierarchy level (0 = root)",
    )
    path: list[UUID4] = Field(
        default_factory=list,
        description="Ordered list of asset IDs from root to this node",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional hierarchy metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the hierarchy record was created",
    )


class AssetRelationship(BaseModel):
    """Typed relationship between two energy assets.

    Captures arbitrary relationships between assets beyond
    simple hierarchy, such as connectivity, redundancy,
    or operational dependency.
    """

    relationship_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique relationship identifier",
    )
    source_asset_id: UUID4 = Field(
        description="The source asset identifier",
    )
    target_asset_id: UUID4 = Field(
        description="The target asset identifier",
    )
    relationship_type: str = Field(
        description="Type of relationship (feeds, backs_up, monitors, etc.)",
    )
    direction: str = Field(
        default="directed",
        description="Directionality: directed, bidirectional",
    )
    weight: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relationship strength or importance weight",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional relationship metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the relationship was created",
    )


class DigitalTwin(BaseModel):
    """Digital twin representation of an energy asset.

    Provides a virtual representation of a physical asset
    that can be used for simulation, monitoring, and
    predictive analytics.
    """

    twin_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique digital twin identifier",
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
    state: dict[str, Any] = Field(
        default_factory=dict,
        description="Current state of the digital twin",
    )
    last_synchronised: datetime | None = Field(
        default=None,
        description="When the twin was last synchronised with the physical asset",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the digital twin is active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional digital twin metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the digital twin was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the digital twin was last updated",
    )


class Sensor(BaseModel):
    """A sensor device attached to an energy asset.

    Represents a physical or virtual sensor that measures
    a specific parameter of an energy asset.
    """

    sensor_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique sensor identifier",
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
        description="Measurement unit (e.g., °C, kV, A, MW)",
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
    accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Sensor accuracy percentage",
    )
    min_range: float | None = Field(
        default=None,
        description="Minimum measurable value",
    )
    max_range: float | None = Field(
        default=None,
        description="Maximum measurable value",
    )
    location: str = Field(
        default="",
        description="Specific location on or near the asset",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional sensor metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the sensor record was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the sensor record was last updated",
    )


class SensorReading(BaseModel):
    """A single reading from a sensor.

    Captures a measurement value at a specific point in time
    with quality and provenance metadata.
    """

    reading_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique reading identifier",
    )
    sensor_id: UUID4 = Field(
        description="The sensor that produced this reading",
    )
    asset_id: UUID4 = Field(
        description="The asset this reading relates to",
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
        description="Reading quality: good,可疑, bad, substituted",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the reading was taken",
    )
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the reading was received by the system",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional reading metadata",
    )


class AssetHealth(BaseModel):
    """Health status of an energy asset.

    Provides a comprehensive view of asset health based on
    sensor readings, maintenance history, and operational
    context.
    """

    health_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique health identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset this health record belongs to",
    )
    health_state: HealthState = Field(
        default=HealthState.NORMAL,
        description="Current health state",
    )
    overall_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall health score (0.0 = critical, 1.0 = perfect)",
    )
    temperature_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Temperature-based health score",
    )
    vibration_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Vibration-based health score",
    )
    efficiency_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Operational efficiency score",
    )
    age_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Age-based degradation score",
    )
    maintenance_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Maintenance compliance score",
    )
    alerts: list[str] = Field(
        default_factory=list,
        description="Active alerts affecting health",
    )
    last_assessment: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last assessed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional health metadata",
    )


class MaintenanceRecord(BaseModel):
    """A record of a maintenance action performed on an asset.

    Captures the details of a completed maintenance activity
    including work performed, parts used, and duration.
    """

    record_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique maintenance record identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset that received maintenance",
    )
    maintenance_type: MaintenanceType = Field(
        description="Type of maintenance performed",
    )
    work_order_id: UUID4 | None = Field(
        default=None,
        description="Associated work order identifier",
    )
    description: str = Field(
        default="",
        description="Description of maintenance performed",
    )
    technician: str = Field(
        default="",
        description="Technician who performed the maintenance",
    )
    parts_used: list[str] = Field(
        default_factory=list,
        description="Parts or materials used",
    )
    duration_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Duration of maintenance in hours",
    )
    cost: float | None = Field(
        default=None,
        ge=0.0,
        description="Cost of maintenance",
    )
    downtime_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Asset downtime caused by maintenance in hours",
    )
    findings: str = Field(
        default="",
        description="Findings or observations from the maintenance",
    )
    recommendations: str = Field(
        default="",
        description="Recommendations for future maintenance",
    )
    scheduled_date: datetime | None = Field(
        default=None,
        description="When the maintenance was scheduled",
    )
    completed_date: datetime | None = Field(
        default=None,
        description="When the maintenance was completed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional maintenance metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the record was created",
    )


class MaintenancePlan(BaseModel):
    """A planned maintenance schedule for an asset.

    Defines when and how maintenance should be performed
    on an asset, including triggers and recurrence rules.
    """

    plan_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique maintenance plan identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset this plan applies to",
    )
    maintenance_type: MaintenanceType = Field(
        description="Type of maintenance planned",
    )
    name: str = Field(
        default="",
        description="Name of the maintenance plan",
    )
    description: str = Field(
        default="",
        description="Description of the maintenance plan",
    )
    interval_days: int = Field(
        default=0,
        ge=0,
        description="Recurrence interval in days (0 = one-time)",
    )
    trigger_condition: str = Field(
        default="",
        description="Condition that triggers maintenance (e.g., reading threshold)",
    )
    estimated_duration_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated duration in hours",
    )
    estimated_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated cost",
    )
    required_parts: list[str] = Field(
        default_factory=list,
        description="Parts or materials required",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Skills or certifications required",
    )
    safety_instructions: str = Field(
        default="",
        description="Safety instructions for this maintenance",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this plan is active",
    )
    next_due_date: datetime | None = Field(
        default=None,
        description="When the next maintenance is due",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional plan metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plan was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plan was last updated",
    )


class Alarm(BaseModel):
    """An alarm raised for an energy asset.

    Represents an alert or notification generated by asset
    monitoring, indicating an abnormal condition that may
    require attention.
    """

    alarm_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique alarm identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset this alarm relates to",
    )
    external_id: str = Field(
        default="",
        description="External alarm identifier from source system",
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
        description="Source of the alarm (sensor, analytics, manual)",
    )
    acknowledged_by: str = Field(
        default="",
        description="User who acknowledged the alarm",
    )
    acknowledged_at: datetime | None = Field(
        default=None,
        description="When the alarm was acknowledged",
    )
    resolved_by: str = Field(
        default="",
        description="User who resolved the alarm",
    )
    resolved_at: datetime | None = Field(
        default=None,
        description="When the alarm was resolved",
    )
    raised_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the alarm was raised",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional alarm metadata",
    )


class Incident(BaseModel):
    """An operational incident in the energy domain.

    Captures details of an incident event, such as an outage,
    equipment failure, or safety event, including impact
    assessment and resolution tracking.
    """

    incident_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique incident identifier",
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
    is_resolved: bool = Field(
        default=False,
        description="Whether the incident has been resolved",
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
    outage_duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Duration of outage in minutes",
    )
    root_cause: str = Field(
        default="",
        description="Root cause of the incident",
    )
    resolution: str = Field(
        default="",
        description="How the incident was resolved",
    )
    reported_by: str = Field(
        default="",
        description="User or system that reported the incident",
    )
    reported_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the incident was reported",
    )
    resolved_at: datetime | None = Field(
        default=None,
        description="When the incident was resolved",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional incident metadata",
    )


class WorkOrder(BaseModel):
    """A work order for maintenance or operational tasks.

    Represents a formal request for work to be performed
    on an energy asset, tracking assignment, execution,
    and completion.
    """

    work_order_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique work order identifier",
    )
    external_id: str = Field(
        default="",
        description="External work order identifier",
    )
    asset_id: UUID4 = Field(
        description="The asset this work order relates to",
    )
    incident_id: UUID4 | None = Field(
        default=None,
        description="Related incident identifier",
    )
    alarm_id: UUID4 | None = Field(
        default=None,
        description="Related alarm identifier",
    )
    title: str = Field(
        default="",
        description="Work order title",
    )
    description: str = Field(
        default="",
        description="Detailed description of work to be performed",
    )
    status: WorkOrderStatus = Field(
        default=WorkOrderStatus.OPEN,
        description="Current status of the work order",
    )
    priority: IncidentPriority = Field(
        default=IncidentPriority.MEDIUM,
        description="Priority of the work order",
    )
    assigned_to: str = Field(
        default="",
        description="Technician or team assigned to the work order",
    )
    scheduled_start: datetime | None = Field(
        default=None,
        description="Scheduled start time",
    )
    scheduled_end: datetime | None = Field(
        default=None,
        description="Scheduled end time",
    )
    actual_start: datetime | None = Field(
        default=None,
        description="Actual start time",
    )
    actual_end: datetime | None = Field(
        default=None,
        description="Actual end time",
    )
    estimated_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated hours to complete",
    )
    actual_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Actual hours worked",
    )
    notes: str = Field(
        default="",
        description="Work order notes and observations",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional work order metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the work order was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the work order was last updated",
    )


class EnergyContext(BaseModel):
    """Contextual information for an energy operation.

    Provides asset, location, domain, and environmental
    context to inform energy domain decisions and operations.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    asset_id: UUID4 | None = Field(
        default=None,
        description="The primary asset in context",
    )
    domain: EnergyDomain = Field(
        default=EnergyDomain.ELECTRICITY,
        description="The utility domain",
    )
    facility_id: str = Field(
        default="",
        description="Facility or site identifier",
    )
    region: str = Field(
        default="",
        description="Geographic region",
    )
    weather_conditions: str = Field(
        default="",
        description="Current weather conditions affecting operations",
    )
    load_condition: str = Field(
        default="normal",
        description="Current load condition (normal, peak, off_peak)",
    )
    season: str = Field(
        default="",
        description="Current season",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the context was captured",
    )


class EnergyMetadata(BaseModel):
    """Metadata describing an energy entity.

    Provides standard metadata fields for energy domain
    entities including classification, versioning, and
    source tracking.
    """

    title: str = Field(
        default="",
        description="Title of the energy entity",
    )
    description: str = Field(
        default="",
        description="Description of the energy entity",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising the entity",
    )
    category: str = Field(
        default="",
        description="Category of the entity",
    )
    source: str = Field(
        default="",
        description="Source system of the entity",
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the entity schema",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class EnergyMetrics(BaseModel):
    """Metrics for the Energy Domain Package.

    Captures operational metrics including asset counts,
    sensor readings, maintenance activities, alarms,
    incidents, quality, diagnostics, compliance, and
    pipeline versions.
    """

    assets_total: int = Field(
        default=0,
        ge=0,
        description="Total number of registered assets",
    )
    assets_active: int = Field(
        default=0,
        ge=0,
        description="Number of active assets",
    )
    assets_in_maintenance: int = Field(
        default=0,
        ge=0,
        description="Number of assets under maintenance",
    )
    assets_offline: int = Field(
        default=0,
        ge=0,
        description="Number of offline assets",
    )
    sensors_total: int = Field(
        default=0,
        ge=0,
        description="Total number of sensors",
    )
    sensors_active: int = Field(
        default=0,
        ge=0,
        description="Number of active sensors",
    )
    readings_total: int = Field(
        default=0,
        ge=0,
        description="Total number of sensor readings",
    )
    alarms_active: int = Field(
        default=0,
        ge=0,
        description="Number of active alarms",
    )
    alarms_critical: int = Field(
        default=0,
        ge=0,
        description="Number of critical alarms",
    )
    incidents_open: int = Field(
        default=0,
        ge=0,
        description="Number of open incidents",
    )
    work_orders_open: int = Field(
        default=0,
        ge=0,
        description="Number of open work orders",
    )
    work_orders_completed: int = Field(
        default=0,
        ge=0,
        description="Number of completed work orders",
    )
    maintenance_scheduled: int = Field(
        default=0,
        ge=0,
        description="Number of scheduled maintenance activities",
    )
    maintenance_completed: int = Field(
        default=0,
        ge=0,
        description="Number of completed maintenance activities",
    )
    average_health_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average health score across all assets",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall domain quality score",
    )
    diagnostics_count: int = Field(
        default=0,
        ge=0,
        description="Number of diagnostics collected",
    )
    compliance_violations: int = Field(
        default=0,
        ge=0,
        description="Number of compliance violations detected",
    )
    pipeline_versions: int = Field(
        default=0,
        ge=0,
        description="Number of pipeline versions tracked",
    )
    audits_created: int = Field(
        default=0,
        ge=0,
        description="Number of audit packages created",
    )
    exports_created: int = Field(
        default=0,
        ge=0,
        description="Number of export profiles created",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the metrics were captured",
    )


class EnergyHealth(BaseModel):
    """Health status for the Energy Domain Package.

    Provides a comprehensive view of the health of all
    energy domain sub-components and overall system status,
    including quality, compliance, diagnostics, audit,
    export, and pipeline version status.
    """

    overall_status: str = Field(
        default="",
        description="Overall health status",
    )
    asset_service_status: str = Field(
        default="",
        description="Status of the asset service",
    )
    sensor_service_status: str = Field(
        default="",
        description="Status of the sensor service",
    )
    digital_twin_status: str = Field(
        default="",
        description="Status of the digital twin service",
    )
    maintenance_service_status: str = Field(
        default="",
        description="Status of the maintenance service",
    )
    alarm_service_status: str = Field(
        default="",
        description="Status of the alarm service",
    )
    incident_service_status: str = Field(
        default="",
        description="Status of the incident service",
    )
    quality_manager_status: str = Field(
        default="HEALTHY",
        description="Status of the quality manager",
    )
    compliance_manager_status: str = Field(
        default="HEALTHY",
        description="Status of the compliance manager",
    )
    diagnostics_status: str = Field(
        default="HEALTHY",
        description="Status of the diagnostics system",
    )
    audit_status: str = Field(
        default="HEALTHY",
        description="Status of the audit system",
    )
    export_status: str = Field(
        default="HEALTHY",
        description="Status of the export system",
    )
    pipeline_version_status: str = Field(
        default="HEALTHY",
        description="Status of the pipeline version manager",
    )
    total_assets: int = Field(
        default=0,
        ge=0,
        description="Total number of managed assets",
    )
    active_alarms: int = Field(
        default=0,
        ge=0,
        description="Number of currently active alarms",
    )
    open_incidents: int = Field(
        default=0,
        ge=0,
        description="Number of open incidents",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )
