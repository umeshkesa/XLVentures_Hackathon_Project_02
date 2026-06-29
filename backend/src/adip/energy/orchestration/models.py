"""Orchestration-layer models for the Energy Domain Phase 3.5.

Enterprise orchestration models for sessions, decisions,
explainability, readiness, versioning, lineage, snapshots,
quality, compliance, diagnostics, audit packages, export
profiles, and pipeline versions. Not exposed through the
public API directly.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID as PydanticUUID
from pydantic.types import UUID4


class EnergySession(BaseModel):
    """Session tracking for energy domain operations."""

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    asset_id: PydanticUUID = Field(
        description="The primary asset for this session",
    )
    domain: str = Field(
        default="ELECTRICITY",
        description="Energy domain for this session",
    )
    status: str = Field(
        default="INITIALIZED",
        description="Session status: INITIALIZED, ACTIVE, COMPLETED, FAILED",
    )
    operation: str = Field(
        default="",
        description="Operation being performed",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session completed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )


class EnergyDecision(BaseModel):
    """Decision produced by an energy domain operation.

    Enhanced in Phase 3.5 with: asset_context, health, readiness,
    quality_score, compliance_status, diagnostics, portfolio_summary.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    session_id: UUID4 = Field(
        description="The session that produced this decision",
    )
    asset_id: PydanticUUID = Field(
        description="The asset this decision relates to",
    )
    asset_context: str = Field(
        default="",
        description="Detailed asset context at decision time",
    )
    health: dict[str, Any] = Field(
        default_factory=dict,
        description="Asset health details at decision time",
    )
    readiness: dict[str, Any] = Field(
        default_factory=dict,
        description="Readiness assessment details",
    )
    context_summary: str = Field(
        default="",
        description="Summary of the asset context at decision time",
    )
    health_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Asset health score at decision time",
    )
    readiness_status: str = Field(
        default="",
        description="Readiness status at decision time",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Domain quality score at decision time",
    )
    compliance_status: str = Field(
        default="",
        description="Compliance status at decision time",
    )
    diagnostics: dict[str, Any] = Field(
        default_factory=dict,
        description="Diagnostics collected at decision time",
    )
    portfolio_summary: str = Field(
        default="",
        description="Summary of portfolio analysis",
    )
    decisions: list[str] = Field(
        default_factory=list,
        description="List of decisions or recommendations made",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the decision",
    )
    explainability: dict[str, Any] = Field(
        default_factory=dict,
        description="Explainability metadata for the decision",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )


class EnergyExplainabilityMetadata(BaseModel):
    """Explainability metadata for energy domain operations.

    Enhanced in Phase 3.5 with: why_quality_assessed,
    why_compliance_checked, why_compliance_failed, why_diagnostic.
    """

    why_asset_selected: str = Field(
        default="",
        description="Why this asset was selected for the operation",
    )
    why_sensor_used: str = Field(
        default="",
        description="Why specific sensors were used for analysis",
    )
    why_alarm_raised: str = Field(
        default="",
        description="Why an alarm was raised",
    )
    why_maintenance_scheduled: str = Field(
        default="",
        description="Why maintenance was scheduled",
    )
    why_health_assessed: str = Field(
        default="",
        description="Why the health assessment produced its result",
    )
    why_incident_created: str = Field(
        default="",
        description="Why an incident was created",
    )
    why_quality_assessed: str = Field(
        default="",
        description="Why the quality assessment produced its result",
    )
    why_compliance_checked: str = Field(
        default="",
        description="Why compliance was checked",
    )
    why_compliance_failed: str = Field(
        default="",
        description="Why compliance validation failed",
    )
    why_diagnostic: str = Field(
        default="",
        description="Why diagnostics were collected",
    )


class EnergyReadiness(BaseModel):
    """Readiness assessment for an energy domain operation."""

    readiness_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique readiness identifier",
    )
    asset_id: PydanticUUID = Field(
        description="The asset this readiness applies to",
    )
    status: str = Field(
        default="PENDING",
        description="Readiness status: READY, PENDING, BLOCKED, NOT_READY",
    )
    checks: dict[str, bool] = Field(
        default_factory=dict,
        description="Individual readiness checks and their pass/fail status",
    )
    reason: str = Field(
        default="",
        description="Reason for the readiness status",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the readiness was assessed",
    )


class EnergyReadinessReport(BaseModel):
    """Operational readiness summary report.

    Generated from readiness assessments across multiple
    dimensions, providing a comprehensive view of asset
    operational readiness.
    """

    report_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique report identifier",
    )
    asset_id: str = Field(
        description="The asset this report applies to",
    )
    overall_status: str = Field(
        default="PENDING",
        description="Overall readiness status: READY, PENDING, BLOCKED, NOT_READY",
    )
    health_ok: bool = Field(default=True, description="Whether health checks pass")
    sensors_active: bool = Field(default=True, description="Whether required sensors are active")
    no_critical_alarms: bool = Field(default=True, description="Whether no critical alarms exist")
    maintenance_current: bool = Field(default=True, description="Whether maintenance is current")
    topology_ok: bool = Field(default=True, description="Whether topology is valid")
    quality_ok: bool = Field(default=True, description="Whether quality checks pass")
    compliance_ok: bool = Field(default=True, description="Whether compliance checks pass")
    score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall readiness score",
    )
    summary: str = Field(
        default="",
        description="Human-readable readiness summary",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the report was generated",
    )


class EnergyDiagnostics(BaseModel):
    """Diagnostics collected for an energy domain operation.

    Captures sensor issues, health issues, topology issues,
    policy violations, and maintenance issues in a structured
    format.
    """

    diagnostics_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique diagnostics identifier",
    )
    asset_id: str = Field(
        description="The asset this diagnostics applies to",
    )
    sensor_issues: list[str] = Field(
        default_factory=list,
        description="Issues detected with sensors",
    )
    health_issues: list[str] = Field(
        default_factory=list,
        description="Issues detected with health",
    )
    topology_issues: list[str] = Field(
        default_factory=list,
        description="Issues detected with topology",
    )
    policy_violations: list[str] = Field(
        default_factory=list,
        description="Policy violations detected",
    )
    maintenance_issues: list[str] = Field(
        default_factory=list,
        description="Issues detected with maintenance",
    )
    total_issues: int = Field(
        default=0,
        ge=0,
        description="Total number of issues detected",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When diagnostics were collected",
    )


class EnergyQualityReport(BaseModel):
    """Quality assessment report for an energy domain entity.

    Evaluates asset completeness, sensor coverage, topology
    integrity, maintenance coverage, and overall quality.
    """

    quality_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique quality identifier",
    )
    asset_id: str = Field(
        description="The asset this quality report applies to",
    )
    asset_completeness: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Completeness of asset data (0.0 to 1.0)",
    )
    sensor_coverage: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Coverage of sensor data (0.0 to 1.0)",
    )
    topology_integrity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Integrity of topology (0.0 to 1.0)",
    )
    maintenance_coverage: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Coverage of maintenance records (0.0 to 1.0)",
    )
    overall_quality: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall domain quality score (0.0 to 1.0)",
    )
    summary: str = Field(
        default="",
        description="Human-readable quality summary",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the quality was assessed",
    )


class EnergyComplianceReport(BaseModel):
    """Compliance validation report.

    Validates safety rules, maintenance policies, operational
    constraints, inspection rules, and regulatory rules.
    """

    compliance_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique compliance identifier",
    )
    asset_id: str = Field(
        description="The asset this compliance report applies to",
    )
    status: str = Field(
        default="COMPLIANT",
        description="Overall compliance status: COMPLIANT, NON_COMPLIANT, PENDING",
    )
    safety_rules: list[str] = Field(
        default_factory=list,
        description="Safety rule checks and their results",
    )
    maintenance_policies: list[str] = Field(
        default_factory=list,
        description="Maintenance policy checks and their results",
    )
    operational_constraints: list[str] = Field(
        default_factory=list,
        description="Operational constraint checks and their results",
    )
    inspection_rules: list[str] = Field(
        default_factory=list,
        description="Inspection rule checks and their results",
    )
    regulatory_rules: list[str] = Field(
        default_factory=list,
        description="Regulatory rule checks and their results",
    )
    violations: list[str] = Field(
        default_factory=list,
        description="List of compliance violations detected",
    )
    summary: str = Field(
        default="",
        description="Human-readable compliance summary",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When compliance was validated",
    )


class EnergyAuditPackage(BaseModel):
    """Immutable audit package for energy domain operations.

    Contains a complete snapshot of asset, digital twin,
    sensors, maintenance, incidents, timeline, and metadata
    for auditing purposes.
    """

    audit_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique audit identifier",
    )
    asset_id: str = Field(
        description="The asset this audit package applies to",
    )
    asset_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of asset data",
    )
    digital_twin_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of digital twin data",
    )
    sensor_snapshot: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Snapshot of sensor data",
    )
    maintenance_snapshot: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Snapshot of maintenance data",
    )
    incident_snapshot: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Snapshot of incident data",
    )
    timeline_snapshot: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Snapshot of event timeline",
    )
    metadata_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of metadata",
    )
    hash: str = Field(
        default="",
        description="Hash of the audit package contents for integrity",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the audit package was created",
    )


class EnergyExportProfile(BaseModel):
    """Export profile for energy domain data.

    Supports REST, Dashboard, Analytics, Audit, JSON, CSV
    formats with profile-specific configuration.
    """

    profile_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique profile identifier",
    )
    name: str = Field(
        description="Profile name (REST, Dashboard, Analytics, Audit, JSON, CSV)",
    )
    format: str = Field(
        default="json",
        description="Export format",
    )
    fields: list[str] = Field(
        default_factory=list,
        description="Fields to include in the export",
    )
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Profile-specific configuration",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the profile was created",
    )


class PortfolioQuality(BaseModel):
    """Quality assessment for a portfolio of assets.

    Evaluates quality at region, plant, utility, and fleet
    levels.
    """

    portfolio_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique portfolio identifier",
    )
    name: str = Field(
        description="Portfolio name",
    )
    level: str = Field(
        description="Portfolio level (region, plant, utility, fleet)",
    )
    asset_count: int = Field(
        default=0,
        ge=0,
        description="Number of assets in the portfolio",
    )
    average_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average quality score across the portfolio",
    )
    average_health: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average health score across the portfolio",
    )
    average_compliance: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Average compliance score across the portfolio",
    )
    risk_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall risk score for the portfolio",
    )
    summary: str = Field(
        default="",
        description="Human-readable portfolio quality summary",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the portfolio quality was assessed",
    )


class DomainPipelineVersion(BaseModel):
    """Pipeline version tracking for the energy domain.

    Supports version creation, active version tracking,
    and version history.
    """

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version identifier",
    )
    pipeline_name: str = Field(
        description="Name of the pipeline being versioned",
    )
    version_number: int = Field(
        default=1,
        ge=1,
        description="Pipeline version number",
    )
    is_active: bool = Field(
        default=False,
        description="Whether this is the active pipeline version",
    )
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline configuration for this version",
    )
    change_description: str = Field(
        default="",
        description="Description of changes in this version",
    )
    created_by: str = Field(
        default="system",
        description="Who or what created this version",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the version was created",
    )


class EnergyVersionRecord(BaseModel):
    """Version record for an energy domain entity."""

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version identifier",
    )
    entity_id: str = Field(
        description="ID of the entity being versioned",
    )
    entity_type: str = Field(
        description="Type of entity (asset, sensor, decision, configuration)",
    )
    version_number: int = Field(
        default=1,
        ge=1,
        description="Version number",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Versioned data snapshot",
    )
    created_by: str = Field(
        default="system",
        description="Who or what created this version",
    )
    change_description: str = Field(
        default="",
        description="Description of changes in this version",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the version was created",
    )


class EnergyLineageModel(BaseModel):
    """Lineage record for an energy domain entity."""

    lineage_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique lineage identifier",
    )
    entity_id: str = Field(
        description="ID of the entity this lineage tracks",
    )
    entity_type: str = Field(
        description="Type of entity",
    )
    parent_ids: list[str] = Field(
        default_factory=list,
        description="IDs of parent/source entities",
    )
    operations: list[str] = Field(
        default_factory=list,
        description="List of operations performed in order",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the lineage was recorded",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional lineage metadata",
    )


class EnergySnapshotModel(BaseModel):
    """Immutable point-in-time snapshot for an energy entity.

    Enhanced in Phase 3.5 to support quality, compliance,
    diagnostics, audit, and export snapshot types.
    """

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    entity_id: str = Field(
        description="ID of the entity being snapshotted",
    )
    entity_type: str = Field(
        description="Type of entity",
    )
    snapshot_type: str = Field(
        default="state",
        description="Type of snapshot (state, decision, health, configuration, quality, compliance, diagnostics, audit, export)",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot data",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was taken",
    )
