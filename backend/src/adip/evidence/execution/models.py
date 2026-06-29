"""Execution-layer models for the Evidence Fusion Engine Phase 2.

Defines intermediate data structures used within the execution pipeline
that are not part of the public domain model API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.evidence.enums import (
    BundleType,
    EvidenceDomain,
    EvidenceType,
)


class CorrelationResult(BaseModel):
    """Result of correlating evidence items."""

    correlation_id: str = Field(default="", description="Unique correlation identifier")
    source_evidence_id: UUID4 = Field(description="The source evidence ID")
    correlated_evidence_ids: list[UUID4] = Field(
        default_factory=list, description="Evidence IDs this was correlated with",
    )
    source_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Source agreement score")
    temporal_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Temporal consistency score")
    domain_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Domain consistency score")
    entity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Entity match score")
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall correlation score")


class ConflictReport(BaseModel):
    """Report of conflicts detected between evidence items."""

    report_id: str = Field(default="", description="Unique report identifier")
    contradictory_pairs: list[tuple[UUID4, UUID4]] = Field(
        default_factory=list, description="Pairs of contradictory evidence IDs",
    )
    duplicate_pairs: list[tuple[UUID4, UUID4]] = Field(
        default_factory=list, description="Pairs of duplicate evidence IDs",
    )
    missing_evidence_ids: list[UUID4] = Field(
        default_factory=list, description="Evidence IDs that are missing expected counterparts",
    )
    stale_evidence_ids: list[UUID4] = Field(
        default_factory=list, description="Evidence IDs that are stale",
    )
    has_conflicts: bool = Field(default=False, description="Whether any conflicts were detected")
    conflict_count: int = Field(default=0, ge=0, description="Total number of conflicts")


class TrustScore(BaseModel):
    """Trust score for a piece of evidence or source."""

    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall trust score")
    source_reliability: float = Field(default=0.0, ge=0.0, le=1.0, description="Source reliability component")
    historical_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Historical accuracy component")
    validation_status: float = Field(default=0.0, ge=0.0, le=1.0, description="Validation status component")
    provenance: float = Field(default=0.0, ge=0.0, le=1.0, description="Provenance completeness component")


class EvidenceBundle(BaseModel):
    """A bundle of evidence grouped by a common entity."""

    bundle_id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique bundle identifier")
    bundle_type: BundleType = Field(default=BundleType.INCIDENT, description="Type of bundle grouping")
    entity_id: str = Field(default="", description="ID of the entity this bundle relates to")
    evidence_ids: list[UUID4] = Field(default_factory=list, description="Evidence IDs in this bundle")
    title: str = Field(default="", description="Human-readable bundle title")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Bundle confidence score")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the bundle was created")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional bundle metadata")


class TimelineEntry(BaseModel):
    """A single entry in an evidence timeline."""

    entry_id: str = Field(default="", description="Unique entry identifier")
    evidence_id: UUID4 = Field(description="The evidence this entry relates to")
    event_time: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the event occurred")
    collection_time: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the evidence was collected")
    processing_time: datetime | None = Field(default=None, description="When the evidence was processed")
    version_time: datetime | None = Field(default=None, description="Version timestamp of the evidence")
    evidence_type: EvidenceType = Field(default=EvidenceType.KNOWLEDGE, description="Type of evidence")
    domain: EvidenceDomain = Field(default=EvidenceDomain.SYSTEM, description="Domain of the evidence")
    label: str = Field(default="", description="Human-readable label for this entry")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional entry metadata")


class Timeline(BaseModel):
    """Chronological timeline of evidence events."""

    timeline_id: str = Field(default="", description="Unique timeline identifier")
    entries: list[TimelineEntry] = Field(default_factory=list, description="Timeline entries in chronological order")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the timeline was created")


class FreshnessThreshold(BaseModel):
    """Freshness threshold configuration for an evidence type."""

    evidence_type: EvidenceType = Field(default=EvidenceType.KNOWLEDGE, description="Evidence type this threshold applies to")
    max_age_seconds: float = Field(default=3600.0, ge=0.0, description="Maximum age in seconds before evidence is stale")


class SourceReliability(BaseModel):
    """Reliability metadata for an evidence source."""

    source_id: str = Field(default="", description="Source identifier")
    source_type: str = Field(default="", description="Type of source")
    reliability_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Base reliability score")
    historical_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Historical accuracy rate")
    validation_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Validation success rate")
    ranking: int = Field(default=0, ge=0, description="Source ranking (lower = more reliable)")


class CorrelationScore(BaseModel):
    """Detailed correlation score between two evidence items."""

    source_agreement: float = Field(default=0.0, ge=0.0, le=1.0, description="Agreement between sources")
    temporal_consistency: float = Field(default=0.0, ge=0.0, le=1.0, description="Temporal consistency")
    domain_consistency: float = Field(default=0.0, ge=0.0, le=1.0, description="Domain consistency")
    entity_match: float = Field(default=0.0, ge=0.0, le=1.0, description="Entity match score")
    overall: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall correlation score")


class TraceRecord(BaseModel):
    """Trace record for a single pipeline stage."""

    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique trace identifier")
    stage_name: str = Field(default="", description="Name of the pipeline stage")
    operation: str = Field(default="", description="Operation being performed")
    evidence_id: str = Field(default="", description="Evidence ID being processed")
    correlation_id: str = Field(default="", description="Correlation ID for distributed tracing")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the stage started")
    completed_at: datetime | None = Field(default=None, description="When the stage completed")
    duration_ms: float | None = Field(default=None, ge=0.0, description="Stage duration in milliseconds")
    success: bool = Field(default=True, description="Whether the stage completed successfully")
    warnings: list[str] = Field(default_factory=list, description="Stage warnings")
    errors: list[str] = Field(default_factory=list, description="Stage errors")
