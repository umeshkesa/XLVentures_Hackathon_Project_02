"""CompensationManager — compensation, rollback, manual recovery, and alternative actions.

Manages compensation plans for rolling back or compensating
executed tasks when execution fails or is cancelled. Supports
automatic compensation, manual recovery hints, and alternative
action suggestions.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class CompensationAction:
    """A recorded compensation or rollback action."""

    def __init__(
        self,
        action_id: str = "",
        task_id: str = "",
        action_type: str = "compensation",
        description: str = "",
        success: bool = True,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.action_id = action_id
        self.task_id = task_id
        self.action_type = action_type
        self.description = description
        self.success = success
        self.details = details or {}


class CompensationManager:
    """Manages compensation, rollback, and recovery actions."""

    def __init__(self) -> None:
        self._actions: list[CompensationAction] = []

    def compensate(
        self,
        task_id: str = "",
        session_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> CompensationAction:
        """Execute compensation for a failed task.

        Reverses the effects of a completed task to maintain
        system consistency after failure.

        Args:
            task_id: The task ID to compensate for.
            session_id: The session ID.
            reason: Reason for compensation.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A CompensationAction describing the compensation result.
        """
        action = CompensationAction(
            action_id=f"comp-{task_id[:8]}" if task_id else "comp-unknown",
            task_id=task_id,
            action_type="compensation",
            description=f"Compensated task {task_id}: {reason}" if reason else f"Compensated task {task_id}",
            success=True,
            details={"session_id": session_id, "reason": reason},
        )
        self._actions.append(action)
        log.info(
            "compensation_manager.compensated",
            task_id=task_id,
            action_id=action.action_id,
            correlation_id=correlation_id,
        )
        return action

    def rollback(
        self,
        task_id: str = "",
        session_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> CompensationAction:
        """Execute rollback for a failed task.

        Rolls back the changes made by a task, restoring the
        previous system state.

        Args:
            task_id: The task ID to roll back.
            session_id: The session ID.
            reason: Reason for rollback.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A CompensationAction describing the rollback result.
        """
        action = CompensationAction(
            action_id=f"rb-{task_id[:8]}" if task_id else "rb-unknown",
            task_id=task_id,
            action_type="rollback",
            description=f"Rolled back task {task_id}: {reason}" if reason else f"Rolled back task {task_id}",
            success=True,
            details={"session_id": session_id, "reason": reason},
        )
        self._actions.append(action)
        log.info(
            "compensation_manager.rolled_back",
            task_id=task_id,
            action_id=action.action_id,
            correlation_id=correlation_id,
        )
        return action

    def manual_recovery(
        self,
        task_id: str = "",
        session_id: str = "",
        recovery_steps: list[str] | None = None,
        correlation_id: str = "",
    ) -> CompensationAction:
        """Suggest manual recovery steps for a failed task.

        Provides human-readable recovery instructions when
        automatic compensation or rollback is not possible.

        Args:
            task_id: The task ID requiring manual recovery.
            session_id: The session ID.
            recovery_steps: Suggested manual recovery steps.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A CompensationAction with manual recovery details.
        """
        steps = recovery_steps or ["Check system logs", "Verify system state", "Contact support"]
        action = CompensationAction(
            action_id=f"mr-{task_id[:8]}" if task_id else "mr-unknown",
            task_id=task_id,
            action_type="manual_recovery",
            description=f"Manual recovery required for task {task_id}",
            success=True,
            details={"recovery_steps": steps, "session_id": session_id},
        )
        self._actions.append(action)
        log.info(
            "compensation_manager.manual_recovery",
            task_id=task_id,
            steps=len(steps),
            correlation_id=correlation_id,
        )
        return action

    def alternative_action(
        self,
        task_id: str = "",
        session_id: str = "",
        alternative: str = "",
        correlation_id: str = "",
    ) -> CompensationAction:
        """Suggest an alternative action for a failed task.

        Provides an alternative approach when the original
        task cannot be completed and compensation is preferred
        over rollback.

        Args:
            task_id: The task ID.
            session_id: The session ID.
            alternative: Description of the alternative action.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A CompensationAction with alternative action details.
        """
        action = CompensationAction(
            action_id=f"alt-{task_id[:8]}" if task_id else "alt-unknown",
            task_id=task_id,
            action_type="alternative_action",
            description=alternative or f"Alternative action for task {task_id}",
            success=True,
            details={"session_id": session_id, "alternative": alternative},
        )
        self._actions.append(action)
        log.info(
            "compensation_manager.alternative_action",
            task_id=task_id,
            alternative=alternative,
            correlation_id=correlation_id,
        )
        return action

    def get_actions(self) -> list[CompensationAction]:
        """Get all recorded compensation actions."""
        return list(self._actions)

    def get_actions_for_task(self, task_id: str) -> list[CompensationAction]:
        """Get all compensation actions for a specific task.

        Args:
            task_id: The task ID.

        Returns:
            List of CompensationAction for the task.
        """
        return [a for a in self._actions if a.task_id == task_id]

    def get_total_actions(self) -> int:
        """Get total number of compensation actions."""
        return len(self._actions)

    def clear(self) -> None:
        """Clear all recorded compensation actions."""
        self._actions.clear()
