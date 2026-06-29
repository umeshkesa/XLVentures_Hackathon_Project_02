"""Tests for Plugin Manager package imports and re-exports."""

from __future__ import annotations


class TestTopLevelImports:
    def test_all_imports(self) -> None:
        from adip.plugins import (  # noqa: F811
            AbstractPluginService,
            Plugin,
            PluginDiscovered,
            PluginDomain,
            PluginException,
        )
        assert Plugin is not None
        assert PluginDomain is not None
        assert AbstractPluginService is not None
        assert PluginDiscovered is not None
        assert PluginException is not None

    def test_enums_importable(self) -> None:
        from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType
        assert PluginType.DOMAIN == "DOMAIN"
        assert PluginLifecycleStatus.DISCOVERED == "DISCOVERED"
        assert PluginDomain.ENERGY == "ENERGY"

    def test_models_importable(self) -> None:
        from adip.plugins.contracts.models import (
            Plugin,
            PluginCapability,
            PluginDependency,
            PluginNamespace,
            PluginPolicy,
            PluginSandbox,
        )
        assert Plugin is not None
        assert PluginCapability is not None
        assert PluginSandbox is not None
        assert PluginPolicy is not None
        assert PluginNamespace is not None
        assert PluginDependency is not None

    def test_events_importable(self) -> None:
        from adip.plugins.contracts.events import (
            PluginDiscovered,
            SandboxCreated,
        )
        assert PluginDiscovered is not None
        assert SandboxCreated is not None

    def test_dtos_importable(self) -> None:
        from adip.plugins.dtos import (
            PluginRequestDTO,
            PluginSandboxDTO,
        )
        assert PluginRequestDTO is not None
        assert PluginSandboxDTO is not None

    def test_exceptions_importable(self) -> None:
        from adip.plugins.contracts.exceptions import (
            PluginException,
            SandboxException,
        )
        assert PluginException is not None
        assert SandboxException is not None

    def test_interfaces_importable(self) -> None:
        from adip.plugins.interfaces import (
            PluginCoordinator as AbstractPluginCoordinator,
        )
        from adip.plugins.interfaces import (
            PluginManager as AbstractPluginManager,
        )
        from adip.plugins.interfaces import (
            PluginService as AbstractPluginService,
        )
        assert AbstractPluginService is not None
        assert AbstractPluginManager is not None
        assert AbstractPluginCoordinator is not None


class TestAllNames:
    def test_all_names_in_all(self) -> None:
        from adip.plugins import __all__ as top_all
        expected = {
            "PluginType", "PluginLifecycleStatus", "PluginDomain",
            "Plugin", "PluginManifest", "PluginMetadata",
            "PluginCapability", "PluginDependency",
            "PluginConfiguration", "PluginHealth", "PluginMetrics",
            "PluginSession", "PluginDecision",
            "PluginSandbox", "PluginNamespace", "PluginPolicy",
            "PluginRequestDTO", "PluginResponseDTO",
            "PluginInstallDTO", "PluginDiscoveryDTO", "PluginSandboxDTO",
            "EventVersion", "PluginEvent",
            "PluginDiscovered", "PluginValidated", "PluginInstalled",
            "PluginLoaded", "PluginActivated", "PluginSuspended",
            "PluginUnloaded", "PluginRemoved",
            "SandboxCreated", "SandboxDestroyed",
            "PluginException", "PluginValidationException",
            "PluginDependencyException", "PluginLoadException",
            "SandboxException",
            "AbstractPluginService", "AbstractPluginManager",
            "AbstractPluginCoordinator", "AbstractPluginLoader",
            "AbstractPluginValidator", "AbstractDependencyResolver",
            "AbstractCapabilityDiscoverer", "AbstractLifecycleManager",
            "AbstractVersionManager", "AbstractSandboxManager",
            "AbstractPluginHealthChecker",
            # Execution Models (Phase 2)
            "DiscoveryResult",
            "DependencyGraph",
            "DependencyNode",
            "CompatibilityResult",
            "LoaderResult",
            "InitializationResult",
            "ResourceUsage",
            "LifecycleHistoryEntry",
            "CapabilityRecord",
            "TraceRecord",
            # Execution Components (Phase 2)
            "PluginDiscoverer",
            "PluginValidator",
            "DependencyResolver",
            "PluginDependencyGraph",
            "PluginCompatibilityManager",
            "PluginLoader",
            "PluginInitializer",
            "PluginSandboxManager",
            "PluginResourceManager",
            "PluginLifecycleManager",
            "CapabilityRegistration",
            "PluginCache",
            "PluginPolicyEngine",
            "PluginTrace",
            "PluginMetricsCollector",
            # Orchestration (Phase 3)
            "PluginCoordinator",
            "OrchestrationPluginManager",
            "PluginSessionManager",
            "PluginConfidenceCalculator",
            # Services (Phase 3)
            "IntegrationHooks",
            "global_hooks",
            "PluginService",
            "AuthResult",
        }
        assert set(top_all) == expected
