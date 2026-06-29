"""Execution-layer models for the Energy Domain Phase 2.

Internal processing models for asset graphs, lifecycle states,
sensor validation, health scores, alarm correlation, maintenance
scheduling, topology, event timelines, trace, and metrics.
Not exposed through the public EnergyDomainService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import UUID4, BaseModel, Field
from pydantic.types import UUID as PydanticUUID

from adip.energy.enums import AlarmSeverity, AssetType, MaintenanceType


class AssetLifecycleState(StrEnum):
    """Lifecycle state of an energy asset.

    Values:
    - PLANNED: Asset is planned but not yet installed
    - COMMISSIONED: Asset has been commissioned and is being tested
    - OPERATIONAL: Asset is fully operational
    - MAINTENANCE: Asset is under maintenance
    - RETIRED: Asset has been retired from service
    """

    PLANNED = "PLANNED"
    COMMISSIONED = "COMMISSIONED"
    OPERATIONAL = "OPERATIONAL"
    MAINTENANCE = "MAINTENANCE"
    RETIRED = "RETIRED"


class AssetNode(BaseModel):
    """A node in the energy asset graph."""

    node_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique node identifier",
    )
    asset_id: PydanticUUID = Field(
        description="The asset this node represents",
    )
    asset_name: str = Field(
        default="",
        description="Human-readable asset name",
    )
    asset_type: AssetType = Field(
        description="Type of energy asset",
    )
    level: int = Field(
        default=0,
        ge=0,
        description="Hierarchical level in the graph (0 = root)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional node metadata",
    )


class AssetEdge(BaseModel):
    """A directed edge in the energy asset graph."""

    edge_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique edge identifier",
    )
    source_asset_id: PydanticUUID = Field(
        description="Source asset identifier",
    )
    target_asset_id: PydanticUUID = Field(
        description="Target asset identifier",
    )
    relationship_type: str = Field(
        default="connects_to",
        description="Type of relationship",
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relationship weight",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional edge metadata",
    )


class AssetGraphModel(BaseModel):
    """Complete asset graph with nodes, edges, and topology analysis."""

    graph_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique graph identifier",
    )
    nodes: list[AssetNode] = Field(
        default_factory=list,
        description="Nodes in the graph",
    )
    edges: list[AssetEdge] = Field(
        default_factory=list,
        description="Edges in the graph",
    )
    has_cycle: bool = Field(
        default=False,
        description="Whether the graph contains a cycle",
    )
    topological_order: list[PydanticUUID] = Field(
        default_factory=list,
        description="Topologically sorted asset IDs",
    )
    root_nodes: list[PydanticUUID] = Field(
        default_factory=list,
        description="Root nodes (no incoming edges)",
    )
    leaf_nodes: list[PydanticUUID] = Field(
        default_factory=list,
        description="Leaf nodes (no outgoing edges)",
    )


class LifecycleTransition(BaseModel):
    """A recorded lifecycle state transition for an asset."""

    transition_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique transition identifier",
    )
    asset_id: PydanticUUID = Field(
        description="The asset that transitioned",
    )
    from_state: AssetLifecycleState = Field(
        description="Previous lifecycle state",
    )
    to_state: AssetLifecycleState = Field(
        description="New lifecycle state",
    )
    reason: str = Field(
        default="",
        description="Reason for the transition",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the transition occurred",
    )


class ValidationResult(BaseModel):
    """Result of validating a sensor reading."""

    is_valid: bool = Field(
        default=True,
        description="Whether the reading is valid",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Validation issues found",
    )
    normalized_value: float = Field(
        default=0.0,
        description="Normalized value after unit conversion",
    )
    normalized_unit: str = Field(
        default="",
        description="Normalized unit after conversion",
    )


class HealthScoreResult(BaseModel):
    """Calculated health score for an energy asset."""

    asset_id: PydanticUUID = Field(
        description="The asset this health score applies to",
    )
    overall_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall health score (0.0 = critical, 1.0 = perfect)",
    )
    sensor_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Health score contribution from sensor readings",
    )
    maintenance_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Health score contribution from maintenance history",
    )
    age_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Health score contribution from asset age",
    )
    alarm_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Health score contribution from alarm history",
    )


class CorrelationGroup(BaseModel):
    """A group of correlated alarms that may form an incident."""

    group_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique correlation group identifier",
    )
    alarm_ids: list[PydanticUUID] = Field(
        default_factory=list,
        description="Alarm IDs in this correlation group",
    )
    asset_ids: list[PydanticUUID] = Field(
        default_factory=list,
        description="Asset IDs involved in this group",
    )
    highest_severity: AlarmSeverity = Field(
        default=AlarmSeverity.INFO,
        description="Highest severity among grouped alarms",
    )
    correlation_reason: str = Field(
        default="",
        description="Reason these alarms were correlated",
    )
    incident_id: PydanticUUID | None = Field(
        default=None,
        description="Incident ID if an incident was created from this group",
    )


class MaintenanceSchedule(BaseModel):
    """A scheduled maintenance activity for an asset."""

    schedule_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique schedule identifier",
    )
    asset_id: PydanticUUID = Field(
        description="The asset scheduled for maintenance",
    )
    maintenance_type: MaintenanceType = Field(
        description="Type of maintenance scheduled",
    )
    due_date: datetime = Field(
        description="When the maintenance is due",
    )
    priority: str = Field(
        default="normal",
        description="Schedule priority (high, normal, low)",
    )
    description: str = Field(
        default="",
        description="Description of the scheduled maintenance",
    )


class TopologyResult(BaseModel):
    """Topology information for an energy asset."""

    asset_id: PydanticUUID = Field(
        description="The asset this topology describes",
    )
    upstream: list[PydanticUUID] = Field(
        default_factory=list,
        description="Upstream asset IDs (towards source)",
    )
    downstream: list[PydanticUUID] = Field(
        default_factory=list,
        description="Downstream asset IDs (towards load)",
    )
    connected: list[PydanticUUID] = Field(
        default_factory=list,
        description="Directly connected asset IDs",
    )
    neighbors: list[PydanticUUID] = Field(
        default_factory=list,
        description="Neighboring asset IDs (same level)",
    )


class TimelineEntry(BaseModel):
    """A single event in the energy event timeline."""

    entry_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique timeline entry identifier",
    )
    asset_id: PydanticUUID = Field(
        description="The asset this event relates to",
    )
    event_type: str = Field(
        description="Type of event (sensor_update, alarm, incident, maintenance, recovery)",
    )
    description: str = Field(
        default="",
        description="Description of the event",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )


class DomainTraceRecord(BaseModel):
    """A single trace entry for domain observability."""

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    domain: str = Field(
        default="energy",
        description="Domain name for this trace",
    )
    entity_id: str = Field(
        default="",
        description="ID of the entity being traced",
    )
    entity_type: str = Field(
        default="",
        description="Type of entity (asset, sensor, alarm, incident, maintenance)",
    )
    operation: str = Field(
        default="",
        description="Operation being performed",
    )
    details: str = Field(
        default="",
        description="Details about the trace entry",
    )
    success: bool = Field(
        default=True,
        description="Whether the operation succeeded",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the trace was recorded",
    )


class DomainMetricsSnapshot(BaseModel):
    """Snapshot of energy domain metrics at a point in time."""

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    asset_count: int = Field(
        default=0,
        ge=0,
        description="Total number of registered assets",
    )
    sensor_count: int = Field(
        default=0,
        ge=0,
        description="Total number of sensors",
    )
    alarm_count: int = Field(
        default=0,
        ge=0,
        description="Total number of alarms",
    )
    incident_count: int = Field(
        default=0,
        ge=0,
        description="Total number of incidents",
    )
    maintenance_count: int = Field(
        default=0,
        ge=0,
        description="Total number of maintenance activities",
    )
    average_health_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average health score across all assets",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was taken",
    )


class ClassificationResult(BaseModel):
    """Result of classifying an energy asset."""

    asset_id: PydanticUUID = Field(
        description="The classified asset",
    )
    asset_type: AssetType = Field(
        description="Type of the asset",
    )
    classification: str = Field(
        default="",
        description="Equipment classification (generation, transmission, distribution, consumption, storage)",
    )
    category: str = Field(
        default="",
        description="Detailed category within the classification",
    )


class ConversionRequest(BaseModel):
    """A unit conversion request."""

    value: float = Field(
        description="The value to convert",
    )
    from_unit: str = Field(
        description="Source unit",
    )
    to_unit: str = Field(
        description="Target unit",
    )
    conversion_type: str = Field(
        description="Type of conversion (temperature, voltage, current, power, frequency, pressure)",
    )


class ConversionResult(BaseModel):
    """Result of a unit conversion."""

    input_value: float = Field(
        description="The original input value",
    )
    output_value: float = Field(
        description="The converted value",
    )
    from_unit: str = Field(
        description="Source unit",
    )
    to_unit: str = Field(
        description="Target unit",
    )
    conversion_type: str = Field(
        description="Type of conversion performed",
    )
