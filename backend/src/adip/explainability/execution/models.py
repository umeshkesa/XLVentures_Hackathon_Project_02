"""Execution-layer models for the Explainability Engine Phase 2.

Internal models used by execution components during explanation
pipeline processing. Not part of the public API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ExplanationSection(BaseModel):
    """A single section within an explanation."""

    section_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique section identifier",
    )
    section_type: str = Field(default="", description="Type of section (summary, evidence, etc.)")
    title: str = Field(default="", description="Section title")
    content: str = Field(default="", description="Section content body")
    order: int = Field(default=0, ge=0, description="Section order in the explanation")
    audience: str = Field(default="", description="Target audience for this section")
    citations: list[str] = Field(default_factory=list, description="Citation IDs associated with this section")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional section metadata")


class TimelineEvent(BaseModel):
    """A single event within an explanation timeline."""

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event identifier",
    )
    event_type: str = Field(default="", description="Type of timeline event")
    description: str = Field(default="", description="Event description")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")


class ExplanationTimeline(BaseModel):
    """Chronological timeline of explanation events."""

    timeline_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique timeline identifier",
    )
    explanation_id: str = Field(default="", description="The explanation this timeline belongs to")
    events: list[dict[str, Any]] = Field(default_factory=list, description="Timeline events")
    start_time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the timeline started",
    )
    end_time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the timeline ended",
    )
    total_duration_ms: float = Field(default=0.0, ge=0.0, description="Total duration in milliseconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional timeline metadata")


class SectionContent(BaseModel):
    """Content for a specific section type."""

    content_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique content identifier",
    )
    section_type: str = Field(default="", description="Type of section content")
    summary: str = Field(default="", description="Section summary")
    details: str = Field(default="", description="Detailed section content")
    key_points: list[str] = Field(default_factory=list, description="Key points in this section")
    audience: str = Field(default="", description="Target audience for this content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional content metadata")


class AudienceFormat(BaseModel):
    """Format configuration for a specific audience."""

    format_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique format identifier",
    )
    audience: str = Field(default="", description="Target audience identifier")
    template_name: str = Field(default="", description="Template name for this audience")
    detail_level: str = Field(default="", description="Level of detail (high, medium, low)")
    technical_depth: float = Field(default=0.5, ge=0.0, le=1.0, description="Technical depth (0.0-1.0)")
    format_preferences: dict[str, Any] = Field(default_factory=dict, description="Format preferences")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional format metadata")


class NarrativeTemplate(BaseModel):
    """A predefined narrative template."""

    template_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique template identifier",
    )
    template_type: str = Field(
        default="",
        description="Template type (executive, technical, audit, incident, compliance)",
    )
    name: str = Field(default="", description="Template name")
    description: str = Field(default="", description="Template description")
    sections: list[str] = Field(default_factory=list, description="Ordered section types for this template")
    audience: str = Field(default="", description="Target audience for this template")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional template metadata")


class PolicyRule(BaseModel):
    """A policy rule governing explanation generation."""

    rule_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique rule identifier",
    )
    policy_type: str = Field(
        default="",
        description="Policy type (SUMMARY, STANDARD, FULL, AUDIT, CONFIDENTIAL)",
    )
    name: str = Field(default="", description="Policy name")
    allowed_audiences: list[str] = Field(default_factory=list, description="Audiences allowed by this policy")
    max_narratives: int = Field(default=10, ge=1, description="Maximum number of narratives allowed")
    require_citations: bool = Field(default=False, description="Whether citations are required")
    require_trace: bool = Field(default=False, description="Whether trace is required")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional rule metadata")


class QualityScore(BaseModel):
    """Quality assessment scores for an explanation."""

    score_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique score identifier",
    )
    completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Completeness score (0.0-1.0)")
    citation_coverage: float = Field(default=0.0, ge=0.0, le=1.0, description="Citation coverage score (0.0-1.0)")
    trace_coverage: float = Field(default=0.0, ge=0.0, le=1.0, description="Trace coverage score (0.0-1.0)")
    readability: float = Field(default=0.0, ge=0.0, le=1.0, description="Readability score (0.0-1.0)")
    consistency: float = Field(default=0.0, ge=0.0, le=1.0, description="Consistency score (0.0-1.0)")
    overall: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality score (0.0-1.0)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional score metadata")


class TraceRecord(BaseModel):
    """A single trace record for an explanation pipeline stage."""

    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique trace record identifier",
    )
    stage_name: str = Field(default="", description="Name of the pipeline stage")
    operation: str = Field(default="", description="The operation being traced")
    explanation_id: str = Field(default="", description="The explanation ID associated with this trace")
    correlation_id: str = Field(default="", description="Correlation ID for distributed tracing")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage started",
    )
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage completed",
    )
    duration_ms: float | None = Field(default=None, ge=0.0, description="Stage duration in milliseconds")
    success: bool = Field(default=True, description="Whether the stage completed successfully")
    warnings: list[str] = Field(default_factory=list, description="Warnings generated during this stage")
    errors: list[str] = Field(default_factory=list, description="Errors generated during this stage")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")


class ExplainabilityMetrics(BaseModel):
    """Aggregated metrics for the explainability engine."""

    metrics_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique metrics identifier",
    )
    explanations_total: int = Field(default=0, ge=0, description="Total explanations generated")
    narratives_total: int = Field(default=0, ge=0, description="Total narratives generated")
    citations_total: int = Field(default=0, ge=0, description="Total citations generated")
    audience_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Explanation count per audience",
    )
    template_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Template usage count per template type",
    )
    average_quality: float = Field(default=0.0, ge=0.0, le=1.0, description="Average quality score")
    average_completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Average completeness score")
    reviews_total: int = Field(default=0, ge=0, description="Total reviews performed")
    versions_total: int = Field(default=0, ge=0, description="Total versions created")
    readiness_by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Readiness assessment count per status",
    )
    lineage_entries_total: int = Field(default=0, ge=0, description="Total lineage entries recorded")
    snapshots_total: int = Field(default=0, ge=0, description="Total snapshots created")
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Average confidence score")
    compliance_total: int = Field(default=0, ge=0, description="Total compliance checks performed")
    readiness_ready: int = Field(default=0, ge=0, description="Total readiness assessments marked READY")
    readiness_review: int = Field(default=0, ge=0, description="Total readiness assessments marked REVIEW_REQUIRED")
    readiness_incomplete: int = Field(default=0, ge=0, description="Total readiness assessments marked INCOMPLETE")
    readiness_non_compliant: int = Field(default=0, ge=0, description="Total readiness assessments marked NON_COMPLIANT")
    audits_total: int = Field(default=0, ge=0, description="Total audits performed")
    exports_total: int = Field(default=0, ge=0, description="Total exports generated")
    justifications_total: int = Field(default=0, ge=0, description="Total justifications created")
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When metrics were collected",
    )
