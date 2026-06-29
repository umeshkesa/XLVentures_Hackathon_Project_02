"""Evidence Data Transfer Objects (DTOs).

DTOs for the Evidence Fusion Engine API layer. These are used
for external communication and should not contain business logic.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.evidence.enums import EvidenceDomain, EvidenceType


class EvidenceRequestDTO(BaseModel):
    """DTO for requesting evidence collection.

    Carries the parameters needed to collect evidence from
    a specific source type and domain.
    """

    evidence_type: EvidenceType = Field(
        default=EvidenceType.KNOWLEDGE,
        description="Type of evidence to collect",
    )
    domain: EvidenceDomain = Field(
        default=EvidenceDomain.SYSTEM,
        description="Domain context for the evidence",
    )
    source_id: str = Field(
        default="",
        description="Optional source identifier",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional collection parameters",
    )


class EvidenceResponseDTO(BaseModel):
    """DTO for evidence operation responses.

    Carries the result of an evidence operation including
    the evidence ID, status, and any additional metadata.
    """

    evidence_id: UUID4 = Field(
        description="The evidence ID this response relates to",
    )
    evidence_type: EvidenceType = Field(
        description="Type of the evidence",
    )
    domain: EvidenceDomain = Field(
        description="Domain of the evidence",
    )
    status: str = Field(
        default="",
        description="Current status of the evidence",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0–1.0)",
    )
    message: str = Field(
        default="",
        description="Human-readable response message",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the response was generated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata",
    )


class EvidencePackageDTO(BaseModel):
    """DTO for evidence package responses.

    Carries a summary of an evidence package for external
    consumption without exposing the full internal model.
    """

    package_id: UUID4 = Field(
        description="The package ID this DTO relates to",
    )
    evidence_count: int = Field(
        default=0,
        ge=0,
        description="Number of evidence items in the package",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Package confidence score (0.0–1.0)",
    )
    domains: list[EvidenceDomain] = Field(
        default_factory=list,
        description="Domains covered in this package",
    )
    evidence_types: list[EvidenceType] = Field(
        default_factory=list,
        description="Evidence types in this package",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package DTO was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional package metadata",
    )
