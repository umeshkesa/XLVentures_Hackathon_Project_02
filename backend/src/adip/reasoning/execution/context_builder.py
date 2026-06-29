"""ContextBuilder — constructs ReasoningContext for reasoning operations.

Collects evidence package, planner goal, workflow, rules,
memory, and knowledge into a unified reasoning context.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.reasoning.contracts.models import ReasoningContext
from adip.reasoning.enums import ReasoningDomain

log = structlog.get_logger(__name__)


class ContextBuilder:
    """Constructs ReasoningContext from available data sources.

    Deterministic placeholder that assembles context from
    evidence, goals, workflows, rules, memory, and knowledge.
    """

    def build_context(
        self,
        evidence_ids: list[str] | None = None,
        domain: ReasoningDomain = ReasoningDomain.SYSTEM,
        planner_goal: str = "",
        workflow_id: str = "",
        rule_ids: list[str] | None = None,
        memory_ids: list[str] | None = None,
        knowledge_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> ReasoningContext:
        """Build a complete reasoning context.

        Args:
            evidence_ids: Evidence IDs to include.
            domain: The reasoning domain.
            planner_goal: The planner goal string.
            workflow_id: Optional workflow ID.
            rule_ids: Optional rule IDs.
            memory_ids: Optional memory IDs.
            knowledge_ids: Optional knowledge IDs.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A ReasoningContext populated from available sources.
        """
        log.info("context_builder.build", domain=domain.value, correlation_id=correlation_id)
        return ReasoningContext(
            metadata={
                "evidence_ids": evidence_ids or [],
                "domain": domain.value,
                "planner_goal": planner_goal,
                "workflow_id": workflow_id,
                "rule_ids": rule_ids or [],
                "memory_ids": memory_ids or [],
                "knowledge_ids": knowledge_ids or [],
                "correlation_id": correlation_id,
            },
        )

    def merge_contexts(
        self,
        contexts: list[ReasoningContext],
        correlation_id: str = "",
    ) -> ReasoningContext:
        """Merge multiple reasoning contexts into one.

        Args:
            contexts: List of contexts to merge.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A merged ReasoningContext.
        """
        log.info("context_builder.merge", count=len(contexts), correlation_id=correlation_id)
        merged_metadata: dict[str, Any] = {}
        for ctx in contexts:
            merged_metadata.update(ctx.metadata)
        merged_metadata["merged_count"] = len(contexts)
        return ReasoningContext(
            metadata=merged_metadata,
        )

    def enrich_context(
        self,
        context: ReasoningContext,
        additional_data: dict[str, Any],
        correlation_id: str = "",
    ) -> ReasoningContext:
        """Enrich a context with additional data.

        Args:
            context: The context to enrich.
            additional_data: Data to add.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The enriched ReasoningContext.
        """
        log.info("context_builder.enrich", correlation_id=correlation_id)
        merged = dict(context.metadata)
        merged.update(additional_data)
        merged["enriched"] = True
        return ReasoningContext(metadata=merged)
