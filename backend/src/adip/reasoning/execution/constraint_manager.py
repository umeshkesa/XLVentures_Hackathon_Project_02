"""ConstraintManager — manages reasoning constraints.

Handles creation, validation, and tracking of constraints
including budget, time, safety, compliance, SLA, resources,
and business policies.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.reasoning.enums import ConstraintType
from adip.reasoning.execution.models import Constraint

log = structlog.get_logger(__name__)


class ConstraintManager:
    """Manages constraints for reasoning operations.

    Deterministic placeholder that creates, validates, and
    tracks constraints for reasoning pipelines.
    """

    def __init__(self) -> None:
        self._constraints: dict[str, Constraint] = {}

    def create_constraint(
        self,
        constraint_type: ConstraintType,
        description: str = "",
        value: float = 0.0,
        unit: str = "",
        is_hard: bool = True,
        is_active: bool = True,
    ) -> Constraint:
        """Create a new constraint.

        Args:
            constraint_type: The type of constraint.
            description: Description of the constraint.
            value: Numeric value for this constraint.
            unit: Unit of measurement.
            is_hard: Whether this is a hard constraint.
            is_active: Whether this constraint is active.

        Returns:
            The created Constraint.
        """
        constraint = Constraint(
            constraint_type=constraint_type,
            description=description or self._default_description(constraint_type),
            value=value,
            unit=unit,
            is_hard=is_hard,
            is_active=is_active,
        )
        self._constraints[str(constraint.constraint_id)] = constraint
        log.info(
            "constraint_manager.create",
            constraint_type=constraint_type.value,
            is_hard=is_hard,
        )
        return constraint

    def get_constraint(self, constraint_id: str) -> Constraint | None:
        """Get a constraint by ID.

        Args:
            constraint_id: The constraint identifier.

        Returns:
            The Constraint if found, None otherwise.
        """
        return self._constraints.get(constraint_id)

    def get_all_constraints(self) -> list[Constraint]:
        """Get all tracked constraints.

        Returns:
            List of all Constraint instances.
        """
        return list(self._constraints.values())

    def get_active_constraints(self) -> list[Constraint]:
        """Get all active constraints.

        Returns:
            List of active Constraint instances.
        """
        return [c for c in self._constraints.values() if c.is_active]

    def validate_constraint(self, constraint: Constraint, value: float = 0.0) -> bool:
        """Validate a constraint against a value.

        A hard constraint is satisfied if value <= constraint.value.
        A soft constraint logs a warning but passes.

        Args:
            constraint: The constraint to validate.
            value: The value to check against the constraint.

        Returns:
            True if the constraint is satisfied, False otherwise.
        """
        satisfied = value <= constraint.value if constraint.is_hard else True
        if not satisfied:
            log.warning(
                "constraint_manager.violation",
                constraint_id=str(constraint.constraint_id),
                type=constraint.constraint_type.value,
                value=value,
                limit=constraint.value,
            )
        return satisfied

    def validate_all(
        self,
        values: dict[str, float] | None = None,
    ) -> list[tuple[Constraint, bool]]:
        """Validate all active constraints against provided values.

        Args:
            values: Map of constraint_id string to value to check.

        Returns:
            List of (Constraint, satisfied) tuples.
        """
        results: list[tuple[Constraint, bool]] = []
        values = values or {}
        for constraint in self.get_active_constraints():
            val = values.get(str(constraint.constraint_id), 0.0)
            satisfied = self.validate_constraint(constraint, val)
            results.append((constraint, satisfied))
        return results

    def deactivate(self, constraint_id: str) -> bool:
        """Deactivate a constraint.

        Args:
            constraint_id: The constraint identifier.

        Returns:
            True if deactivated, False if not found.
        """
        constraint = self._constraints.get(constraint_id)
        if constraint is None:
            return False
        constraint.is_active = False
        return True

    def clear(self) -> None:
        """Clear all tracked constraints."""
        self._constraints.clear()

    def count(self) -> int:
        """Get the number of tracked constraints.

        Returns:
            Constraint count.
        """
        return len(self._constraints)

    def _default_description(self, constraint_type: ConstraintType) -> str:
        """Get default description for a constraint type.

        Args:
            constraint_type: The constraint type.

        Returns:
            Default description string.
        """
        descriptions = {
            ConstraintType.BUDGET: "Budget constraint for reasoning operation",
            ConstraintType.TIME: "Time constraint for reasoning operation",
            ConstraintType.SAFETY: "Safety constraint for reasoning operation",
            ConstraintType.COMPLIANCE: "Compliance constraint for reasoning operation",
            ConstraintType.SLA: "SLA constraint for reasoning operation",
            ConstraintType.RESOURCES: "Resource constraint for reasoning operation",
            ConstraintType.BUSINESS_POLICIES: "Business policy constraint for reasoning operation",
        }
        return descriptions.get(constraint_type, f"Constraint: {constraint_type.value}")
