"""PluginLifecycleManager — manages plugin lifecycle transitions.

Lifecycle states:
  DISCOVERED → VALIDATED → INSTALLED → LOADED → INITIALIZED →
  ACTIVE → SUSPENDED → UNLOADED → REMOVED

Supports forward and some backward transitions for lifecycle
management. Validates all transitions before applying.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import Plugin
from adip.plugins.enums import PluginLifecycleStatus
from adip.plugins.execution.models import LifecycleHistoryEntry

log = structlog.get_logger(__name__)


# Allowed lifecycle transitions
# Forward path: DISCOVERED → VALIDATED → INSTALLED → LOADED → INITIALIZED → ACTIVE
# Suspension: ACTIVE ↔ SUSPENDED
# Removal: ACTIVE → UNLOADED → REMOVED
# Re-entry: SUSPENDED → ACTIVE
# Skip: REMOVED is terminal

_ALLOWED_TRANSITIONS: dict[PluginLifecycleStatus, set[PluginLifecycleStatus]] = {
    PluginLifecycleStatus.DISCOVERED: {PluginLifecycleStatus.VALIDATED},
    PluginLifecycleStatus.VALIDATED: {PluginLifecycleStatus.INSTALLED, PluginLifecycleStatus.DISCOVERED},
    PluginLifecycleStatus.INSTALLED: {PluginLifecycleStatus.LOADED, PluginLifecycleStatus.REMOVED},
    PluginLifecycleStatus.LOADED: {PluginLifecycleStatus.INITIALIZED, PluginLifecycleStatus.UNLOADED},
    PluginLifecycleStatus.INITIALIZED: {PluginLifecycleStatus.ACTIVE, PluginLifecycleStatus.UNLOADED},
    PluginLifecycleStatus.ACTIVE: {PluginLifecycleStatus.SUSPENDED, PluginLifecycleStatus.UNLOADED},
    PluginLifecycleStatus.SUSPENDED: {PluginLifecycleStatus.ACTIVE, PluginLifecycleStatus.UNLOADED},
    PluginLifecycleStatus.UNLOADED: {PluginLifecycleStatus.LOADED, PluginLifecycleStatus.REMOVED},
    PluginLifecycleStatus.REMOVED: set(),
}


class PluginLifecycleManager:
    """Manages plugin lifecycle transitions and history."""

    def __init__(self) -> None:
        self._history: list[LifecycleHistoryEntry] = []

    def transition(
        self,
        plugin: Plugin,
        to_status: PluginLifecycleStatus,
        reason: str = "",
        changed_by: str = "",
    ) -> Plugin:
        """Transition a plugin to a new lifecycle status.

        Validates the transition against allowed rules before
        applying. Returns an updated Plugin with the new status.

        Raises ValueError if the transition is not allowed.
        """
        plugin_id = str(plugin.plugin_id)
        from_status = plugin.status

        log.info(
            "lifecycle_manager.transition",
            plugin=plugin.name,
            from_status=from_status.value,
            to_status=to_status.value,
        )

        if to_status == from_status:
            return plugin

        allowed = _ALLOWED_TRANSITIONS.get(from_status, set())
        if to_status not in allowed:
            raise ValueError(
                f"Illegal lifecycle transition: {from_status.value} -> {to_status.value} "
                f"for plugin {plugin.name} ({plugin_id})"
            )

        entry = LifecycleHistoryEntry(
            plugin_id=plugin.plugin_id,
            from_status=from_status,
            to_status=to_status,
            reason=reason or f"Transitioned from {from_status.value} to {to_status.value}",
            changed_by=changed_by,
        )
        self._history.append(entry)

        result = plugin.model_copy(update={"status": to_status, "updated_at": entry.timestamp})
        log.info(
            "lifecycle_manager.transition.complete",
            plugin=plugin.name,
            to_status=to_status.value,
        )
        return result

    def get_current_status(self, plugin: Plugin) -> PluginLifecycleStatus:
        """Return the current lifecycle status of a plugin."""
        return plugin.status

    def is_transition_allowed(
        self,
        current: PluginLifecycleStatus,
        target: PluginLifecycleStatus,
    ) -> bool:
        """Check if a lifecycle transition is allowed."""
        if current == target:
            return True
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        return target in allowed

    def get_history(self, plugin_id: str) -> list[LifecycleHistoryEntry]:
        """Return lifecycle history for a specific plugin."""
        return [e for e in self._history if str(e.plugin_id) == plugin_id]

    def get_all_history(self) -> list[LifecycleHistoryEntry]:
        """Return all lifecycle history entries."""
        return list(self._history)

    def get_transition_history(self, plugin_id: str) -> list[dict[str, str]]:
        """Return lifecycle transition history as serialisable dictionaries."""
        entries = self.get_history(plugin_id)
        return [
            {
                "from": str(e.from_status.value) if e.from_status else "",
                "to": e.to_status.value,
                "reason": e.reason,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in entries
        ]

    def clear(self) -> None:
        """Clear all lifecycle history."""
        self._history.clear()
