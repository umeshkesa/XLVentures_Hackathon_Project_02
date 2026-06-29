"""CheckpointManager — execution checkpoint creation, restoration, and resumption.

Manages checkpoints for saving and restoring execution state,
enabling resumption of failed or paused executions.
"""

from __future__ import annotations

import structlog

from adip.execution.enums import ExecutionState
from adip.execution.execution.models import Checkpoint

log = structlog.get_logger(__name__)


class CheckpointManager:
    """Creates, restores, and manages execution checkpoints."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, Checkpoint] = {}

    def create_checkpoint(
        self,
        session_id: str = "",
        package_id: str = "",
        completed_task_ids: list[str] | None = None,
        failed_task_ids: list[str] | None = None,
        in_progress_task_ids: list[str] | None = None,
        pending_task_ids: list[str] | None = None,
        task_states: dict[str, ExecutionState] | None = None,
        state: ExecutionState = ExecutionState.RUNNING,
        correlation_id: str = "",
    ) -> Checkpoint:
        """Create an execution checkpoint.

        Args:
            session_id: The execution session ID.
            package_id: The execution package ID.
            completed_task_ids: Task IDs that completed.
            failed_task_ids: Task IDs that failed.
            in_progress_task_ids: Task IDs in progress.
            pending_task_ids: Task IDs still pending.
            task_states: Map of task ID to state.
            state: Current execution state.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created Checkpoint.
        """
        checkpoint = Checkpoint(
            session_id=session_id,
            package_id=package_id,
            completed_task_ids=completed_task_ids or [],
            failed_task_ids=failed_task_ids or [],
            in_progress_task_ids=in_progress_task_ids or [],
            pending_task_ids=pending_task_ids or [],
            task_states=task_states or {},
            state=state,
        )
        cp_id = str(checkpoint.checkpoint_id)
        self._checkpoints[cp_id] = checkpoint
        log.info(
            "checkpoint.created",
            checkpoint_id=cp_id,
            session_id=session_id,
            completed=len(checkpoint.completed_task_ids),
            failed=len(checkpoint.failed_task_ids),
            correlation_id=correlation_id,
        )
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Get a checkpoint by ID.

        Args:
            checkpoint_id: The checkpoint ID.

        Returns:
            Checkpoint if found, None otherwise.
        """
        return self._checkpoints.get(checkpoint_id)

    def restore_checkpoint(
        self,
        checkpoint_id: str,
        correlation_id: str = "",
    ) -> Checkpoint | None:
        """Restore a checkpoint for resumption.

        Args:
            checkpoint_id: The checkpoint ID to restore.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The Checkpoint if found, None otherwise.
        """
        checkpoint = self._checkpoints.get(checkpoint_id)
        if checkpoint:
            log.info(
                "checkpoint.restored",
                checkpoint_id=checkpoint_id,
                session_id=checkpoint.session_id,
                state=checkpoint.state.value,
                correlation_id=correlation_id,
            )
        else:
            log.warning(
                "checkpoint.not_found",
                checkpoint_id=checkpoint_id,
                correlation_id=correlation_id,
            )
        return checkpoint

    def get_latest_for_session(self, session_id: str) -> Checkpoint | None:
        """Get the latest checkpoint for a session.

        Args:
            session_id: The session ID.

        Returns:
            The most recent Checkpoint for the session, or None.
        """
        matches = [
            cp for cp in self._checkpoints.values() if cp.session_id == session_id
        ]
        if not matches:
            return None
        return max(matches, key=lambda cp: cp.created_at)

    def get_session_checkpoints(self, session_id: str) -> list[Checkpoint]:
        """Get all checkpoints for a session.

        Args:
            session_id: The session ID.

        Returns:
            List of Checkpoints for the session.
        """
        return [
            cp for cp in self._checkpoints.values() if cp.session_id == session_id
        ]

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.

        Args:
            checkpoint_id: The checkpoint ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        if checkpoint_id in self._checkpoints:
            del self._checkpoints[checkpoint_id]
            log.info("checkpoint.deleted", checkpoint_id=checkpoint_id)
            return True
        return False

    def get_all_checkpoints(self) -> list[Checkpoint]:
        """Get all stored checkpoints."""
        return list(self._checkpoints.values())

    def resume_from_checkpoint(
        self,
        checkpoint: Checkpoint,
        correlation_id: str = "",
    ) -> dict[str, list[str]]:
        """Compute resume plan from a checkpoint.

        Determines which tasks need re-execution, which can
        be skipped, and which still need compensation.

        Args:
            checkpoint: The checkpoint to resume from.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dict with 'completed', 'failed', 'pending', 'in_progress' task ID lists.
        """
        plan = {
            "completed": list(checkpoint.completed_task_ids),
            "failed": list(checkpoint.failed_task_ids),
            "pending": list(checkpoint.pending_task_ids),
            "in_progress": list(checkpoint.in_progress_task_ids),
        }
        log.info(
            "checkpoint.resume_plan",
            checkpoint_id=str(checkpoint.checkpoint_id),
            completed=len(plan["completed"]),
            failed=len(plan["failed"]),
            pending=len(plan["pending"]),
            correlation_id=correlation_id,
        )
        return plan
