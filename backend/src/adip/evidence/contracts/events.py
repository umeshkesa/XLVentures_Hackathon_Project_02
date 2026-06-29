"""Events for the Evidence Fusion Engine.

Defines the event types emitted during evidence processing
including collection, validation, normalization, correlation,
fusion, and packaging lifecycle stages.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.evidence.enums import EvidenceDomain, EvidenceType

EventVersion: str = "1.0.0"


class EvidenceEvent(BaseModel):
    """Base event for all evidence-related events.

    Provides common fields including event identification,
    evidence reference, type classification, domain,
    timestamp, correlation, and extensible payload.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    evidence_id: UUID4 = Field(
        description="The evidence this event relates to",
    )
    evidence_type: EvidenceType = Field(
        description="Type of the evidence",
    )
    domain: EvidenceDomain = Field(
        default=EvidenceDomain.SYSTEM,
        description="Domain of the evidence",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event payload",
    )


class EvidenceCollected(EvidenceEvent):
    """Emitted when evidence has been collected from a source."""

    source_type: str = Field(
        default="",
        description="Type of source the evidence was collected from",
    )
    source_manager: str = Field(
        default="",
        description="Manager that collected the evidence",
    )


class EvidenceValidated(EvidenceEvent):
    """Emitted when evidence has passed validation."""

    validated: bool = Field(
        default=True,
        description="Whether validation passed",
    )
    violations: list[str] = Field(
        default_factory=list,
        description="Validation violations if any",
    )


class EvidenceNormalized(EvidenceEvent):
    """Emitted when evidence has been normalized."""

    normalizer: str = Field(
        default="",
        description="Normalizer component that processed the evidence",
    )
    normalized_fields: list[str] = Field(
        default_factory=list,
        description="Fields that were normalized",
    )


class EvidenceCorrelated(EvidenceEvent):
    """Emitted when evidence has been correlated with other evidence."""

    correlated_evidence_ids: list[UUID4] = Field(
        default_factory=list,
        description="Evidence IDs this evidence was correlated with",
    )
    correlation_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Correlation strength score (0.0–1.0)",
    )


class EvidenceFused(EvidenceEvent):
    """Emitted when evidence has been fused into a unified form."""

    package_id: UUID4 = Field(
        description="The package this evidence was fused into",
    )
    fusion_weight: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Weight of this evidence in the fusion (0.0–1.0)",
    )


class EvidencePackaged(EvidenceEvent):
    """Emitted when an evidence package has been created."""

    package_id: UUID4 = Field(
        description="The package that was created",
    )
    evidence_count: int = Field(
        default=0,
        ge=0,
        description="Number of evidence items in the package",
    )
    package_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the package (0.0–1.0)",
    )
