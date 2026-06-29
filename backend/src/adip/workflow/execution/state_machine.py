"""Workflow state machine — validates every lifecycle transition."""

from __future__ import annotations

import structlog

from adip.workflow.contracts.exceptions import StateTransitionException
from adip.workflow.enums import WorkflowStatus

log = structlog.get_logger(__name__)

_VALID_TRANSITIONS: dict[WorkflowStatus, set[WorkflowStatus]] = {
    WorkflowStatus.CREATED: {WorkflowStatus.INITIALIZED},
    WorkflowStatus.INITIALIZED: {WorkflowStatus.GRAPH_BUILT},
    WorkflowStatus.GRAPH_BUILT: {WorkflowStatus.SCHEDULED},
    WorkflowStatus.SCHEDULED: {
        WorkflowStatus.READY, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED,
    },
    WorkflowStatus.READY: {WorkflowStatus.RUNNING, WorkflowStatus.FAILED},
    WorkflowStatus.RUNNING: {
        WorkflowStatus.WAITING_APPROVAL,
        WorkflowStatus.PAUSED,
        WorkflowStatus.RETRYING,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.WAITING_APPROVAL: {
        WorkflowStatus.RUNNING,
        WorkflowStatus.PAUSED,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.FAILED,
    },
    WorkflowStatus.PAUSED: {
        WorkflowStatus.RUNNING,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.FAILED,
    },
    WorkflowStatus.RETRYING: {
        WorkflowStatus.RUNNING,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.COMPLETED: set(),
    WorkflowStatus.FAILED: set(),
    WorkflowStatus.CANCELLED: set(),
}


class WorkflowStateMachine:
    """Validates and executes state transitions for a workflow.

    Every transition is checked against the allowed graph before
    proceeding.  Illegal transitions raise ``StateTransitionException``.
    """

    def __init__(self, initial_state: WorkflowStatus = WorkflowStatus.CREATED) -> None:
        self._current = initial_state

    @property
    def current(self) -> WorkflowStatus:
        """The current workflow status."""
        return self._current

    def transition_to(self, target: WorkflowStatus) -> WorkflowStatus:
        """Attempt a transition from the current state to *target*.

        Returns the new state on success.
        Raises ``StateTransitionException`` if the transition is
        not in the allowed graph.
        """
        allowed = _VALID_TRANSITIONS.get(self._current, set())
        if target not in allowed:
            raise StateTransitionException(
                from_state=self._current.value,
                to_state=target.value,
            )
        log.info(
            "state_machine.transition",
            from_state=self._current.value,
            to_state=target.value,
        )
        self._current = target
        return self._current

    def reset(self, state: WorkflowStatus = WorkflowStatus.CREATED) -> None:
        """Reset the state machine to an initial state."""
        self._current = state
        log.info("state_machine.reset", state=state.value)

    def can_transition_to(self, target: WorkflowStatus) -> bool:
        """Check whether a transition is allowed without performing it."""
        return target in _VALID_TRANSITIONS.get(self._current, set())

    @staticmethod
    def is_terminal(state: WorkflowStatus) -> bool:
        """Return ``True`` if *state* is a terminal (absorbing) state."""
        return state in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED)

    @staticmethod
    def get_allowed_transitions(state: WorkflowStatus) -> set[WorkflowStatus]:
        """Return the set of states reachable from *state* in one transition."""
        return _VALID_TRANSITIONS.get(state, set())
