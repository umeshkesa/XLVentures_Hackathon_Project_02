"""RegistryLifecycleManager — manages the lifecycle state machine.

Handles status transitions, transition validation, and history
tracking for the RegistryLifecycleStatus state machine.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.registry.contracts.models import RegistryEntry
from adip.registry.enums import RegistryLifecycleStatus
from adip.registry.execution.models import LifecycleHistoryEntry

log = structlog.get_logger(__name__)

_ALLOWED_TRANSITIONS: dict[RegistryLifecycleStatus, set[RegistryLifecycleStatus]] = {
    RegistryLifecycleStatus.REGISTERED: {RegistryLifecycleStatus.VALIDATED},
    RegistryLifecycleStatus.VALIDATED: {RegistryLifecycleStatus.ACTIVE, RegistryLifecycleStatus.REGISTERED},
    RegistryLifecycleStatus.ACTIVE: {RegistryLifecycleStatus.SUSPENDED, RegistryLifecycleStatus.DEPRECATED},
    RegistryLifecycleStatus.SUSPENDED: {RegistryLifecycleStatus.ACTIVE, RegistryLifecycleStatus.DEPRECATED},
    RegistryLifecycleStatus.DEPRECATED: {RegistryLifecycleStatus.REMOVED},
    RegistryLifecycleStatus.REMOVED: set(),
}


class RegistryLifecycleManager:
    """Manages the lifecycle state machine for registry entries."""

    def __init__(self) -> None:
        self._history: list[LifecycleHistoryEntry] = []

    def transition(
        self,
        entry: RegistryEntry,
        new_status: RegistryLifecycleStatus,
        reason: str = "",
        changed_by: str = "",
    ) -> RegistryEntry:
        """Transition an entry to a new lifecycle status."""
        log.info(
            "registry_lifecycle_manager.transition",
            entry_id=str(entry.entry_id),
            from_status=entry.status.value,
            to_status=new_status.value,
        )
        if entry.status == new_status:
            return entry
        allowed = _ALLOWED_TRANSITIONS.get(entry.status, set())
        if new_status not in allowed:
            valid = [s.value for s in allowed]
            msg = (
                f"Transition from {entry.status.value} to {new_status.value} is not allowed. "
                f"Valid next states: {valid}"
            )
            raise ValueError(msg)
        history_entry = LifecycleHistoryEntry(
            entry_id=entry.entry_id,
            from_status=entry.status,
            to_status=new_status,
            reason=reason,
            changed_by=changed_by,
        )
        self._history.append(history_entry)
        return entry.model_copy(update={
            "status": new_status,
            "updated_at": datetime.now(UTC),
        })

    def get_valid_transitions(self, current_status: RegistryLifecycleStatus) -> list[RegistryLifecycleStatus]:
        """Return valid next states for a given status."""
        log.info("registry_lifecycle_manager.get_valid_transitions", status=current_status.value)
        return list(_ALLOWED_TRANSITIONS.get(current_status, set()))

    def can_transition(self, entry: RegistryEntry, new_status: RegistryLifecycleStatus) -> bool:
        """Check whether a transition is allowed."""
        allowed = _ALLOWED_TRANSITIONS.get(entry.status, set())
        return new_status in allowed

    def is_transition_allowed(self, current: RegistryLifecycleStatus, target: RegistryLifecycleStatus) -> bool:
        """Check whether a transition between two statuses is allowed."""
        return target in _ALLOWED_TRANSITIONS.get(current, set())

    def get_history(self, entry_id: str) -> list[LifecycleHistoryEntry]:
        """Retrieve lifecycle transition history for an entry."""
        log.info("registry_lifecycle_manager.get_history", entry_id=entry_id)
        return [h for h in self._history if str(h.entry_id) == entry_id]

    def get_all_history(self) -> list[LifecycleHistoryEntry]:
        """Retrieve all lifecycle transition history."""
        return list(self._history)

    def clear(self) -> None:
        """Clear all transition history."""
        self._history.clear()
