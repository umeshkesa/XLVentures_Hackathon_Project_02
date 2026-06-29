"""PluginResourceManager — tracks placeholder resource usage for plugins.

Monitors CPU, memory, storage, network, timeout, and agent/tool
resource limits.

Deterministic placeholder — no actual resource monitoring.
"""

from __future__ import annotations

import uuid

import structlog

from adip.plugins.execution.models import ResourceUsage

log = structlog.get_logger(__name__)


class PluginResourceManager:
    """Tracks resource usage and limits for plugins.

    Provides placeholder resource tracking with configurable
    limits and usage snapshots.
    """

    def __init__(self) -> None:
        self._usage: dict[str, ResourceUsage] = {}
        self._limits: dict[str, dict[str, float]] = {}

    def allocate(self, plugin_id: str, limits: dict[str, float] | None = None) -> ResourceUsage:
        """Allocate resources for a plugin.

        Creates a ResourceUsage entry with optional custom limits.
        """
        log.info("resource_manager.allocate", plugin_id=plugin_id)

        usage = ResourceUsage(
            plugin_id=uuid.UUID(plugin_id) if isinstance(plugin_id, str) and _is_uuid(plugin_id) else uuid.uuid4(),
            cpu_percent=0.0,
            memory_mb=0.0,
            storage_mb=0.0,
            timeout_seconds=limits.get("timeout_seconds", 30.0) if limits else 30.0,
            agent_count=int(limits.get("max_agents", 5)) if limits else 5,
            tool_count=int(limits.get("max_tools", 10)) if limits else 10,
        )

        self._usage[plugin_id] = usage
        if limits:
            self._limits[plugin_id] = dict(limits)

        return usage

    def track_cpu(self, plugin_id: str, percent: float) -> bool:
        """Track CPU usage for a plugin."""
        usage = self._usage.get(plugin_id)
        if usage is None:
            return False
        usage.cpu_percent = percent
        return True

    def track_memory(self, plugin_id: str, mb: float) -> bool:
        """Track memory usage for a plugin."""
        usage = self._usage.get(plugin_id)
        if usage is None:
            return False
        usage.memory_mb = mb
        return True

    def track_storage(self, plugin_id: str, mb: float) -> bool:
        """Track storage usage for a plugin."""
        usage = self._usage.get(plugin_id)
        if usage is None:
            return False
        usage.storage_mb = mb
        return True

    def track_network(self, plugin_id: str, bytes_count: int) -> bool:
        """Track network usage for a plugin."""
        usage = self._usage.get(plugin_id)
        if usage is None:
            return False
        usage.network_bytes = bytes_count
        return True

    def get_usage(self, plugin_id: str) -> ResourceUsage | None:
        """Get current resource usage for a plugin."""
        return self._usage.get(plugin_id)

    def get_limits(self, plugin_id: str) -> dict[str, float]:
        """Get resource limits for a plugin."""
        return dict(self._limits.get(plugin_id, {}))

    def get_all_usage(self) -> list[ResourceUsage]:
        """Get resource usage for all tracked plugins."""
        return list(self._usage.values())

    def release(self, plugin_id: str) -> bool:
        """Release all resources allocated to a plugin."""
        log.info("resource_manager.release", plugin_id=plugin_id)
        existed = plugin_id in self._usage
        self._usage.pop(plugin_id, None)
        self._limits.pop(plugin_id, None)
        return existed

    def check_limits(self, plugin_id: str) -> list[str]:
        """Check if a plugin has exceeded its resource limits.

        Returns a list of violation strings (empty = within limits).
        """
        violations: list[str] = []
        usage = self._usage.get(plugin_id)
        limits = self._limits.get(plugin_id, {})

        if usage is None:
            violations.append(f"No resource usage tracked for plugin {plugin_id}")
            return violations

        cpu_limit = limits.get("cpu_max_percent", 100.0)
        if usage.cpu_percent > cpu_limit:
            violations.append(
                f"CPU usage {usage.cpu_percent}% exceeds limit {cpu_limit}%"
            )

        mem_limit = limits.get("memory_max_mb", 1024.0)
        if usage.memory_mb > mem_limit:
            violations.append(
                f"Memory usage {usage.memory_mb}MB exceeds limit {mem_limit}MB"
            )

        storage_limit = limits.get("storage_max_mb", 4096.0)
        if usage.storage_mb > storage_limit:
            violations.append(
                f"Storage usage {usage.storage_mb}MB exceeds limit {storage_limit}MB"
            )

        return violations

    def reset(self, plugin_id: str) -> bool:
        """Reset resource usage for a plugin to zero."""
        usage = self._usage.get(plugin_id)
        if usage is None:
            return False
        usage.cpu_percent = 0.0
        usage.memory_mb = 0.0
        usage.storage_mb = 0.0
        usage.network_bytes = 0
        return True

    def clear(self) -> int:
        """Clear all resource tracking. Returns the number cleared."""
        count = len(self._usage)
        self._usage.clear()
        self._limits.clear()
        return count


def _is_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False
