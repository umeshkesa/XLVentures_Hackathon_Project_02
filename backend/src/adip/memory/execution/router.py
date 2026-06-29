"""MemoryRouter — determines storage tier and backend for memory operations.

The router encapsulates all routing logic so that Memory Stores
and the Memory Manager delegate tier decisions without knowing
the storage topology.
"""

from __future__ import annotations

import structlog

from adip.memory.contracts.models import MemoryPolicy, MemoryRecord
from adip.memory.enums import MemoryTier, MemoryType

log = structlog.get_logger(__name__)

# Default tier mapping: memory type → default storage tier
_DEFAULT_TIER_MAP: dict[MemoryType, MemoryTier] = {
    MemoryType.SESSION: MemoryTier.HOT,
    MemoryType.WORKFLOW: MemoryTier.HOT,
    MemoryType.CACHE: MemoryTier.HOT,
    MemoryType.CONVERSATION: MemoryTier.WARM,
    MemoryType.PLANNING: MemoryTier.WARM,
    MemoryType.RECOMMENDATION: MemoryTier.WARM,
    MemoryType.USER: MemoryTier.WARM,
    MemoryType.LEARNING: MemoryTier.COLD,
}


class MemoryRouter:
    """Determines the storage tier and backend for a memory record.

    No database calls are made.  All routing decisions are based on
    memory type, namespace rules, and policy.
    """

    def __init__(
        self,
        custom_tier_map: dict[MemoryType, MemoryTier] | None = None,
        namespace_routes: dict[str, MemoryTier] | None = None,
    ) -> None:
        self._tier_map = {**_DEFAULT_TIER_MAP, **(custom_tier_map or {})}
        self._namespace_routes = namespace_routes or {}

    def route(
        self,
        record: MemoryRecord,
        policy: MemoryPolicy | None = None,
    ) -> MemoryTier:
        """Determine the storage tier for a record.

        Precedence:
          1. Namespace override (if configured)
          2. Memory type default
          3. Policy hint
          4. Fallback to WARM
        """
        # Namespace override takes highest precedence
        if record.namespace in self._namespace_routes:
            tier = self._namespace_routes[record.namespace]
            log.debug(
                "router.namespace_route",
                memory_id=str(record.memory_id),
                namespace=record.namespace,
                tier=tier.value,
            )
            return tier

        # Memory type default
        tier = self._tier_map.get(record.memory_type, MemoryTier.WARM)

        log.debug(
            "router.route",
            memory_id=str(record.memory_id),
            memory_type=record.memory_type.value,
            tier=tier.value,
        )
        return tier

    def get_tier_for_type(self, memory_type: MemoryType) -> MemoryTier:
        """Return the default tier for a memory type."""
        return self._tier_map.get(memory_type, MemoryTier.WARM)

    def validate_route(self, tier: MemoryTier) -> bool:
        """Return True if the tier is a valid storage target."""
        return tier in MemoryTier

    def get_all_routes(self) -> dict[MemoryType, MemoryTier]:
        """Return the complete tier map (for diagnostics / metrics)."""
        return dict(self._tier_map)
