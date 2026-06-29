"""Domain models for the Evidence Fusion Engine.

Defines all data models used across the evidence pipeline including
evidence items, sources, packages, graphs, quality assessments,
provenance tracking, health, metrics, sessions, and decisions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.evidence.enums import (
    EvidenceDomain,
    EvidenceStatus,
    EvidenceType,
)

# ─────────────────────────────────────────────────────────────────────────────
# EvidenceSource
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceSource(BaseModel):
    """Source origin for evidence.

    Tracks where evidence originated, including the source system,
    the manager that collected it, and the version of the source.
    """

    source_id: str = Field(
        default="",
        description="Unique identifier for the source",
    )
    source_type: str = Field(
        default="",
        description="Type of the source system (knowledge, memory, rule, etc.)",
    )
    manager: str = Field(
        default="",
        description="Manager component that collected the evidence",
    )
    version: str = Field(
        default="",
        description="Version of the source or manager",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceMetadata
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceMetadata(BaseModel):
    """Metadata describing evidence content.

    Provides descriptive information about evidence for search,
    filtering, and explainability purposes.
    """

    title: str = Field(
        default="",
        description="Human-readable title for the evidence",
    )
    description: str = Field(
        default="",
        description="Detailed description of the evidence",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorising and filtering evidence",
    )
    category: str = Field(
        default="",
        description="Category classification for the evidence",
    )
    source: str = Field(
        default="",
        description="Original source description",
    )
    additional: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata key-value pairs",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceProvenance
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceProvenance(BaseModel):
    """Provenance tracking for evidence.

    Tracks the origin, ownership, and retrieval details of evidence
    to support auditability and explainability.
    """

    source: str = Field(
        default="",
        description="Original source system or service",
    )
    source_type: str = Field(
        default="",
        description="Type of the source (service, sensor, system, etc.)",
    )
    manager: str = Field(
        default="",
        description="Manager component responsible for retrieval",
    )
    version: str = Field(
        default="",
        description="Version of the evidence or source",
    )
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the evidence was retrieved",
    )
    owner: str = Field(
        default="",
        description="Owner or creator of the evidence",
    )
    original_identifier: str = Field(
        default="",
        description="Original identifier in the source system",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceQuality
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceQuality(BaseModel):
    """Quality assessment for evidence.

    Evaluates evidence quality across multiple dimensions:
    freshness, completeness, consistency, and reliability.
    All scores are between 0.0 and 1.0.
    """

    freshness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How recent the evidence is (0.0–1.0)",
    )
    completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How complete the evidence data is (0.0–1.0)",
    )
    consistency: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How consistent the evidence is with other sources (0.0–1.0)",
    )
    reliability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How reliable the evidence source is (0.0–1.0)",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall quality score (0.0–1.0)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Evidence
# ─────────────────────────────────────────────────────────────────────────────


class Evidence(BaseModel):
    """Core evidence item representing a single piece of evidence.

    Each evidence item carries type, domain, status, source,
    provenance, quality, and payload information. Evidence flows
    through the pipeline from COLLECTED to READY status.
    """

    evidence_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique evidence identifier",
    )
    evidence_type: EvidenceType = Field(
        default=EvidenceType.KNOWLEDGE,
        description="Type of evidence",
    )
    domain: EvidenceDomain = Field(
        default=EvidenceDomain.SYSTEM,
        description="Domain this evidence belongs to",
    )
    status: EvidenceStatus = Field(
        default=EvidenceStatus.COLLECTED,
        description="Current processing status",
    )
    source: EvidenceSource = Field(
        default_factory=EvidenceSource,
        description="Source origin of the evidence",
    )
    metadata: EvidenceMetadata = Field(
        default_factory=EvidenceMetadata,
        description="Descriptive metadata for the evidence",
    )
    provenance: EvidenceProvenance = Field(
        default_factory=EvidenceProvenance,
        description="Provenance tracking information",
    )
    quality: EvidenceQuality = Field(
        default_factory=EvidenceQuality,
        description="Quality assessment of the evidence",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="The actual evidence data payload",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this evidence was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceNode
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceNode(BaseModel):
    """A node in the evidence graph representing a piece of evidence.

    Nodes wrap evidence items with graph-specific metadata for
    positioning and relationship tracking.
    """

    node_id: str = Field(
        default="",
        description="Unique identifier for the node in the graph",
    )
    evidence_id: UUID4 = Field(
        description="Reference to the evidence this node represents",
    )
    evidence_type: EvidenceType = Field(
        default=EvidenceType.KNOWLEDGE,
        description="Type of evidence at this node",
    )
    domain: EvidenceDomain = Field(
        default=EvidenceDomain.SYSTEM,
        description="Domain of the evidence at this node",
    )
    label: str = Field(
        default="",
        description="Human-readable label for the node",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional node metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceEdge
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceEdge(BaseModel):
    """A directed edge in the evidence graph.

    Represents a relationship between two evidence nodes with
    a type, weight, and optional metadata.
    """

    edge_id: str = Field(
        default="",
        description="Unique identifier for the edge in the graph",
    )
    source_node_id: str = Field(
        default="",
        description="Node ID of the source evidence",
    )
    target_node_id: str = Field(
        default="",
        description="Node ID of the target evidence",
    )
    relationship: str = Field(
        default="",
        description="Type of relationship (supports, contradicts, correlates, etc.)",
    )
    weight: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Strength of the relationship (0.0–1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional edge metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceGraph
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceGraph(BaseModel):
    """Graph representation of evidence relationships.

    Contains nodes and edges that represent evidence items and
    their relationships. Provides a structural view of how
    evidence items relate to each other.
    """

    nodes: list[EvidenceNode] = Field(
        default_factory=list,
        description="Nodes in the evidence graph",
    )
    edges: list[EvidenceEdge] = Field(
        default_factory=list,
        description="Edges connecting evidence nodes",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidencePackage
# ─────────────────────────────────────────────────────────────────────────────


class EvidencePackage(BaseModel):
    """Unified package of fused evidence.

    Aggregates multiple evidence items into a single package
    with fused content, a relationship graph, and a confidence
    score for the Reasoning Engine.
    """

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique package identifier",
    )
    evidence_ids: list[UUID4] = Field(
        default_factory=list,
        description="Evidence items included in this package",
    )
    fused_evidence: dict[str, Any] = Field(
        default_factory=dict,
        description="Fused evidence content keyed by evidence_id",
    )
    graph: EvidenceGraph | None = Field(
        default=None,
        description="Optional evidence relationship graph",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for this package (0.0–1.0)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this package was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceHealth
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceHealth(BaseModel):
    """Health status of the Evidence Fusion Engine.

    Provides operational health information for monitoring and
    observability of all evidence pipeline components.
    Phase 3 enhanced with classification, priority, trust,
    bundle, timeline, dedup, classification_manager,
    cache, policy, trace, metrics statuses and average latency.
    """

    overall_status: str = Field(
        default="UNKNOWN",
        description="Overall health status (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)",
    )
    evidence_count: int = Field(
        default=0,
        ge=0,
        description="Total number of evidence items",
    )
    collector_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence collector",
    )
    validator_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence validator",
    )
    normalizer_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence normalizer",
    )
    classifier_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence classification manager",
    )
    priority_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence priority assigner",
    )
    trust_manager_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence trust manager",
    )
    correlator_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence correlator",
    )
    conflict_detector_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence conflict detector",
    )
    deduplicator_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence deduplicator",
    )
    scorer_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence scorer",
    )
    graph_builder_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence graph builder",
    )
    bundle_manager_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence bundle manager",
    )
    timeline_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence timeline manager",
    )
    cache_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence cache",
    )
    policy_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence policy engine",
    )
    weight_manager_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence weight manager",
    )
    consensus_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence consensus manager",
    )
    trace_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence trace",
    )
    metrics_status: str = Field(
        default="UNKNOWN",
        description="Status of the evidence metrics collector",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of evidence pipeline errors",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average pipeline latency in milliseconds",
    )
    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Evidence engine uptime in seconds",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceMetrics
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceMetrics(BaseModel):
    """Aggregated metrics for the Evidence Fusion Engine.

    Tracks operational metrics for monitoring, alerting, and
    capacity planning of the evidence pipeline.
    Phase 3 enhanced with per-category/per-scope counters,
    version usage, collector/conflict/bundle/timeline/dedup
    totals, and cache/policy metrics.
    """

    evidence_total: int = Field(
        default=0,
        ge=0,
        description="Total number of evidence items processed",
    )
    packages_total: int = Field(
        default=0,
        ge=0,
        description="Total number of evidence packages created",
    )
    collections_total: int = Field(
        default=0,
        ge=0,
        description="Total number of evidence collections performed",
    )
    validations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of validations performed",
    )
    normalizations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of normalizations performed",
    )
    classifications_total: int = Field(
        default=0,
        ge=0,
        description="Total number of classifications performed",
    )
    priority_assignments_total: int = Field(
        default=0,
        ge=0,
        description="Total number of priority assignments performed",
    )
    graphs_total: int = Field(
        default=0,
        ge=0,
        description="Total number of graphs created",
    )
    graph_nodes_total: int = Field(
        default=0,
        ge=0,
        description="Total number of graph nodes created",
    )
    graph_edges_total: int = Field(
        default=0,
        ge=0,
        description="Total number of graph edges created",
    )
    correlations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of correlations performed",
    )
    conflicts_total: int = Field(
        default=0,
        ge=0,
        description="Total number of conflicts detected",
    )
    deduplications_total: int = Field(
        default=0,
        ge=0,
        description="Total number of deduplications performed",
    )
    bundles_total: int = Field(
        default=0,
        ge=0,
        description="Total number of bundles created",
    )
    timelines_total: int = Field(
        default=0,
        ge=0,
        description="Total number of timelines created",
    )
    fusions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of fusions performed",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Total number of cache hits",
    )
    cache_misses: int = Field(
        default=0,
        ge=0,
        description="Total number of cache misses",
    )
    policy_checks: int = Field(
        default=0,
        ge=0,
        description="Total number of policy checks performed",
    )
    policy_violations: int = Field(
        default=0,
        ge=0,
        description="Total number of policy violations",
    )
    errors_total: int = Field(
        default=0,
        ge=0,
        description="Total number of evidence pipeline errors",
    )
    evidence_per_classification: dict[str, int] = Field(
        default_factory=dict,
        description="Evidence count per classification",
    )
    evidence_per_priority: dict[str, int] = Field(
        default_factory=dict,
        description="Evidence count per priority level",
    )
    evidence_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Evidence count per domain",
    )
    evidence_per_type: dict[str, int] = Field(
        default_factory=dict,
        description="Evidence count per evidence type",
    )
    average_quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average quality score across all evidence (0.0–1.0)",
    )
    consistency_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of consistency scores",
    )
    consensus_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of consensus levels",
    )
    weight_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of weight values",
    )
    trust_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of trust scores",
    )
    quality_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of quality scores",
    )
    correlation_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of correlation scores",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When these metrics were captured",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceSession
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceSession(BaseModel):
    """Operational session for an evidence processing sequence.

    Tracks a sequence of evidence operations within a single
    session context for auditing, correlation, and explainability.
    Phase 3 enhanced with bundle, sources, domains, conflicts, quality.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    operation: str = Field(
        default="",
        description="The operation being performed (collect, validate, fuse, etc.)",
    )
    user_id: str = Field(
        default="",
        description="User or system that initiated the session",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    evidence_count: int = Field(
        default=0,
        ge=0,
        description="Number of evidence items in this session",
    )
    package_count: int = Field(
        default=0,
        ge=0,
        description="Number of packages created in this session",
    )
    bundle_id: UUID4 | None = Field(
        default=None,
        description="Optional bundle ID associated with this session",
    )
    sources_used: list[str] = Field(
        default_factory=list,
        description="Source identifiers used in this session",
    )
    domains_used: list[str] = Field(
        default_factory=list,
        description="Domain values tracked in this session",
    )
    conflicts_detected: int = Field(
        default=0,
        ge=0,
        description="Number of conflicts detected in this session",
    )
    quality_summary: str = Field(
        default="",
        description="Summary of overall evidence quality in this session",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session was completed (None if active)",
    )
    status: str = Field(
        default="ACTIVE",
        description="Session status (ACTIVE, COMPLETED, FAILED)",
    )
    statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Session statistics and timing data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceDecision
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceDecision(BaseModel):
    """Decision record for an evidence operation.

    Captures the outcome of an evidence operation including
    whether it was allowed, the reasoning, confidence, and
    associated metadata for explainability.
    Phase 3 enhanced with bundle, selected/rejected evidence,
    conflicts, quality, trust, and explainability.
    Phase 3.5 enhanced with evidence_weights and consensus_result.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    evidence_id: UUID4 = Field(
        description="The evidence this decision relates to",
    )
    bundle_id: UUID4 | None = Field(
        default=None,
        description="Optional bundle associated with this decision",
    )
    operation: str = Field(
        default="",
        description="The operation that triggered this decision",
    )
    allowed: bool = Field(
        default=True,
        description="Whether the operation was allowed",
    )
    selected_evidence: list[UUID4] = Field(
        default_factory=list,
        description="Evidence IDs selected for inclusion",
    )
    rejected_evidence: list[UUID4] = Field(
        default_factory=list,
        description="Evidence IDs rejected for inclusion",
    )
    evidence_weights: dict[str, float] = Field(
        default_factory=dict,
        description="Map of evidence ID to weight value (0.0–1.0)",
    )
    consensus_result: str = Field(
        default="",
        description="Consensus result summary (HIGH/MEDIUM/LOW agreement)",
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="Conflict descriptions detected during processing",
    )
    reasoning: list[str] = Field(
        default_factory=list,
        description="Human-readable reasoning steps for this decision",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this decision (0.0–1.0)",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Aggregate quality score from evidence processing (0.0–1.0)",
    )
    trust_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Trust score for this decision (0.0–1.0)",
    )
    performed_by: str = Field(
        default="",
        description="The user or system that performed the operation",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceConfidence
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceConfidence(BaseModel):
    """Confidence assessment for an evidence decision.

    Captures confidence across multiple dimensions: quality,
    trust, correlation, freshness, completeness, consensus,
    and weight distribution. Overall confidence is the
    average of all dimension scores.
    Phase 3.5 refreshed to consolidate dimensions.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0–1.0)",
    )
    quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality confidence (0.0–1.0)",
    )
    trust: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Trust confidence (0.0–1.0)",
    )
    correlation: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Correlation confidence (0.0–1.0)",
    )
    freshness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Freshness confidence (0.0–1.0)",
    )
    completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness confidence (0.0–1.0)",
    )
    consensus: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Consensus confidence (0.0–1.0)",
    )
    weight_distribution: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Weight distribution confidence (0.0–1.0)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceExplainabilityMetadata(BaseModel):
    """Explainability metadata for evidence decision reasoning.

    Captures why specific decisions were made during evidence
    processing, including why evidence was selected or rejected,
    why bundles were created or why conflicts were detected.
    Phase 3.5 enhanced with why_weight_assigned and why_consensus_reached.
    """

    why_selected: list[str] = Field(
        default_factory=list,
        description="Reasons why evidence was selected",
    )
    why_rejected: list[str] = Field(
        default_factory=list,
        description="Reasons why evidence was rejected",
    )
    why_bundle_created: list[str] = Field(
        default_factory=list,
        description="Reasons why a bundle was created",
    )
    why_conflict_detected: list[str] = Field(
        default_factory=list,
        description="Reasons why conflicts were detected",
    )
    why_priority_assigned: list[str] = Field(
        default_factory=list,
        description="Reasons why a priority was assigned",
    )
    why_trust_score: list[str] = Field(
        default_factory=list,
        description="Reasons for the trust score",
    )
    why_weight_assigned: list[str] = Field(
        default_factory=list,
        description="Reasons why specific weights were assigned",
    )
    why_consensus_reached: list[str] = Field(
        default_factory=list,
        description="Reasons for the consensus level",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceLineage
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceLineage(BaseModel):
    """Lineage record for an evidence item.

    Tracks the complete lineage of an evidence item through
    the fusion pipeline, including source, fusion history,
    bundle membership, decision chain, and parent/derived
    relationships.
    """

    evidence_id: UUID4 = Field(
        description="The evidence item this lineage belongs to",
    )
    original_source: str = Field(
        default="",
        description="Original source identifier for this evidence",
    )
    fusion_history: list[str] = Field(
        default_factory=list,
        description="History of fusion operations applied",
    )
    bundle_history: list[str] = Field(
        default_factory=list,
        description="Bundle membership changes over time",
    )
    decision_chain: list[str] = Field(
        default_factory=list,
        description="Chain of decision IDs that affected this evidence",
    )
    parent_evidence: list[UUID4] = Field(
        default_factory=list,
        description="Parent evidence IDs this was derived from",
    )
    derived_evidence: list[UUID4] = Field(
        default_factory=list,
        description="Evidence IDs derived from this evidence",
    )
    transformations: list[str] = Field(
        default_factory=list,
        description="Transformations applied to this evidence",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this lineage was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional lineage metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceSnapshot
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceSnapshot(BaseModel):
    """Immutable snapshot of evidence state at a point in time.

    Captures the complete state of evidence processing at a
    specific moment, including bundle, graph, timeline, quality,
    trust, and weight information.
    """

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    evidence_id: UUID4 = Field(
        description="The evidence this snapshot relates to",
    )
    bundle_state: dict[str, Any] = Field(
        default_factory=dict,
        description="State of the bundle at snapshot time",
    )
    graph_state: dict[str, Any] = Field(
        default_factory=dict,
        description="State of the graph at snapshot time",
    )
    timeline: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Timeline entries at snapshot time",
    )
    quality_state: dict[str, Any] = Field(
        default_factory=dict,
        description="Quality metrics at snapshot time",
    )
    trust_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Trust score at snapshot time",
    )
    weights: dict[str, float] = Field(
        default_factory=dict,
        description="Weight values at snapshot time",
    )
    consensus_level: str = Field(
        default="",
        description="Consensus level at snapshot time",
    )
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this snapshot was captured",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional snapshot metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceContext
# ─────────────────────────────────────────────────────────────────────────────


class EvidenceContext(BaseModel):
    """Contextual metadata for evidence processing.

    Carries context information such as asset, machine, facility,
    customer, workflow, and incident IDs that may be relevant
    during evidence collection, correlation, and fusion.
    """

    context_id: str = Field(
        default="",
        description="Unique context identifier",
    )
    asset_id: str = Field(
        default="",
        description="Asset identifier associated with this context",
    )
    machine_id: str = Field(
        default="",
        description="Machine identifier associated with this context",
    )
    facility_id: str = Field(
        default="",
        description="Facility identifier associated with this context",
    )
    customer_id: str = Field(
        default="",
        description="Customer identifier associated with this context",
    )
    workflow_id: str = Field(
        default="",
        description="Workflow identifier associated with this context",
    )
    incident_id: str = Field(
        default="",
        description="Incident identifier associated with this context",
    )
