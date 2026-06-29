"""ExecutionStateMachine — validates and manages execution state transitions.

Supports the full execution state lifecycle with validated
transitions: PENDING → READY → RUNNING → WAITING/PAUSED/COMPLETED/FAILED
and rollback states.
"""

from __future__ import annotations

import structlog

from adip.execution.enums import ExecutionState

log = structlog.get_logger(__name__)

# Valid state transitions
_TRANSITIONS: dict[ExecutionState, set[ExecutionState]] = {
    ExecutionState.PENDING: {ExecutionState.READY, ExecutionState.CANCELLED},
    ExecutionState.READY: {ExecutionState.RUNNING, ExecutionState.CANCELLED},
    ExecutionState.RUNNING: {
        ExecutionState.WAITING,
        ExecutionState.PAUSED,
        ExecutionState.COMPLETED,
        ExecutionState.FAILED,
        ExecutionState.CANCELLED,
        ExecutionState.ROLLING_BACK,
    },
    ExecutionState.WAITING: {
        ExecutionState.RUNNING,
        ExecutionState.PAUSED,
        ExecutionState.CANCELLED,
        ExecutionState.FAILED,
    },
    ExecutionState.PAUSED: {
        ExecutionState.RUNNING,
        ExecutionState.CANCELLED,
        ExecutionState.FAILED,
    },
    ExecutionState.COMPLETED: set(),
    ExecutionState.FAILED: {ExecutionState.ROLLING_BACK},
    ExecutionState.CANCELLED: {ExecutionState.ROLLING_BACK},
    ExecutionState.ROLLING_BACK: {ExecutionState.ROLLED_BACK, ExecutionState.FAILED},
    ExecutionState.ROLLED_BACK: set(),
}


class ExecutionStateMachine:
    """Validates and manages execution state transitions."""

    def __init__(self) -> None:
        self._states: dict[str, ExecutionState] = {}

    def get_current_state(self, entity_id: str) -> ExecutionState:
        """Get the current state for an entity.

        Args:
            entity_id: The entity (session/task) ID.

        Returns:
            The current ExecutionState, or PENDING if not tracked.
        """
        return self._states.get(entity_id, ExecutionState.PENDING)

    def transition(
        self,
        entity_id: str,
        new_state: ExecutionState,
        correlation_id: str = "",
    ) -> tuple[bool, str]:
        """Attempt a state transition for an entity.

        Args:
            entity_id: The entity (session/task) ID.
            new_state: The desired new state.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Tuple of (success, message).
        """
        current = self.get_current_state(entity_id)
        allowed = _TRANSITIONS.get(current, set())

        if new_state not in allowed:
            message = (
                f"Invalid transition: {current.value} -> {new_state.value} "
                f"for entity {entity_id}"
            )
            log.warning(
                "state_machine.invalid_transition",
                entity_id=entity_id,
                current=current.value,
                desired=new_state.value,
                correlation_id=correlation_id,
            )
            return False, message

        self._states[entity_id] = new_state
        log.info(
            "state_machine.transitioned",
            entity_id=entity_id,
            from_state=current.value,
            to_state=new_state.value,
            correlation_id=correlation_id,
        )
        return True, f"Transitioned: {current.value} -> {new_state.value}"

    def reset(self, entity_id: str) -> None:
        """Reset an entity to PENDING state.

        Args:
            entity_id: The entity ID to reset.
        """
        self._states[entity_id] = ExecutionState.PENDING
        log.info("state_machine.reset", entity_id=entity_id)

    def is_terminal(self, entity_id: str) -> bool:
        """Check if an entity is in a terminal state.

        Args:
            entity_id: The entity ID.

        Returns:
            True if in a terminal state.
        """
        state = self.get_current_state(entity_id)
        return state in {ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED, ExecutionState.ROLLED_BACK}

    def is_active(self, entity_id: str) -> bool:
        """Check if an entity is in an active (non-terminal, non-pending) state.

        Args:
            entity_id: The entity ID.

        Returns:
            True if in an active state.
        """
        state = self.get_current_state(entity_id)
        return state in {ExecutionState.RUNNING, ExecutionState.WAITING, ExecutionState.PAUSED, ExecutionState.ROLLING_BACK}

    def is_transition_allowed(
        self,
        from_state: ExecutionState,
        to_state: ExecutionState,
    ) -> bool:
        """Check if a transition between two states is allowed.

        Args:
            from_state: The current state.
            to_state: The desired state.

        Returns:
            True if the transition is valid.
        """
        allowed = _TRANSITIONS.get(from_state, set())
        return to_state in allowed

    def get_allowed_transitions(
        self,
        from_state: ExecutionState,
    ) -> list[ExecutionState]:
        """Get all allowed transitions from a given state.

        Args:
            from_state: The state to check from.

        Returns:
            List of allowed ExecutionState values.
        """
        allowed = _TRANSITIONS.get(from_state, set())
        return list(allowed)
