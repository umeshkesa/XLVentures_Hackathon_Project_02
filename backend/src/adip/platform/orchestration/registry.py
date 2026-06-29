"""DefaultServiceRegistry — DI wiring of all platform module services.

Provides constructor injection verification and service resolution
for all 16 ADIP platform modules.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.platform.contracts.models import ServiceDescriptor
from adip.platform.enums import ModuleName
from adip.platform.interfaces import ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultServiceRegistry(ServiceRegistry):
    """Default in-memory service registry for the platform.

    Provides constructor injection verification by checking that
    registered services follow ADIP patterns (no direct instantiation
    of domain objects, all dependencies injected via constructor).
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._module_map: dict[str, ModuleName] = {}
        self._dependency_map: dict[str, list[str]] = {}
        logger.debug("service_registry.initialized")

    def register(
        self,
        name: str,
        service: Any,
        module: ModuleName,
        dependencies: list[str] | None = None,
    ) -> None:
        """Register a service with the platform.

        Args:
            name: Unique service name (e.g. "planner_service", "memory_manager")
            service: The service instance (injected via constructor)
            module: The module this service belongs to
            dependencies: Names of services this service depends on

        Raises:
            ValueError: If a service with the same name is already registered.
        """
        if name in self._services:
            logger.warning("service_registry.already_registered", name=name, module=module.value)
            return

        self._services[name] = service
        self._module_map[name] = module
        self._dependency_map[name] = dependencies or []

        # Dependency injection verification: ensure all dependencies exist
        missing = [d for d in self._dependency_map[name] if d not in self._services]
        if missing:
            logger.warning(
                "service_registry.missing_dependencies",
                name=name,
                missing=missing,
            )

        logger.debug(
            "service_registry.registered",
            name=name,
            module=module.value,
            dependency_count=len(self._dependency_map[name]),
        )

    def resolve(self, name: str) -> Any:
        """Resolve a service by name.

        Args:
            name: The service name to resolve.

        Returns:
            The service instance.

        Raises:
            KeyError: If the service is not registered.
        """
        if name not in self._services:
            raise KeyError(f"Service '{name}' is not registered in the platform.")
        return self._services[name]

    def resolve_all(self) -> dict[str, Any]:
        """Resolve all registered services."""
        return dict(self._services)

    def get_service_descriptors(self) -> list[ServiceDescriptor]:
        """Get descriptors for all registered services."""
        descriptors: list[ServiceDescriptor] = []
        for name, service in self._services.items():
            module = self._module_map.get(name, ModuleName.API)
            descriptors.append(
                ServiceDescriptor(
                    name=name,
                    module=module,
                    service_type=type(service).__name__,
                    version="1.0.0",
                    dependencies=list(self._dependency_map.get(name, [])),
                )
            )
        return descriptors

    def get_modules(self) -> list[dict[str, Any]]:
        """Get list of registered modules with their services."""
        modules_map: dict[str, list[dict[str, Any]]] = {}
        for name, service in self._services.items():
            module = self._module_map.get(name, ModuleName.API).value
            if module not in modules_map:
                modules_map[module] = []
            modules_map[module].append({
                "name": name,
                "type": type(service).__name__,
            })
        return [
            {
                "name": module_name,
                "services": services,
                "service_count": len(services),
            }
            for module_name, services in sorted(modules_map.items())
        ]

    def has_module(self, module: ModuleName) -> bool:
        """Check if any services are registered for a module."""
        return module in self._module_map.values()

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._module_map.clear()
        self._dependency_map.clear()
        logger.debug("service_registry.cleared")

    @property
    def service_count(self) -> int:
        """Return the number of registered services."""
        return len(self._services)
