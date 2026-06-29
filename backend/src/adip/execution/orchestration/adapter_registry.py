"""ExecutionAdapterRegistry — registry of available execution adapters.

Deterministic placeholder providing a registry of adapter
capabilities for the execution engine. Maps adapter types
to their supported capabilities and configurations.
"""

from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)


class AdapterInfo:
    """Information about a registered adapter."""

    def __init__(
        self,
        adapter_type: str,
        name: str = "",
        capabilities: list[str] | None = None,
        version: str = "1.0.0",
        enabled: bool = True,
    ) -> None:
        self.adapter_type = adapter_type
        self.name = name or adapter_type
        self.capabilities = capabilities or []
        self.version = version
        self.enabled = enabled


class ExecutionAdapterRegistry:
    """Registry of available execution adapters.

    Manages adapter registration, discovery, and capability
    lookup for the execution engine.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, AdapterInfo] = {}

    def register_adapter(
        self,
        adapter_type: str,
        name: str = "",
        capabilities: list[str] | None = None,
        version: str = "1.0.0",
        correlation_id: str = "",
    ) -> bool:
        """Register an adapter type.

        Args:
            adapter_type: The adapter type identifier.
            name: Optional human-readable name.
            capabilities: Optional list of capabilities.
            version: Adapter version string.
            correlation_id: Optional correlation ID.

        Returns:
            True if registered, False if already registered.
        """
        if adapter_type in self._adapters:
            log.warning(
                "adapter.already_registered",
                adapter_type=adapter_type,
                cid=correlation_id,
            )
            return False

        self._adapters[adapter_type] = AdapterInfo(
            adapter_type=adapter_type,
            name=name or adapter_type,
            capabilities=capabilities or [],
            version=version,
        )
        log.info(
            "adapter.registered",
            adapter_type=adapter_type,
            capabilities=len(capabilities or []),
            cid=correlation_id,
        )
        return True

    def unregister_adapter(
        self,
        adapter_type: str,
        correlation_id: str = "",
    ) -> bool:
        """Unregister an adapter type.

        Args:
            adapter_type: The adapter type to unregister.
            correlation_id: Optional correlation ID.

        Returns:
            True if unregistered, False if not found.
        """
        if adapter_type not in self._adapters:
            return False
        del self._adapters[adapter_type]
        log.info(
            "adapter.unregistered",
            adapter_type=adapter_type,
            cid=correlation_id,
        )
        return True

    def get_adapter(self, adapter_type: str) -> AdapterInfo | None:
        """Get adapter info by type.

        Args:
            adapter_type: The adapter type identifier.

        Returns:
            AdapterInfo if found, None otherwise.
        """
        return self._adapters.get(adapter_type)

    def has_adapter(self, adapter_type: str) -> bool:
        """Check if an adapter type is registered.

        Args:
            adapter_type: The adapter type identifier.

        Returns:
            True if registered, False otherwise.
        """
        return adapter_type in self._adapters

    def get_available_adapters(self) -> list[str]:
        """Get all registered adapter types.

        Returns:
            List of adapter type strings.
        """
        return list(self._adapters.keys())

    def get_capabilities_for(self, adapter_type: str) -> list[str]:
        """Get capabilities for an adapter type.

        Args:
            adapter_type: The adapter type identifier.

        Returns:
            List of capability strings, empty if not found.
        """
        adapter = self._adapters.get(adapter_type)
        return list(adapter.capabilities) if adapter else []

    def count(self) -> int:
        """Get the number of registered adapters.

        Returns:
            Adapter count.
        """
        return len(self._adapters)
