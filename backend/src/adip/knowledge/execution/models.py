"""Execution-layer models for the Knowledge Manager.

These models support internal processing: version tracking, query
analysis, trace records, lifecycle history, and policy decisions.
They are not exposed through the public KnowledgeService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import UUID4, BaseModel, Field

from adip.knowledge.enums import (
    KnowledgeDomain,
    KnowledgeLifecycleStatus,
    RetrievalType,
)

# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeVersionRecord
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeVersionRecord(BaseModel):
    """A version record for a knowledge document.

    Tracks every version of a document including its version number,
    parent version, change summary, and lifecycle status.
    """

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version identifier",
    )
    document_id: UUID4 = Field(
        description="The document this version belongs to",
    )
    version_number: int = Field(
        default=1,
        ge=1,
        description="Monotonic version number",
    )
    parent_version: int | None = Field(
        default=None,
        description="The parent version this was derived from",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this version was created",
    )
    created_by: str = Field(
        default="",
        description="User or system that created this version",
    )
    change_summary: str = Field(
        default="",
        description="Summary of changes in this version",
    )
    lifecycle_status: KnowledgeLifecycleStatus = Field(
        default=KnowledgeLifecycleStatus.DRAFT,
        description="Current lifecycle status of this version",
    )
    active: bool = Field(
        default=True,
        description="Whether this is the active version",
    )


# ─────────────────────────────────────────────────────────────────────────────
# LifecycleHistoryEntry
# ─────────────────────────────────────────────────────────────────────────────


class LifecycleHistoryEntry(BaseModel):
    """A single lifecycle transition record."""

    entry_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique history entry identifier",
    )
    document_id: UUID4 = Field(
        description="The document that transitioned",
    )
    from_status: KnowledgeLifecycleStatus | None = Field(
        default=None,
        description="Previous lifecycle status",
    )
    to_status: KnowledgeLifecycleStatus = Field(
        description="New lifecycle status",
    )
    reason: str = Field(
        default="",
        description="Reason for the transition",
    )
    changed_by: str = Field(
        default="",
        description="User or system that performed the transition",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the transition occurred",
    )


# ─────────────────────────────────────────────────────────────────────────────
# QueryAnalysis
# ─────────────────────────────────────────────────────────────────────────────


class QueryAnalysis(BaseModel):
    """Result of analysing a knowledge query.

    Captures the parsed intent, domain, filters, keywords, and
    recommended retrieval strategy for a query.
    """

    analysis_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique analysis identifier",
    )
    query_text: str = Field(
        default="",
        description="The original query text",
    )
    intent: str = Field(
        default="",
        description="Detected query intent (e.g. lookup, compare, summarise)",
    )
    domain: KnowledgeDomain = Field(
        default=KnowledgeDomain.SYSTEM,
        description="The most relevant knowledge domain",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Extracted metadata filters",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Extracted keywords",
    )
    suggested_retrieval_type: RetrievalType = Field(
        default=RetrievalType.HYBRID,
        description="Recommended retrieval strategy",
    )
    requested_version: int | None = Field(
        default=None,
        description="Specific version requested (if any)",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the analysis (0.0–1.0)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# QueryRewrite
# ─────────────────────────────────────────────────────────────────────────────


class QueryRewrite(BaseModel):
    """Result of rewriting a query for improved retrieval.

    Produces alternative query forms for expansion, normalisation,
    and synonym-based retrieval.
    """

    rewrite_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique rewrite identifier",
    )
    original_query: str = Field(
        default="",
        description="The original query text",
    )
    expanded_query: str = Field(
        default="",
        description="Query expanded with synonyms or context",
    )
    normalised_query: str = Field(
        default="",
        description="Normalised version of the query",
    )
    alternative_queries: list[str] = Field(
        default_factory=list,
        description="Alternative phrasings of the query",
    )
    strategy: str = Field(
        default="",
        description="Rewriting strategy applied (e.g. synonym, expansion)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TraceRecord
# ─────────────────────────────────────────────────────────────────────────────


class TraceRecord(BaseModel):
    """A single trace entry recording a stage in a knowledge operation.

    Tracks execution stage, operation type, document context,
    timing, warnings, errors, and correlation ID for observability.
    """

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    stage_name: str = Field(
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        description="The operation being performed",
    )
    document_id: UUID4 | None = Field(
        default=None,
        description="The document involved (if applicable)",
    )
    version: int | None = Field(
        default=None,
        ge=1,
        description="Document version involved",
    )
    lifecycle_state: str = Field(
        default="",
        description="Current lifecycle state",
    )
    domain: str = Field(
        default="",
        description="Knowledge domain of the operation",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage began",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the stage finished",
    )
    duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Wall-clock duration in milliseconds",
    )
    success: bool = Field(
        default=True,
        description="Whether the stage completed without error",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Fatal errors",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
