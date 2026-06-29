"""Tests for Plugin Manager interfaces — abstract nature and method contracts."""

from __future__ import annotations

import abc

from adip.plugins.interfaces import (
    CapabilityDiscoverer,
    DependencyResolver,
    LifecycleManager,
    PluginCoordinator,
    PluginHealthChecker,
    PluginLoader,
    PluginManager,
    PluginService,
    PluginValidator,
    SandboxManager,
    VersionManager,
)


class TestInterfacesAreAbstract:
    def test_plugin_service_is_abstract(self) -> None:
        assert issubclass(PluginService, abc.ABC)

    def test_plugin_manager_is_abstract(self) -> None:
        assert issubclass(PluginManager, abc.ABC)

    def test_plugin_coordinator_is_abstract(self) -> None:
        assert issubclass(PluginCoordinator, abc.ABC)

    def test_plugin_loader_is_abstract(self) -> None:
        assert issubclass(PluginLoader, abc.ABC)

    def test_plugin_validator_is_abstract(self) -> None:
        assert issubclass(PluginValidator, abc.ABC)

    def test_dependency_resolver_is_abstract(self) -> None:
        assert issubclass(DependencyResolver, abc.ABC)

    def test_capability_discoverer_is_abstract(self) -> None:
        assert issubclass(CapabilityDiscoverer, abc.ABC)

    def test_lifecycle_manager_is_abstract(self) -> None:
        assert issubclass(LifecycleManager, abc.ABC)

    def test_version_manager_is_abstract(self) -> None:
        assert issubclass(VersionManager, abc.ABC)

    def test_sandbox_manager_is_abstract(self) -> None:
        assert issubclass(SandboxManager, abc.ABC)

    def test_plugin_health_checker_is_abstract(self) -> None:
        assert issubclass(PluginHealthChecker, abc.ABC)


class TestInterfaceMethods:
    def test_plugin_service_methods(self) -> None:
        methods = [
            "discover_plugin", "install_plugin", "get_plugin",
            "update_plugin", "uninstall_plugin", "list_plugins",
            "activate_plugin", "suspend_plugin", "load_plugin",
            "unload_plugin", "create_sandbox", "destroy_sandbox",
            "get_sandbox", "health", "get_metrics",
        ]
        for method in methods:
            assert hasattr(PluginService, method), f"Missing: {method}"
            assert getattr(PluginService, method).__isabstractmethod__

    def test_plugin_manager_methods(self) -> None:
        methods = [
            "install_plugin", "read_plugin", "update_plugin",
            "uninstall_plugin", "list_plugins", "activate_plugin",
            "suspend_plugin", "load_plugin", "unload_plugin",
            "create_sandbox", "destroy_sandbox", "get_sandbox",
            "discover_plugin", "get_health", "get_metrics",
        ]
        for method in methods:
            assert hasattr(PluginManager, method), f"Missing: {method}"
            assert getattr(PluginManager, method).__isabstractmethod__

    def test_plugin_coordinator_methods(self) -> None:
        methods = [
            "install_plugin", "get_plugin", "update_plugin",
            "uninstall_plugin", "list_plugins", "activate_plugin",
            "suspend_plugin", "load_plugin", "unload_plugin",
            "discover_plugin", "create_sandbox", "destroy_sandbox",
            "get_sandbox", "health", "metrics",
        ]
        for method in methods:
            assert hasattr(PluginCoordinator, method), f"Missing: {method}"
            assert getattr(PluginCoordinator, method).__isabstractmethod__

    def test_plugin_loader_methods(self) -> None:
        methods = ["load", "load_from_module", "get_supported_sources"]
        for method in methods:
            assert hasattr(PluginLoader, method)
            assert getattr(PluginLoader, method).__isabstractmethod__

    def test_plugin_validator_methods(self) -> None:
        methods = ["validate_manifest", "validate_configuration", "validate_plugin", "validate_sandbox"]
        for method in methods:
            assert hasattr(PluginValidator, method)
            assert getattr(PluginValidator, method).__isabstractmethod__

    def test_dependency_resolver_methods(self) -> None:
        methods = ["resolve", "check_compatibility", "detect_circular_dependencies"]
        for method in methods:
            assert hasattr(DependencyResolver, method)
            assert getattr(DependencyResolver, method).__isabstractmethod__

    def test_capability_discoverer_methods(self) -> None:
        methods = ["discover_capabilities", "get_capability", "list_capabilities"]
        for method in methods:
            assert hasattr(CapabilityDiscoverer, method)
            assert getattr(CapabilityDiscoverer, method).__isabstractmethod__

    def test_lifecycle_manager_methods(self) -> None:
        methods = ["transition", "get_current_status", "is_transition_allowed", "get_transition_history"]
        for method in methods:
            assert hasattr(LifecycleManager, method)
            assert getattr(LifecycleManager, method).__isabstractmethod__

    def test_version_manager_methods(self) -> None:
        methods = ["register_version", "get_latest_version", "list_versions", "satisfies_constraint"]
        for method in methods:
            assert hasattr(VersionManager, method)
            assert getattr(VersionManager, method).__isabstractmethod__

    def test_sandbox_manager_methods(self) -> None:
        methods = ["create_sandbox", "destroy_sandbox", "get_sandbox", "get_sandbox_by_plugin", "list_sandboxes"]
        for method in methods:
            assert hasattr(SandboxManager, method)
            assert getattr(SandboxManager, method).__isabstractmethod__

    def test_plugin_health_checker_methods(self) -> None:
        methods = ["check_health", "check_all", "get_health_summary"]
        for method in methods:
            assert hasattr(PluginHealthChecker, method)
            assert getattr(PluginHealthChecker, method).__isabstractmethod__
