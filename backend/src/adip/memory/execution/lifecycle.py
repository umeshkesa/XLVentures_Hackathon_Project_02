"""MemoryLifecycleManager — first-class lifecycle state management.

Every MemoryRecord must maintain lifecycle state.  The LifecycleManager
validates all transitions, records history, and emits lifecycle events.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.memory.contracts.models import MemoryRecord
from adip.memory.enums import MemoryLifecycleStatus
from adip.memory.execution.models import MemoryLifecycleHistory

log = structlog.get_logger(__name__)

# Allowed transitions: current → {allowed next states}
_ALLOWED_TRANSITIONS: dict[MemoryLifecycleStatus, set[MemoryLifecycleStatus]] = {
    MemoryLifecycleStatus.CREATED: {MemoryLifecycleStatus.ACTIVE},
    MemoryLifecycleStatus.ACTIVE: {
        MemoryLifecycleStatus.UPDATED,
        MemoryLifecycleStatus.ARCHIVED,
        MemoryLifecycleStatus.EXPIRED,
        MemoryLifecycleStatus.DELETED,
    },
    MemoryLifecycleStatus.UPDATED: {
        MemoryLifecycleStatus.ACTIVE,
        MemoryLifecycleStatus.ARCHIVED,
        MemoryLifecycleStatus.EXPIRED,
        MemoryLifecycleStatus.DELETED,
    },
    MemoryLifecycleStatus.ARCHIVED: {
        MemoryLifecycleStatus.DELETED,
        MemoryLifecycleStatus.ACTIVE,  # restore
    },
    MemoryLifecycleStatus.EXPIRED: {MemoryLifecycleStatus.DELETED},
    MemoryLifecycleStatus.DELETED: set(),  # terminal
}


class MemoryLifecycleManager:
    """Manages the lifecycle state of memory records.

    Every transition is validated against a hard-coded allowed graph.
    Illegal transitions raise ``ValueError``.
    """

    def __init__(self) -> None:
        self._history: dict[str, list[MemoryLifecycleHistory]] = {}

    # ── Public API ─────────────────────────────────────────────────────────

    def initialize(self, record: MemoryRecord) -> MemoryRecord:
        """Set the initial lifecycle state to CREATED.

        Called when a record is first created.  Only sets state if
        not already present in metadata.
        """
        if "lifecycle_status" not in record.metadata:
            record.metadata["lifecycle_status"] = MemoryLifecycleStatus.CREATED.value
            log.debug(
                "lifecycle.initialized",
                memory_id=str(record.memory_id),
                state=MemoryLifecycleStatus.CREATED.value,
            )
        return record

    def transition(
        self,
        record: MemoryRecord,
        target: MemoryLifecycleStatus,
        reason: str = "",
        actor: str = "system",
    ) -> MemoryRecord:
        """Transition the record to a new lifecycle state.

        Validates the transition first.  Records history on success.
        """
        current = self._get_current(record)
        if current == target:
            return record

        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise ValueError(
                f"Invalid lifecycle transition: {current.value} → {target.value} "
                f"(allowed from {current.value}: {[s.value for s in allowed]})",
            )

        record.metadata["lifecycle_status"] = target.value
        record.metadata["lifecycle_updated_at"] = datetime.now(UTC).isoformat()

        entry = MemoryLifecycleHistory(
            memory_id=record.memory_id,
            previous_state=current,
            new_state=target,
            reason=reason,
            actor=actor,
        )
        key = str(record.memory_id)
        self._history.setdefault(key, []).append(entry)

        log.info(
            "lifecycle.transition",
            memory_id=str(record.memory_id),
            from_state=current.value,
            to_state=target.value,
            reason=reason,
        )
        return record

    def get_history(
        self,
        record: MemoryRecord,
    ) -> list[MemoryLifecycleHistory]:
        """Return the full lifecycle history for a record."""
        return list(self._history.get(str(record.memory_id), []))

    def get_current(self, record: MemoryRecord) -> MemoryLifecycleStatus:
        """Return the current lifecycle status without modifying the record."""
        return self._get_current(record)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _get_current(self, record: MemoryRecord) -> MemoryLifecycleStatus:
        raw = record.metadata.get("lifecycle_status", MemoryLifecycleStatus.CREATED.value)
        try:
            return MemoryLifecycleStatus(raw)
        except ValueError:
            return MemoryLifecycleStatus.CREATED

    # ── Static helpers ─────────────────────────────────────────────────────

    @staticmethod
    def is_terminal(status: MemoryLifecycleStatus) -> bool:
        """Return True if the status is a terminal (final) state."""
        return status in {MemoryLifecycleStatus.EXPIRED, MemoryLifecycleStatus.DELETED}

    @staticmethod
    def get_allowed_transitions(
        status: MemoryLifecycleStatus,
    ) -> list[MemoryLifecycleStatus]:
        """Return the list of allowed next states from a given status."""
        return sorted(_ALLOWED_TRANSITIONS.get(status, set()), key=lambda s: s.value)
