"""Rule Manager Data Transfer Objects (DTOs).

DTOs provide stable, versioned contracts for external API consumers.
They decouple the public API surface from internal domain models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.rules.enums import RuleDomain, RuleType


class RuleRequestDTO(BaseModel):
    """DTO for incoming rule creation and update requests.

    Provides a clean API contract for rule operations that is
    independent of the internal Rule domain model.
    """

    name: str = Field(
        default="",
        description="Human-readable rule name",
    )
    description: str = Field(
        default="",
        description="Rule description and intent",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The domain this rule belongs to",
    )
    rule_type: RuleType = Field(
        default=RuleType.BUSINESS,
        description="The type of rule",
    )
    priority: int = Field(
        default=0,
        ge=0,
        description="Rule priority (higher = more important)",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this rule",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="User-defined tags for classification",
    )
    conditions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Rule conditions as serialisable dictionaries",
    )
    actions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Rule actions as serialisable dictionaries",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata key-value pairs",
    )


class RuleResponseDTO(BaseModel):
    """DTO for rule operation responses.

    Provides a stable API response contract independent of the
    internal domain model structure.
    """

    rule_id: UUID4 = Field(
        description="The rule identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable rule name",
    )
    description: str = Field(
        default="",
        description="Rule description",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The rule domain",
    )
    rule_type: RuleType = Field(
        default=RuleType.BUSINESS,
        description="The type of rule",
    )
    status: str = Field(
        default="DRAFT",
        description="Current lifecycle status",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Rule version number",
    )
    priority: int = Field(
        default=0,
        ge=0,
        description="Rule priority",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the rule is enabled",
    )
    created_at: datetime = Field(
        description="When the rule was created",
    )
    updated_at: datetime = Field(
        description="When the rule was last updated",
    )


class RuleEvaluationDTO(BaseModel):
    """DTO for rule evaluation requests.

    Provides a clean API contract for evaluation that is independent
    of the internal RuleContext and RuleEvaluation models.
    """

    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The domain to evaluate rules for",
    )
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for rule evaluation",
    )
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Entity attributes for condition matching",
    )
    user_id: str = Field(
        default="",
        description="The user or system triggering the evaluation",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    evaluation_strategy: str = Field(
        default="SEQUENTIAL",
        description="The evaluation strategy to use",
    )
    limit_rules: int = Field(
        default=0,
        ge=0,
        description="Maximum number of rules to evaluate (0 = unlimited)",
    )
