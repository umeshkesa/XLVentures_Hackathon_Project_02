"""DependencyResolver — hard, soft and optional dependency resolution.

Resolves dependencies between action plan steps, categorising
them into hard (mandatory), soft (preferred), and optional
(nice-to-have), and determining the optimal resolution order.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import DependencyResolution

log = structlog.get_logger(__name__)


class DependencyResolver:
    """Resolves hard, soft, and optional dependencies between steps."""

    def resolve_dependencies(
        self,
        plan_id: str = "",
        step_ids: list[str] | None = None,
        dependencies: list[tuple[str, str, str]] | None = None,
        correlation_id: str = "",
    ) -> DependencyResolution:
        """Resolve dependencies for a set of steps.

        Args:
            plan_id: The plan ID.
            step_ids: List of step IDs.
            dependencies: List of (source, target, dep_type) tuples.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            DependencyResolution with categorised dependencies.
        """
        step_ids = step_ids or []
        dependencies = dependencies or []

        hard: list[str] = []
        soft: list[str] = []
        optional: list[str] = []
        unresolved: list[str] = []

        for src, tgt, dep_type in dependencies:
            if dep_type == "hard":
                hard.append(tgt)
            elif dep_type == "soft":
                soft.append(tgt)
            elif dep_type == "optional":
                optional.append(tgt)
            else:
                unresolved.append(tgt)

        # Determine resolution order: hard first, then soft, then optional
        resolution_order = []
        for sid in step_ids:
            if sid not in hard:
                resolution_order.append(sid)
        for sid in hard:
            if sid not in resolution_order:
                resolution_order.append(sid)
        for sid in soft:
            if sid not in resolution_order:
                resolution_order.append(sid)
        for sid in optional:
            if sid not in resolution_order:
                resolution_order.append(sid)

        result = DependencyResolution(
            plan_id=plan_id,
            hard_dependencies=hard,
            soft_dependencies=soft,
            optional_dependencies=optional,
            unresolved_dependencies=unresolved,
            resolution_order=resolution_order,
        )
        log.info(
            "dependency_resolver.resolved",
            plan_id=plan_id,
            hard=len(hard),
            soft=len(soft),
            optional=len(optional),
            unresolved=len(unresolved),
            correlation_id=correlation_id,
        )
        return result

    def validate_dependencies(
        self,
        plan_id: str = "",
        step_ids: list[str] | None = None,
        dependencies: list[tuple[str, str, str]] | None = None,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate dependencies for correctness.

        Args:
            plan_id: The plan ID.
            step_ids: List of step IDs.
            dependencies: List of (source, target, dep_type) tuples.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        violations: list[str] = []
        step_ids_set = set(step_ids or [])
        dependencies = dependencies or []
        valid_types = {"hard", "soft", "optional"}

        for src, tgt, dep_type in dependencies:
            if src not in step_ids_set:
                violations.append(f"Source step {src} not found")
            if tgt not in step_ids_set:
                violations.append(f"Target step {tgt} not found")
            if dep_type not in valid_types:
                violations.append(f"Invalid dependency type: {dep_type}")
            if src == tgt:
                violations.append("Self-referencing dependency")

        return violations

    def get_execution_order(
        self,
        resolution: DependencyResolution,
    ) -> list[str]:
        """Get the recommended execution order from a resolution."""
        return resolution.resolution_order
