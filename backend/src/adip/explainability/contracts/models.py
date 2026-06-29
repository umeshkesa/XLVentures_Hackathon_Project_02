"""Domain models for the Explainability Engine.

Defines all domain models used across explainability contracts,
interfaces, and execution components.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.explainability.enums import (
    CitationType as CitationTypeEnum,
)
from adip.explainability.enums import (
    ExplanationDomain as ExplanationDomainEnum,
)
from adip.explainability.enums import (
    ExplanationLayer as ExplanationLayerEnum,
)
from adip.explainability.enums import (
    ExplanationStatus as ExplanationStatusEnum,
)
from adip.explainability.enums import (
    NarrativeType as NarrativeTypeEnum,
)


class ExplanationRequest(BaseModel):
    """Request to initiate an explanation operation.

    Captures the input parameters for an explanation operation,
    including the results from reasoning, evidence, and recommendation
    engines to transform into human-interpretable explanations.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    reasoning_result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="The reasoning result ID to explain",
    )
    evidence_result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="The evidence result ID to explain",
    )
    recommendation_result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="The recommendation result ID to explain",
    )
    target_audiences: list[ExplanationLayerEnum] = Field(
        default_factory=list,
        description="Target audience layers for this explanation",
    )
    domain: ExplanationDomainEnum = Field(
        default=ExplanationDomainEnum.SYSTEM,
        description="The domain for this explanation operation",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the explanation operation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the request was created",
    )


class ExplanationResult(BaseModel):
    """Result of an explanation operation.

    Captures the complete output of an explanation operation,
    including the package, narratives, citations, and decisions.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    request_id: UUID4 = Field(
        description="The request this result belongs to",
    )
    package: ExplanationPackage | None = Field(
        default=None,
        description="The explanation package",
    )
    narratives: list[ExplanationNarrative] = Field(
        default_factory=list,
        description="Narratives generated for this result",
    )
    citations: list[ExplanationCitation] = Field(
        default_factory=list,
        description="Citations associated with this result",
    )
    decisions: list[ExplanationDecision] = Field(
        default_factory=list,
        description="Decisions made during explanation",
    )
    status: ExplanationStatusEnum = Field(
        default=ExplanationStatusEnum.INITIALIZED,
        description="Status of the explanation operation",
    )
    confidence: ExplanationConfidence | None = Field(
        default=None,
        description="Confidence assessment for this result",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the result was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result metadata",
    )


class ExplanationPackage(BaseModel):
    """A packaged set of explanation components.

    Groups the primary narrative with supporting narratives,
    evidence citations, and summaries from related engines.
    """

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique package identifier",
    )
    result_id: UUID4 = Field(
        description="The result this package belongs to",
    )
    primary_narrative: ExplanationNarrative | None = Field(
        default=None,
        description="The primary explanation narrative",
    )
    supporting_narratives: list[ExplanationNarrative] = Field(
        default_factory=list,
        description="Supporting narratives for this package",
    )
    evidence_citations: list[ExplanationCitation] = Field(
        default_factory=list,
        description="Evidence citations supporting the explanation",
    )
    reasoning_summary: str = Field(
        default="",
        description="Summary of the reasoning behind this explanation",
    )
    recommendation_summary: str = Field(
        default="",
        description="Summary of the recommendations from this explanation",
    )
    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for this package (0.0-1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional package metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package was created",
    )


class ExplanationNarrative(BaseModel):
    """A single narrative within an explanation.

    Represents a tailored explanation narrative for a specific
    audience layer, containing formatted content and metadata.
    """

    narrative_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique narrative identifier",
    )
    package_id: UUID4 = Field(
        description="The package this narrative belongs to",
    )
    narrative_type: NarrativeTypeEnum = Field(
        default=NarrativeTypeEnum.SUMMARY,
        description="Type of narrative content",
    )
    audience: ExplanationLayerEnum = Field(
        default=ExplanationLayerEnum.ENGINEER,
        description="Target audience for this narrative",
    )
    title: str = Field(
        default="",
        description="Narrative title",
    )
    content: str = Field(
        default="",
        description="Narrative content body",
    )
    summary: str = Field(
        default="",
        description="Brief summary of the narrative",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional narrative metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the narrative was created",
    )


class ExplanationContext(BaseModel):
    """Contextual information for an explanation operation.

    Captures the broader operational context including asset,
    machine, facility, and workflow identifiers.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    reasoning_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context from the reasoning engine",
    )
    evidence_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context from the evidence engine",
    )
    recommendation_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context from the recommendation engine",
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
    workflow_id: str = Field(
        default="",
        description="Workflow identifier associated with this context",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


class ExplanationAudience(BaseModel):
    """Audience definition for explanation targeting.

    Defines an audience layer with its detail level requirements
    and technical depth preferences.
    """

    audience_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique audience identifier",
    )
    layer: ExplanationLayerEnum = Field(
        description="The audience layer type",
    )
    name: str = Field(
        default="",
        description="Human-readable audience name",
    )
    description: str = Field(
        default="",
        description="Description of this audience",
    )
    required_detail_level: str = Field(
        default="",
        description="Required level of detail for this audience",
    )
    technical_depth: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Technical depth preference (0.0-1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional audience metadata",
    )


class ExplanationPolicy(BaseModel):
    """Policy governing explanation generation.

    Defines constraints and requirements for generating
    explanations, including allowed audiences and citation rules.
    """

    policy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique policy identifier",
    )
    name: str = Field(
        default="",
        description="Policy name",
    )
    description: str = Field(
        default="",
        description="Policy description",
    )
    allowed_layers: list[ExplanationLayerEnum] = Field(
        default_factory=list,
        description="Audience layers allowed by this policy",
    )
    max_narratives: int = Field(
        default=10,
        ge=1,
        description="Maximum number of narratives allowed",
    )
    require_citations: bool = Field(
        default=True,
        description="Whether citations are required for narratives",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this policy is active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional policy metadata",
    )


class ExplanationTrace(BaseModel):
    """Trace record for an explanation pipeline stage.

    Captures timing, success, and error information for each
    stage of the explanation pipeline.
    """

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    stage_name: str = Field(
        default="",
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        default="",
        description="Operation being traced",
    )
    explanation_id: str = Field(
        default="",
        description="The explanation identifier for this trace",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the stage completed",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Duration of the stage in milliseconds",
    )
    success: bool = Field(
        default=False,
        description="Whether the stage completed successfully",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings generated during this stage",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors generated during this stage",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional trace metadata",
    )


class ExplanationCitation(BaseModel):
    """Citation referencing a source for an explanation.

    Links a narrative to a specific source with an excerpt
    and relevance score for traceability.
    """

    citation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique citation identifier",
    )
    narrative_id: UUID4 = Field(
        description="The narrative this citation belongs to",
    )
    citation_type: CitationTypeEnum = Field(
        description="Type of citation source",
    )
    source_id: str = Field(
        default="",
        description="Identifier of the source document",
    )
    source_type: str = Field(
        default="",
        description="Type of the source (e.g., evidence, reasoning, recommendation)",
    )
    excerpt: str = Field(
        default="",
        description="Excerpt from the source being cited",
    )
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score for this citation (0.0-1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional citation metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the citation was created",
    )


class ExplanationLayer(BaseModel):
    """Layer definition for explanation formatting.

    Defines a specific audience layer with its formatting
    preferences and display requirements.
    """

    layer_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique layer identifier",
    )
    layer_type: ExplanationLayerEnum = Field(
        description="The layer type",
    )
    name: str = Field(
        default="",
        description="Human-readable layer name",
    )
    description: str = Field(
        default="",
        description="Description of this layer",
    )
    format_preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Formatting preferences for this layer",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional layer metadata",
    )


class ExplanationConfidence(BaseModel):
    """Confidence assessment for an explanation.

    Captures multi-dimensional confidence scores for the
    quality, accuracy, and completeness of an explanation.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0-1.0)",
    )
    narrative_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score for narratives (0.0-1.0)",
    )
    citation_accuracy: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Accuracy score for citations (0.0-1.0)",
    )
    completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness score for the explanation (0.0-1.0)",
    )
    audience_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Coverage score across target audiences (0.0-1.0)",
    )
    evidence_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Evidence coverage score (0.0-1.0)",
    )
    consistency: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Consistency score across explanation components (0.0-1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional confidence metadata",
    )


class ExplanationMetadata(BaseModel):
    """Metadata for an explanation entity.

    Provides descriptive and categorical information about
    an explanation for search and organization.
    """

    title: str = Field(
        default="",
        description="Title of the explanation",
    )
    description: str = Field(
        default="",
        description="Description of the explanation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorizing the explanation",
    )
    category: str = Field(
        default="",
        description="Category classification",
    )
    source: str = Field(
        default="",
        description="Source system or component",
    )
    version: str = Field(
        default="",
        description="Version of the explanation format",
    )
    why_narrative: str = Field(default="", description="Why this narrative was chosen")
    why_citation: str = Field(default="", description="Why this citation was selected")
    why_trace: str = Field(default="", description="Why this trace was recorded")
    why_template: str = Field(default="", description="Why this template was used")
    why_policy: str = Field(default="", description="Why this policy was applied")
    why_audience: str = Field(default="", description="Why this audience was targeted")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class ExplanationHealth(BaseModel):
    """Health status of the explanation engine.

    Captures the operational health of all explanation
    engine sub-components and aggregate statistics.
    """

    overall_status: str = Field(
        default="",
        description="Overall health status",
    )
    coordinator_status: str = Field(
        default="",
        description="Status of the coordinator component",
    )
    narrative_builder_status: str = Field(
        default="",
        description="Status of the narrative builder component",
    )
    citation_builder_status: str = Field(
        default="",
        description="Status of the citation builder component",
    )
    audience_formatter_status: str = Field(
        default="",
        description="Status of the audience formatter component",
    )
    validator_status: str = Field(
        default="",
        description="Status of the validator component",
    )
    narrative_status: str = Field(
        default="",
        description="Status of the narrative component",
    )
    citation_status: str = Field(
        default="",
        description="Status of the citation component",
    )
    trace_status: str = Field(
        default="",
        description="Status of the trace component",
    )
    formatter_status: str = Field(
        default="",
        description="Status of the formatter component",
    )
    template_status: str = Field(
        default="",
        description="Status of the template component",
    )
    policy_status: str = Field(
        default="",
        description="Status of the policy component",
    )
    explanation_count: int = Field(
        default=0,
        ge=0,
        description="Total number of explanations generated",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average latency in milliseconds",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )


class ExplanationMetrics(BaseModel):
    """Metrics for the explanation engine.

    Captures aggregate operational metrics for monitoring
    and observability of the explanation engine.
    """

    explanations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of explanations",
    )
    narratives_total: int = Field(
        default=0,
        ge=0,
        description="Total number of narratives generated",
    )
    citations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of citations generated",
    )
    packages_total: int = Field(
        default=0,
        ge=0,
        description="Total number of packages created",
    )
    validated_total: int = Field(
        default=0,
        ge=0,
        description="Total number of validations performed",
    )
    failed_total: int = Field(
        default=0,
        ge=0,
        description="Total number of failures",
    )
    explanations_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Explanation count per domain",
    )
    explanations_per_layer: dict[str, int] = Field(
        default_factory=dict,
        description="Explanation count per audience layer",
    )
    average_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average confidence across all explanations (0.0-1.0)",
    )
    average_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average completeness across all explanations (0.0-1.0)",
    )
    sessions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of explanation sessions",
    )
    audiences_total: int = Field(
        default=0,
        ge=0,
        description="Total number of audiences targeted",
    )
    templates_total: int = Field(
        default=0,
        ge=0,
        description="Total number of templates used",
    )
    citation_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Citation coverage across all explanations (0.0-1.0)",
    )
    average_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average quality across all explanations (0.0-1.0)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When these metrics were recorded",
    )


class ExplanationSession(BaseModel):
    """Session tracking for an explanation operation.

    Captures the lifecycle and statistics of an explanation
    session from initialization to completion.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    request_id: UUID4 = Field(
        description="The request this session belongs to",
    )
    domain: ExplanationDomainEnum = Field(
        default=ExplanationDomainEnum.SYSTEM,
        description="The domain for this session",
    )
    target_layers: list[ExplanationLayerEnum] = Field(
        default_factory=list,
        description="Target audience layers for this session",
    )
    status: ExplanationStatusEnum = Field(
        default=ExplanationStatusEnum.INITIALIZED,
        description="Current status of the session",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session completed",
    )
    statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Session statistics and aggregations",
    )
    audience: str = Field(
        default="",
        description="Target audience for this session",
    )
    template: str = Field(
        default="",
        description="Template used for this session",
    )
    policy: str = Field(
        default="",
        description="Policy applied for this session",
    )
    source_sessions: list[str] = Field(
        default_factory=list,
        description="Source session identifiers contributing to this session",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )


class ExplanationDecision(BaseModel):
    """Decision produced by an explanation operation.

    Captures the final explanation decision, selected and
    rejected narratives, and the reasoning behind the decision.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    result_id: UUID4 = Field(
        description="The result this decision belongs to",
    )
    conclusion: str = Field(
        default="",
        description="The final explanation conclusion",
    )
    reasoning_summary: str = Field(
        default="",
        description="Summary of the reasoning that led to this explanation",
    )
    recommendation_summary: str = Field(
        default="",
        description="Summary of recommendations from this explanation",
    )
    selected_narratives: list[str] = Field(
        default_factory=list,
        description="Narrative IDs selected as part of this decision",
    )
    rejected_narratives: list[str] = Field(
        default_factory=list,
        description="Narrative IDs rejected during explanation",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this decision (0.0-1.0)",
    )
    audience: ExplanationLayerEnum = Field(
        default=ExplanationLayerEnum.ENGINEER,
        description="Primary audience for this decision",
    )
    readiness: str = Field(
        default="",
        description="Readiness assessment for this decision",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
