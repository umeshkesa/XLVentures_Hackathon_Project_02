"""AssumptionManager — manages assumptions during reasoning.

Handles creation, validation, tracking, and invalidation of
assumptions made during reasoning operations.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.reasoning.enums import AssumptionStatus
from adip.reasoning.execution.models import Assumption

log = structlog.get_logger(__name__)


class AssumptionManager:
    """Manages assumptions for reasoning operations.

    Deterministic placeholder that creates, validates, tracks,
    and invalidates assumptions during reasoning.
    """

    def __init__(self) -> None:
        self._assumptions: dict[str, Assumption] = {}

    def create_assumption(
        self,
        description: str,
        source: str = "",
    ) -> Assumption:
        """Create a new assumption.

        Args:
            description: Description of the assumption.
            source: Source of the assumption.

        Returns:
            The created Assumption.
        """
        assumption = Assumption(
            description=description,
            source=source,
            status=AssumptionStatus.ACTIVE,
        )
        self._assumptions[str(assumption.assumption_id)] = assumption
        log.info("assumption_manager.create", source=source)
        return assumption

    def get_assumption(self, assumption_id: str) -> Assumption | None:
        """Get an assumption by ID.

        Args:
            assumption_id: The assumption identifier.

        Returns:
            The Assumption if found, None otherwise.
        """
        return self._assumptions.get(assumption_id)

    def get_all_assumptions(self) -> list[Assumption]:
        """Get all tracked assumptions.

        Returns:
            List of all Assumption instances.
        """
        return list(self._assumptions.values())

    def get_active_assumptions(self) -> list[Assumption]:
        """Get all active assumptions.

        Returns:
            List of active Assumption instances.
        """
        return [a for a in self._assumptions.values() if a.status == AssumptionStatus.ACTIVE]

    def validate_assumption(self, assumption_id: str) -> bool:
        """Validate an assumption (marks it as validated).

        Args:
            assumption_id: The assumption identifier.

        Returns:
            True if validated, False if not found.
        """
        assumption = self._assumptions.get(assumption_id)
        if assumption is None:
            return False
        assumption.status = AssumptionStatus.VALIDATED
        assumption.validated_at = datetime.now(UTC)
        log.info("assumption_manager.validate", assumption_id=assumption_id)
        return True

    def invalidate_assumption(self, assumption_id: str) -> bool:
        """Invalidate an assumption.

        Args:
            assumption_id: The assumption identifier.

        Returns:
            True if invalidated, False if not found.
        """
        assumption = self._assumptions.get(assumption_id)
        if assumption is None:
            return False
        assumption.status = AssumptionStatus.INVALIDATED
        assumption.invalidated_at = datetime.now(UTC)
        log.info("assumption_manager.invalidate", assumption_id=assumption_id)
        return True

    def suspend_assumption(self, assumption_id: str) -> bool:
        """Suspend an assumption.

        Args:
            assumption_id: The assumption identifier.

        Returns:
            True if suspended, False if not found.
        """
        assumption = self._assumptions.get(assumption_id)
        if assumption is None:
            return False
        assumption.status = AssumptionStatus.SUSPENDED
        log.info("assumption_manager.suspend", assumption_id=assumption_id)
        return True

    def clear(self) -> None:
        """Clear all tracked assumptions."""
        self._assumptions.clear()

    def count(self) -> int:
        """Get the number of tracked assumptions.

        Returns:
            Assumption count.
        """
        return len(self._assumptions)
