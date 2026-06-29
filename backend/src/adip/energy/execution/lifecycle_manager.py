"""AssetLifecycleManager — manages asset lifecycle state transitions.

Supports the lifecycle states: PLANNED -> COMMISSIONED -> OPERATIONAL
-> MAINTENANCE -> RETIRED, with validated transitions and
history tracking.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.energy.execution.models import AssetLifecycleState, LifecycleTransition

_INITIAL_STATE = AssetLifecycleState.PLANNED

log = structlog.get_logger(__name__)

_VALID_TRANSITIONS: dict[AssetLifecycleState, set[AssetLifecycleState]] = {
    AssetLifecycleState.PLANNED: {AssetLifecycleState.COMMISSIONED, AssetLifecycleState.RETIRED},
    AssetLifecycleState.COMMISSIONED: {AssetLifecycleState.OPERATIONAL, AssetLifecycleState.RETIRED},
    AssetLifecycleState.OPERATIONAL: {AssetLifecycleState.MAINTENANCE, AssetLifecycleState.RETIRED},
    AssetLifecycleState.MAINTENANCE: {AssetLifecycleState.OPERATIONAL, AssetLifecycleState.RETIRED},
    AssetLifecycleState.RETIRED: set(),
}


class AssetLifecycleManager:
    """Manages asset lifecycle state transitions with validation."""

    def __init__(self) -> None:
        self._transitions: list[LifecycleTransition] = []

    def transition(
        self,
        asset_id: str,
        from_state: AssetLifecycleState | None = None,
        to_state: AssetLifecycleState = _INITIAL_STATE,
        reason: str = "",
        correlation_id: str = "",
    ) -> LifecycleTransition:
        """Attempt a lifecycle state transition.

        Args:
            asset_id: The asset to transition.
            from_state: Current lifecycle state. If None, treated as an
                initial registration (skips transition validation).
            to_state: Desired new state. Defaults to PLANNED for initial
                registration when from_state is None.
            reason: Reason for the transition.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created LifecycleTransition.

        Raises:
            ValueError: If the transition is not valid
                (only when from_state is not None).
        """
        if from_state is not None:
            valid_targets = _VALID_TRANSITIONS.get(from_state, set())
            if to_state not in valid_targets:
                log.warning(
                    "energy.lifecycle.invalid_transition",
                    asset_id=asset_id,
                    from_state=from_state.value,
                    to_state=to_state.value,
                    correlation_id=correlation_id,
                )
                raise ValueError(
                    f"Invalid lifecycle transition: {from_state.value} -> {to_state.value}. "
                    f"Valid targets from {from_state.value}: {[s.value for s in valid_targets]}"
                )
        else:
            log.info(
                "energy.lifecycle.initialising",
                asset_id=asset_id,
                to_state=to_state.value,
                correlation_id=correlation_id,
            )

        transition = LifecycleTransition(
            asset_id=self._parse_uuid(asset_id),
            from_state=from_state or _INITIAL_STATE,
            to_state=to_state,
            reason=reason,
            timestamp=datetime.now(UTC),
        )
        self._transitions.append(transition)
        log.info(
            "energy.lifecycle.transitioned",
            asset_id=asset_id,
            from_state=(from_state or _INITIAL_STATE).value,
            to_state=to_state.value,
            reason=reason,
            correlation_id=correlation_id,
        )
        return transition

    def get_valid_transitions(
        self,
        state: AssetLifecycleState,
    ) -> list[AssetLifecycleState]:
        """Get valid target states from a given state.

        Args:
            state: The current lifecycle state.

        Returns:
            List of valid target states.
        """
        return list(_VALID_TRANSITIONS.get(state, set()))

    def get_transition_history(
        self,
        asset_id: str,
    ) -> list[LifecycleTransition]:
        """Get transition history for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            List of LifecycleTransition records for the asset.
        """
        return [
            t
            for t in self._transitions
            if str(t.asset_id) == asset_id
        ]

    def get_all_transitions(self) -> list[LifecycleTransition]:
        """Get all recorded transitions.

        Returns:
            List of all LifecycleTransition records.
        """
        return list(self._transitions)

    @staticmethod
    def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
        """Parse a string or UUID into a UUID."""
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_DNS, value)
