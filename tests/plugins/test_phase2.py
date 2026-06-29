"""Tests for Plugin Manager Phase 2 — Plugin Processing & Lifecycle Pipeline.

Tests cover all 15 execution components with deterministic placeholder
behaviour: PluginDiscoverer, PluginValidator, DependencyResolver,
PluginDependencyGraph, PluginCompatibilityManager, PluginLoader,
PluginInitializer, PluginSandboxManager, PluginResourceManager,
PluginLifecycleManager, CapabilityRegistration, PluginCache,
PluginPolicyEngine, PluginTrace, PluginMetricsCollector.
"""

from __future__ import annotations

import uuid

import pytest

from adip.plugins.contracts.models import (
    Plugin,
    PluginCapability,
    PluginConfiguration,
    PluginDependency,
    PluginManifest,
    PluginNamespace,
    PluginPolicy,
    PluginSandbox,
)
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType
from adip.plugins.execution.cache import PluginCache
from adip.plugins.execution.capability_registration import CapabilityRegistration
from adip.plugins.execution.compatibility_manager import PluginCompatibilityManager
from adip.plugins.execution.dependency_graph import PluginDependencyGraph
from adip.plugins.execution.dependency_resolver import DependencyResolver
from adip.plugins.execution.discoverer import PluginDiscoverer
from adip.plugins.execution.initializer import PluginInitializer
from adip.plugins.execution.lifecycle_manager import PluginLifecycleManager
from adip.plugins.execution.loader import PluginLoader
from adip.plugins.execution.metrics import PluginMetricsCollector
from adip.plugins.execution.models import (
    CapabilityRecord,
    CompatibilityResult,
    DependencyGraph,
    DependencyNode,
    DiscoveryResult,
    InitializationResult,
    LifecycleHistoryEntry,
    LoaderResult,
    ResourceUsage,
    TraceRecord,
)
from adip.plugins.execution.policy import PluginPolicyEngine
from adip.plugins.execution.resource_manager import PluginResourceManager
from adip.plugins.execution.sandbox_manager import PluginSandboxManager
from adip.plugins.execution.trace import PluginTrace
from adip.plugins.execution.validator import PluginValidator

# ═════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_manifest() -> PluginManifest:
    return PluginManifest(
        plugin_name="test-plugin",
        plugin_version="1.0.0",
        plugin_type=PluginType.DOMAIN,
        plugin_domain=PluginDomain.GENERAL,
        capabilities=[
            PluginCapability(name="search", category="core"),
            PluginCapability(name="analyze", category="analytics"),
        ],
        dependencies=[
            PluginDependency(plugin_name="base-plugin", version_constraint=">=1.0.0"),
        ],
    )


@pytest.fixture
def sample_plugin(sample_manifest: PluginManifest) -> Plugin:
    return Plugin(
        name="test-plugin",
        version="1.0.0",
        plugin_type=PluginType.DOMAIN,
        domain=PluginDomain.GENERAL,
        status=PluginLifecycleStatus.DISCOVERED,
        manifest=sample_manifest,
        namespace="test-ns",
    )


@pytest.fixture
def available_plugins() -> list[Plugin]:
    base = Plugin(
        name="base-plugin",
        version="2.0.0",
        plugin_type=PluginType.DOMAIN,
        domain=PluginDomain.GENERAL,
        manifest=PluginManifest(
            plugin_name="base-plugin",
            plugin_version="2.0.0",
            plugin_type=PluginType.DOMAIN,
        ),
    )
    utils = Plugin(
        name="utils-plugin",
        version="1.5.0",
        plugin_type=PluginType.TOOL,
        domain=PluginDomain.GENERAL,
        manifest=PluginManifest(
            plugin_name="utils-plugin",
            plugin_version="1.5.0",
            plugin_type=PluginType.TOOL,
        ),
    )
    return [base, utils]


@pytest.fixture
def lifecycle_plugin() -> Plugin:
    return Plugin(
        name="lifecycle-test",
        version="1.0.0",
        plugin_type=PluginType.DOMAIN,
        domain=PluginDomain.GENERAL,
        status=PluginLifecycleStatus.DISCOVERED,
    )


# ═════════════════════════════════════════════════════════════════════════════
# Execution Models
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionModels:
    def test_discovery_result_defaults(self) -> None:
        result = DiscoveryResult(source="test", source_type="local_directory")
        assert result.source == "test"
        assert result.source_type == "local_directory"
        assert result.plugin_name == ""
        assert result.plugin_version == ""
        assert result.plugin_type is None
        assert result.domain == PluginDomain.GENERAL
        assert result.discovery_id is not None

    def test_dependency_graph_creation(self) -> None:
        graph = DependencyGraph(nodes={"a": ["b"], "b": []})
        assert "a" in graph.nodes
        assert graph.nodes["a"] == ["b"]
        assert graph.nodes["b"] == []

    def test_dependency_node_defaults(self) -> None:
        node = DependencyNode(plugin_id="p1")
        assert node.plugin_id == "p1"
        assert node.plugin_name == ""
        assert node.resolved is False
        assert node.level == 0
        assert node.dependencies == []
        assert node.dependents == []

    def test_compatibility_result_defaults(self) -> None:
        result = CompatibilityResult(plugin_name="test")
        assert result.compatible is True
        assert result.platform_version_compatible is True
        assert result.manifest_version_compatible is True
        assert result.reasons == []

    def test_compatibility_result_failure(self) -> None:
        result = CompatibilityResult(
            plugin_name="test",
            compatible=False,
            platform_version_compatible=False,
            reasons=["Platform version mismatch"],
        )
        assert result.compatible is False
        assert result.platform_version_compatible is False
        assert len(result.reasons) == 1

    def test_loader_result_defaults(self) -> None:
        result = LoaderResult(plugin_id=uuid.uuid4(), plugin_name="test")
        assert result.success is True
        assert result.validated is False
        assert result.dependencies_resolved is False
        assert result.errors == []

    def test_loader_result_failure(self) -> None:
        result = LoaderResult(
            plugin_id=uuid.uuid4(),
            plugin_name="test",
            success=False,
            errors=["Validation failed"],
        )
        assert result.success is False
        assert len(result.errors) == 1

    def test_initialization_result_defaults(self) -> None:
        result = InitializationResult(plugin_id=uuid.uuid4())
        assert result.success is True
        assert result.config_loaded is False
        assert result.lifecycle_transitioned is False
        assert result.errors == []

    def test_resource_usage_defaults(self) -> None:
        usage = ResourceUsage(plugin_id=uuid.uuid4())
        assert usage.cpu_percent == 0.0
        assert usage.memory_mb == 0.0
        assert usage.timeout_seconds == 30.0
        assert usage.agent_count == 0
        assert usage.tool_count == 0

    def test_lifecycle_history_entry_defaults(self) -> None:
        entry = LifecycleHistoryEntry(
            plugin_id=uuid.uuid4(),
            to_status=PluginLifecycleStatus.ACTIVE,
        )
        assert entry.to_status == PluginLifecycleStatus.ACTIVE
        assert entry.from_status is None
        assert entry.reason == ""

    def test_capability_record_defaults(self) -> None:
        record = CapabilityRecord(
            capability_id=uuid.uuid4(),
            plugin_id=uuid.uuid4(),
            name="search",
            category="core",
        )
        assert record.name == "search"
        assert record.status == "registered"
        assert record.registered_at is not None

    def test_trace_record_defaults(self) -> None:
        record = TraceRecord(stage_name="validation", operation="validate")
        assert record.stage_name == "validation"
        assert record.operation == "validate"
        assert record.success is True
        assert record.warnings == []
        assert record.errors == []
        assert record.duration_ms is None

    def test_trace_record_with_context(self) -> None:
        record = TraceRecord(
            stage_name="discovery",
            operation="discover",
            plugin_id="p1",
            domain="GENERAL",
            duration_ms=150.5,
        )
        assert record.plugin_id == "p1"
        assert record.domain == "GENERAL"
        assert record.duration_ms == 150.5


# ═════════════════════════════════════════════════════════════════════════════
# PluginDiscoverer
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginDiscoverer:
    def test_discover_from_directory(self) -> None:
        d = PluginDiscoverer()
        result = d.discover_from_directory("/path/to/my-plugin")
        assert result.plugin_name == "my-plugin"
        assert result.source_type == "local_directory"
        assert result.plugin_version == "1.0.0"

    def test_discover_from_package(self) -> None:
        d = PluginDiscoverer()
        result = d.discover_from_package("adip-plugin-energy")
        assert result.plugin_name == "adip-plugin-energy"
        assert result.source_type == "installed_package"

    def test_discover_from_repository(self) -> None:
        d = PluginDiscoverer()
        result = d.discover_from_repository("https://github.com/example/my-plugin")
        assert result.source_type == "plugin_repository"
        assert result.plugin_name == "my-plugin"

    def test_discover_from_zip(self) -> None:
        d = PluginDiscoverer()
        result = d.discover_from_zip("/tmp/my-plugin.zip")
        assert result.source_type == "zip_package"
        assert result.plugin_version == "1.0.0"

    def test_discover_auto_detect(self) -> None:
        d = PluginDiscoverer()
        repo_result = d.discover("https://github.com/example/p")
        assert repo_result.source_type == "plugin_repository"

        zip_result = d.discover("/tmp/p.zip")
        assert zip_result.source_type == "zip_package"

        dir_result = d.discover("/some/local/path")
        assert dir_result.source_type == "local_directory"

    def test_discover_with_explicit_type(self) -> None:
        d = PluginDiscoverer()
        result = d.discover("some-path", source_type="installed_package")
        assert result.source_type == "installed_package"

    def test_get_supported_sources(self) -> None:
        d = PluginDiscoverer()
        sources = d.get_supported_sources()
        assert "local_directory" in sources
        assert "installed_package" in sources
        assert "plugin_repository" in sources
        assert "zip_package" in sources

    def test_convert_to_plugin(self) -> None:
        d = PluginDiscoverer()
        result = DiscoveryResult(
            plugin_name="test",
            plugin_version="2.0.0",
            plugin_type=PluginType.AGENT,
            domain=PluginDomain.ENERGY,
            source="test-source",
            source_type="local_directory",
        )
        plugin = d.convert_to_plugin(result)
        assert plugin.name == "test"
        assert plugin.version == "2.0.0"
        assert plugin.plugin_type == PluginType.AGENT
        assert plugin.domain == PluginDomain.ENERGY
        assert plugin.status == PluginLifecycleStatus.DISCOVERED

    def test_unknown_source_type(self) -> None:
        d = PluginDiscoverer()
        result = d.discover("some-value", source_type="unknown_type")
        assert result.source_type == "unknown"

    def test_zip_path_without_extension(self) -> None:
        d = PluginDiscoverer()
        result = d.discover("/path/to/plugin.tar.gz")
        assert result.source_type == "local_directory"  # not .zip


# ═════════════════════════════════════════════════════════════════════════════
# PluginValidator
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginValidator:
    def test_validate_valid_manifest(self, sample_manifest: PluginManifest) -> None:
        v = PluginValidator()
        violations = v.validate_manifest(sample_manifest)
        assert violations == []

    def test_validate_manifest_missing_name(self) -> None:
        v = PluginValidator()
        manifest = PluginManifest(
            plugin_name="",
            plugin_version="1.0.0",
            plugin_type=PluginType.DOMAIN,
        )
        violations = v.validate_manifest(manifest)
        assert any("name" in v.lower() for v in violations)

    def test_validate_manifest_missing_version(self) -> None:
        v = PluginValidator()
        manifest = PluginManifest(
            plugin_name="test",
            plugin_version="",
            plugin_type=PluginType.DOMAIN,
        )
        violations = v.validate_manifest(manifest)
        assert any("version" in v.lower() for v in violations)

    def test_validate_configuration_valid(self) -> None:
        v = PluginValidator()
        config = PluginConfiguration(plugin_id=uuid.uuid4(), version=1)
        violations = v.validate_configuration(config)
        assert violations == []

    def test_validate_configuration_invalid_version(self) -> None:
        v = PluginValidator()
        config = PluginConfiguration.model_construct(plugin_id=uuid.uuid4(), version=0)
        violations = v.validate_configuration(config)
        assert len(violations) == 1

    def test_validate_namespace(self) -> None:
        v = PluginValidator()
        ns = PluginNamespace(plugin_id=uuid.uuid4(), name="my-ns")
        violations = v.validate_namespace(ns)
        assert violations == []

    def test_validate_namespace_empty_name(self) -> None:
        v = PluginValidator()
        ns = PluginNamespace(plugin_id=uuid.uuid4(), name="")
        violations = v.validate_namespace(ns)
        assert len(violations) == 1

    def test_validate_dependencies(self) -> None:
        v = PluginValidator()
        deps = [PluginDependency(plugin_name="base", version_constraint=">=1.0.0")]
        violations = v.validate_dependencies(deps)
        assert violations == []

    def test_validate_dependencies_empty_name(self) -> None:
        v = PluginValidator()
        deps = [PluginDependency(plugin_name="", version_constraint=">=1.0.0")]
        violations = v.validate_dependencies(deps)
        assert len(violations) == 1

    def test_validate_capabilities(self) -> None:
        v = PluginValidator()
        caps = [PluginCapability(name="search", category="core")]
        violations = v.validate_capabilities(caps)
        assert violations == []

    def test_validate_capabilities_empty_name(self) -> None:
        v = PluginValidator()
        caps = [PluginCapability(name="", category="core")]
        violations = v.validate_capabilities(caps)
        assert len(violations) == 1

    def test_validate_capabilities_empty_category(self) -> None:
        v = PluginValidator()
        caps = [PluginCapability(name="search", category="")]
        violations = v.validate_capabilities(caps)
        assert len(violations) == 1

    def test_validate_sandbox_valid(self) -> None:
        v = PluginValidator()
        sandbox = PluginSandbox(
            plugin_id=uuid.uuid4(),
            namespace="test-ns",
            isolation_policy="strict",
        )
        violations = v.validate_sandbox(sandbox)
        assert violations == []

    def test_validate_sandbox_invalid_policy(self) -> None:
        v = PluginValidator()
        sandbox = PluginSandbox(
            plugin_id=uuid.uuid4(),
            namespace="test-ns",
            isolation_policy="invalid",
        )
        violations = v.validate_sandbox(sandbox)
        assert len(violations) == 1

    def test_validate_sandbox_empty_namespace(self) -> None:
        v = PluginValidator()
        sandbox = PluginSandbox(
            plugin_id=uuid.uuid4(),
            namespace="",
        )
        violations = v.validate_sandbox(sandbox)
        assert len(violations) == 1

    def test_validate_plugin_valid(self, sample_plugin: Plugin) -> None:
        v = PluginValidator()
        violations = v.validate_plugin(sample_plugin)
        assert violations == []

    def test_validate_plugin_missing_name(self) -> None:
        v = PluginValidator()
        plugin = Plugin(name="", version="1.0.0")
        violations = v.validate_plugin(plugin)
        assert any("name" in v.lower() for v in violations)

    def test_validate_lifecycle_transition_valid(self) -> None:
        v = PluginValidator()
        violations = v.validate_lifecycle_transition(
            PluginLifecycleStatus.DISCOVERED,
            PluginLifecycleStatus.VALIDATED,
        )
        assert violations == []

    def test_validate_policy_valid(self) -> None:
        v = PluginValidator()
        policy = PluginPolicy(plugin_id=uuid.uuid4(), name="test-policy")
        violations = v.validate_policy(policy)
        assert violations == []

    def test_validate_policy_empty_name(self) -> None:
        v = PluginValidator()
        policy = PluginPolicy(plugin_id=uuid.uuid4(), name="")
        violations = v.validate_policy(policy)
        assert len(violations) == 1


# ═════════════════════════════════════════════════════════════════════════════
# DependencyResolver
# ═════════════════════════════════════════════════════════════════════════════


class TestDependencyResolver:
    def test_resolve_satisfied(self, sample_plugin: Plugin, available_plugins: list[Plugin]) -> None:
        r = DependencyResolver()
        satisfied = r.resolve(sample_plugin, available_plugins)
        assert len(satisfied) == 1

    def test_resolve_no_manifest(self) -> None:
        r = DependencyResolver()
        plugin = Plugin(name="no-manifest", version="1.0.0")
        satisfied = r.resolve(plugin, [])
        assert satisfied == []

    def test_resolve_missing_dependency(self, sample_manifest: PluginManifest) -> None:
        r = DependencyResolver()
        plugin = Plugin(name="test", version="1.0.0", manifest=sample_manifest)
        satisfied = r.resolve(plugin, [])
        assert satisfied == []

    def test_find_missing(self, sample_manifest: PluginManifest) -> None:
        r = DependencyResolver()
        plugin = Plugin(name="test", version="1.0.0", manifest=sample_manifest)
        missing = r.find_missing(plugin, [])
        assert len(missing) == 1
        assert missing[0].plugin_name == "base-plugin"

    def test_find_missing_no_manifest(self) -> None:
        r = DependencyResolver()
        plugin = Plugin(name="test", version="1.0.0")
        missing = r.find_missing(plugin, [])
        assert missing == []

    def test_detect_cycles_no_cycles(self) -> None:
        r = DependencyResolver()
        plugins = [
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
            Plugin(
                name="b", version="1.0.0",
                manifest=PluginManifest(plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
        ]
        cycles = r.detect_cycles(plugins)
        assert cycles == []

    def test_detect_cycles_with_cycle(self) -> None:
        r = DependencyResolver()
        plugins = [
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(
                name="b", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="a", version_constraint=">=1.0.0")],
                ),
            ),
        ]
        cycles = r.detect_cycles(plugins)
        assert len(cycles) > 0

    def test_build_graph(self, available_plugins: list[Plugin]) -> None:
        r = DependencyResolver()
        graph = r.build_graph(available_plugins)
        assert isinstance(graph, DependencyGraph)
        assert "base-plugin" in graph.nodes

    def test_get_load_order(self) -> None:
        r = DependencyResolver()
        plugins = [
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(
                name="b", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                ),
            ),
        ]
        order = r.get_load_order(plugins)
        assert order.index("b") < order.index("a")


# ═════════════════════════════════════════════════════════════════════════════
# PluginDependencyGraph
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginDependencyGraph:
    def test_create(self, available_plugins: list[Plugin]) -> None:
        g = PluginDependencyGraph()
        graph = g.create(available_plugins)
        assert isinstance(graph, DependencyGraph)
        assert "base-plugin" in graph.nodes

    def test_detect_cycles_no_graph(self) -> None:
        g = PluginDependencyGraph()
        cycles = g.detect_cycles()
        assert cycles == []

    def test_detect_cycles_clean(self, available_plugins: list[Plugin]) -> None:
        g = PluginDependencyGraph()
        g.create(available_plugins)
        cycles = g.detect_cycles()
        assert cycles == []

    def test_detect_cycles_with_cycle(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(
                name="b", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="a", version_constraint=">=1.0.0")],
                ),
            ),
        ])
        cycles = g.detect_cycles()
        assert len(cycles) > 0

    def test_has_cycles(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(
                name="b", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="a", version_constraint=">=1.0.0")],
                ),
            ),
        ])
        assert g.has_cycles() is True

    def test_has_cycles_no_cycle(self, available_plugins: list[Plugin]) -> None:
        g = PluginDependencyGraph()
        g.create(available_plugins)
        assert g.has_cycles() is False

    def test_compute_load_order(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(
                name="b", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                ),
            ),
        ])
        order = g.compute_load_order()
        assert order.index("b") < order.index("a")

    def test_compute_load_order_no_graph(self) -> None:
        g = PluginDependencyGraph()
        assert g.compute_load_order() == []

    def test_get_parents(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(name="b", version="1.0.0",
                manifest=PluginManifest(plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
        ])
        parents = g.get_parents("b")
        assert "a" in parents

    def test_get_children(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(name="b", version="1.0.0",
                manifest=PluginManifest(plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
        ])
        children = g.get_children("a")
        assert "b" in children

    def test_get_children_nonexistent(self) -> None:
        g = PluginDependencyGraph()
        assert g.get_children("nonexistent") == []

    def test_get_dependency_tree(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(
                name="a", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="b", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(
                name="b", version="1.0.0",
                manifest=PluginManifest(
                    plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
                    dependencies=[PluginDependency(plugin_name="c", version_constraint=">=1.0.0")],
                ),
            ),
            Plugin(name="c", version="1.0.0",
                manifest=PluginManifest(plugin_name="c", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
        ])
        tree = g.get_dependency_tree("a")
        assert 0 in tree
        assert 1 in tree
        assert "a" in tree[0]

    def test_get_node(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(name="a", version="1.0.0",
                manifest=PluginManifest(plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
        ])
        node = g.get_node("a")
        assert node is not None
        assert node.plugin_name == "a"

    def test_get_node_nonexistent(self) -> None:
        g = PluginDependencyGraph()
        assert g.get_node("nonexistent") is None

    def test_get_all_nodes(self) -> None:
        g = PluginDependencyGraph()
        g.create([
            Plugin(name="a", version="1.0.0",
                manifest=PluginManifest(plugin_name="a", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
            Plugin(name="b", version="1.0.0",
                manifest=PluginManifest(plugin_name="b", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN),
            ),
        ])
        nodes = g.get_all_nodes()
        assert "a" in nodes
        assert "b" in nodes

    def test_clear(self, available_plugins: list[Plugin]) -> None:
        g = PluginDependencyGraph()
        g.create(available_plugins)
        g.clear()
        assert g.get_all_nodes() == {}
        assert g.compute_load_order() == []


# ═════════════════════════════════════════════════════════════════════════════
# PluginCompatibilityManager
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginCompatibilityManager:
    def test_check_compatibility_valid(self, sample_plugin: Plugin) -> None:
        c = PluginCompatibilityManager()
        result = c.check_compatibility(sample_plugin)
        assert isinstance(result, CompatibilityResult)
        assert result.plugin_name == "test-plugin"

    def test_check_compatibility_empty_version(self) -> None:
        c = PluginCompatibilityManager()
        plugin = Plugin(name="test", version="")
        result = c.check_compatibility(plugin)
        assert result.plugin_version_compatible is False

    def test_check_manifest_version_valid(self, sample_manifest: PluginManifest) -> None:
        c = PluginCompatibilityManager()
        assert c.check_manifest_version(sample_manifest) is True

    def test_check_manifest_version_invalid(self) -> None:
        c = PluginCompatibilityManager()
        manifest = PluginManifest(
            plugin_name="test",
            plugin_version="",
            plugin_type=PluginType.DOMAIN,
        )
        assert c.check_manifest_version(manifest) is False

    def test_check_api_version(self, sample_plugin: Plugin) -> None:
        c = PluginCompatibilityManager()
        assert c.check_api_version(sample_plugin) is True

    def test_check_plugin_version_valid(self, sample_plugin: Plugin) -> None:
        c = PluginCompatibilityManager()
        assert c.check_plugin_version(sample_plugin) is True

    def test_check_plugin_version_invalid(self) -> None:
        c = PluginCompatibilityManager()
        plugin = Plugin(name="test", version="")
        assert c.check_plugin_version(plugin) is False

    def test_check_dependency_versions(self, sample_plugin: Plugin) -> None:
        c = PluginCompatibilityManager()
        assert c.check_dependency_versions(sample_plugin) is True


# ═════════════════════════════════════════════════════════════════════════════
# PluginLoader
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginLoader:
    def test_load_success(self, sample_plugin: Plugin) -> None:
        ldr = PluginLoader()
        result = ldr.load(sample_plugin)
        assert isinstance(result, LoaderResult)
        assert result.success is True
        assert result.validated is True
        assert result.dependencies_resolved is True
        assert result.sandbox_created is True
        assert result.metadata_loaded is True
        assert result.capabilities_registered is True
        assert result.initialized is True
        assert result.activated is True

    def test_load_failure_empty_name(self) -> None:
        ldr = PluginLoader()
        plugin = Plugin(name="", version="1.0.0")
        result = ldr.load(plugin)
        assert result.success is False
        assert len(result.errors) > 0

    def test_load_failure_no_manifest(self) -> None:
        ldr = PluginLoader()
        plugin = Plugin(name="test", version="1.0.0")
        result = ldr.load(plugin)
        assert result.success is False

    def test_load_failure_no_version(self) -> None:
        ldr = PluginLoader()
        manifest = PluginManifest(plugin_name="test", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN)
        plugin = Plugin(name="test", version="", manifest=manifest)
        result = ldr.load(plugin)
        assert result.success is False


# ═════════════════════════════════════════════════════════════════════════════
# PluginInitializer
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginInitializer:
    def test_initialize_success(self, sample_plugin: Plugin) -> None:
        init = PluginInitializer()
        result = init.initialize(sample_plugin)
        assert isinstance(result, InitializationResult)
        assert result.success is True
        assert result.config_loaded is True
        assert result.namespace_prepared is True
        assert result.resources_allocated is True

    def test_initialize_with_config(self, sample_plugin: Plugin) -> None:
        init = PluginInitializer()
        config = PluginConfiguration(plugin_id=sample_plugin.plugin_id, version=1)
        result = init.initialize(sample_plugin, config=config)
        assert result.success is True
        assert result.config_loaded is True

    def test_initialize_with_invalid_config(self, sample_plugin: Plugin) -> None:
        init = PluginInitializer()
        config = PluginConfiguration.model_construct(plugin_id=sample_plugin.plugin_id, version=0)
        result = init.initialize(sample_plugin, config=config)
        assert result.success is False
        assert result.config_loaded is False

    def test_load_configuration_valid(self, sample_plugin: Plugin) -> None:
        init = PluginInitializer()
        config = PluginConfiguration(plugin_id=sample_plugin.plugin_id, version=1)
        ok, errors = init.load_configuration(sample_plugin, config=config)
        assert ok is True
        assert errors == []

    def test_load_configuration_none(self, sample_plugin: Plugin) -> None:
        init = PluginInitializer()
        ok, errors = init.load_configuration(sample_plugin, config=None)
        assert ok is True

    def test_prepare_namespace(self, sample_plugin: Plugin) -> None:
        init = PluginInitializer()
        ok, errors = init.prepare_namespace(sample_plugin)
        assert ok is True

    def test_allocate_resources(self, sample_plugin: Plugin) -> None:
        init = PluginInitializer()
        ok, errors = init.allocate_resources(sample_plugin)
        assert ok is True

    def test_validate_initialization_readiness_valid(self) -> None:
        init = PluginInitializer()
        plugin = Plugin(
            name="ready",
            version="1.0.0",
            status=PluginLifecycleStatus.LOADED,
        )
        violations = init.validate_initialization_readiness(plugin)
        assert violations == []

    def test_validate_initialization_readiness_wrong_status(self) -> None:
        init = PluginInitializer()
        plugin = Plugin(
            name="ready",
            version="1.0.0",
            status=PluginLifecycleStatus.DISCOVERED,
        )
        violations = init.validate_initialization_readiness(plugin)
        assert len(violations) == 1

    def test_validate_initialization_readiness_no_name(self) -> None:
        init = PluginInitializer()
        plugin = Plugin(
            name="",
            version="1.0.0",
            status=PluginLifecycleStatus.LOADED,
        )
        violations = init.validate_initialization_readiness(plugin)
        assert len(violations) == 1


# ═════════════════════════════════════════════════════════════════════════════
# PluginSandboxManager
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginSandboxManager:
    def test_create_sandbox(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        sandbox = sm.create_sandbox(sample_plugin)
        assert sandbox.plugin_id == sample_plugin.plugin_id
        assert sandbox.namespace == sample_plugin.namespace
        assert sandbox.isolation_policy == "strict"
        assert "memory_test-plugin" in sandbox.memory_namespace

    def test_create_sandbox_duplicate(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        first = sm.create_sandbox(sample_plugin)
        second = sm.create_sandbox(sample_plugin)
        assert first.sandbox_id == second.sandbox_id

    def test_destroy_sandbox(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        sandbox = sm.create_sandbox(sample_plugin)
        assert sm.destroy_sandbox(str(sandbox.sandbox_id)) is True
        assert sm.get_sandbox(str(sandbox.sandbox_id)) is None

    def test_destroy_sandbox_nonexistent(self) -> None:
        sm = PluginSandboxManager()
        assert sm.destroy_sandbox("nonexistent") is False

    def test_get_sandbox(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        sandbox = sm.create_sandbox(sample_plugin)
        retrieved = sm.get_sandbox(str(sandbox.sandbox_id))
        assert retrieved is not None
        assert retrieved.sandbox_id == sandbox.sandbox_id

    def test_get_sandbox_nonexistent(self) -> None:
        sm = PluginSandboxManager()
        assert sm.get_sandbox("nonexistent") is None

    def test_get_sandbox_by_plugin(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        sandbox = sm.create_sandbox(sample_plugin)
        retrieved = sm.get_sandbox_by_plugin(str(sample_plugin.plugin_id))
        assert retrieved is not None

    def test_list_sandboxes(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        assert sm.list_sandboxes() == []
        sm.create_sandbox(sample_plugin)
        assert len(sm.list_sandboxes()) == 1

    def test_validate_sandbox_valid(self) -> None:
        sm = PluginSandboxManager()
        sandbox = PluginSandbox(
            plugin_id=uuid.uuid4(),
            namespace="test-ns",
            isolation_policy="strict",
        )
        violations = sm.validate_sandbox(sandbox)
        assert violations == []

    def test_validate_sandbox_invalid_policy(self) -> None:
        sm = PluginSandboxManager()
        sandbox = PluginSandbox(
            plugin_id=uuid.uuid4(),
            namespace="test-ns",
            isolation_policy="invalid",
        )
        violations = sm.validate_sandbox(sandbox)
        assert len(violations) == 1

    def test_update_resource_limits(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        sandbox = sm.create_sandbox(sample_plugin)
        assert sm.update_resource_limits(str(sandbox.sandbox_id), {"cpu_max_percent": 80.0}) is True

    def test_update_permissions(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        sandbox = sm.create_sandbox(sample_plugin)
        assert sm.update_permissions(str(sandbox.sandbox_id), ["read", "write"]) is True

    def test_count(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        assert sm.count() == 0
        sm.create_sandbox(sample_plugin)
        assert sm.count() == 1

    def test_clear(self, sample_plugin: Plugin) -> None:
        sm = PluginSandboxManager()
        sm.create_sandbox(sample_plugin)
        assert sm.clear() == 1
        assert sm.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# PluginResourceManager
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginResourceManager:
    def test_allocate(self) -> None:
        rm = PluginResourceManager()
        usage = rm.allocate("p1")
        assert usage is not None
        assert usage.cpu_percent == 0.0
        assert usage.timeout_seconds == 30.0

    def test_allocate_with_limits(self) -> None:
        rm = PluginResourceManager()
        usage = rm.allocate("p1", {"timeout_seconds": 60.0, "max_agents": 10})
        assert usage.timeout_seconds == 60.0
        assert usage.agent_count == 10

    def test_track_cpu(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        assert rm.track_cpu("p1", 45.5) is True
        usage = rm.get_usage("p1")
        assert usage is not None
        assert usage.cpu_percent == 45.5

    def test_track_cpu_no_plugin(self) -> None:
        rm = PluginResourceManager()
        assert rm.track_cpu("nonexistent", 50.0) is False

    def test_track_memory(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        assert rm.track_memory("p1", 128.0) is True
        usage = rm.get_usage("p1")
        assert usage is not None
        assert usage.memory_mb == 128.0

    def test_track_storage(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        assert rm.track_storage("p1", 512.0) is True

    def test_track_network(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        assert rm.track_network("p1", 1024) is True

    def test_get_usage(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        assert rm.get_usage("p1") is not None
        assert rm.get_usage("nonexistent") is None

    def test_get_limits(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1", {"cpu_max_percent": 80.0})
        limits = rm.get_limits("p1")
        assert limits.get("cpu_max_percent") == 80.0

    def test_get_all_usage(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        rm.allocate("p2")
        assert len(rm.get_all_usage()) == 2

    def test_release(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        assert rm.release("p1") is True
        assert rm.release("p1") is False

    def test_check_limits_within(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1", {"cpu_max_percent": 80.0})
        rm.track_cpu("p1", 50.0)
        violations = rm.check_limits("p1")
        assert violations == []

    def test_check_limits_exceeded(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1", {"cpu_max_percent": 50.0})
        rm.track_cpu("p1", 75.0)
        violations = rm.check_limits("p1")
        assert len(violations) == 1

    def test_check_limits_no_usage(self) -> None:
        rm = PluginResourceManager()
        violations = rm.check_limits("nonexistent")
        assert len(violations) == 1

    def test_reset(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        rm.track_cpu("p1", 80.0)
        assert rm.reset("p1") is True
        usage = rm.get_usage("p1")
        assert usage is not None
        assert usage.cpu_percent == 0.0

    def test_reset_no_plugin(self) -> None:
        rm = PluginResourceManager()
        assert rm.reset("nonexistent") is False

    def test_clear(self) -> None:
        rm = PluginResourceManager()
        rm.allocate("p1")
        rm.allocate("p2")
        assert rm.clear() == 2
        assert rm.get_all_usage() == []


# ═════════════════════════════════════════════════════════════════════════════
# PluginLifecycleManager
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginLifecycleManager:
    def test_transition_discovered_to_validated(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        result = lm.transition(lifecycle_plugin, PluginLifecycleStatus.VALIDATED)
        assert result.status == PluginLifecycleStatus.VALIDATED

    def test_transition_validated_to_installed(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        p = lm.transition(lifecycle_plugin, PluginLifecycleStatus.VALIDATED)
        p = lm.transition(p, PluginLifecycleStatus.INSTALLED)
        assert p.status == PluginLifecycleStatus.INSTALLED

    def test_transition_full_path(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        p = lifecycle_plugin
        p = lm.transition(p, PluginLifecycleStatus.VALIDATED)
        p = lm.transition(p, PluginLifecycleStatus.INSTALLED)
        p = lm.transition(p, PluginLifecycleStatus.LOADED)
        p = lm.transition(p, PluginLifecycleStatus.INITIALIZED)
        p = lm.transition(p, PluginLifecycleStatus.ACTIVE)
        assert p.status == PluginLifecycleStatus.ACTIVE

    def test_transition_suspend_active(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        p = lifecycle_plugin
        for s in (PluginLifecycleStatus.VALIDATED, PluginLifecycleStatus.INSTALLED,
                  PluginLifecycleStatus.LOADED, PluginLifecycleStatus.INITIALIZED,
                  PluginLifecycleStatus.ACTIVE):
            p = lm.transition(p, s)
        p = lm.transition(p, PluginLifecycleStatus.SUSPENDED)
        assert p.status == PluginLifecycleStatus.SUSPENDED

    def test_transition_reactivate(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        p = lifecycle_plugin
        for s in (PluginLifecycleStatus.VALIDATED, PluginLifecycleStatus.INSTALLED,
                  PluginLifecycleStatus.LOADED, PluginLifecycleStatus.INITIALIZED,
                  PluginLifecycleStatus.ACTIVE, PluginLifecycleStatus.SUSPENDED):
            p = lm.transition(p, s)
        p = lm.transition(p, PluginLifecycleStatus.ACTIVE)
        assert p.status == PluginLifecycleStatus.ACTIVE

    def test_transition_to_removed(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        p = lifecycle_plugin
        p = lm.transition(p, PluginLifecycleStatus.VALIDATED)
        p = lm.transition(p, PluginLifecycleStatus.INSTALLED)
        p = lm.transition(p, PluginLifecycleStatus.REMOVED)
        assert p.status == PluginLifecycleStatus.REMOVED

    def test_transition_same_status(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        result = lm.transition(lifecycle_plugin, PluginLifecycleStatus.DISCOVERED)
        assert result.status == PluginLifecycleStatus.DISCOVERED

    def test_transition_illegal(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            lm.transition(lifecycle_plugin, PluginLifecycleStatus.ACTIVE)

    def test_get_current_status(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        assert lm.get_current_status(lifecycle_plugin) == PluginLifecycleStatus.DISCOVERED

    def test_is_transition_allowed_valid(self) -> None:
        lm = PluginLifecycleManager()
        assert lm.is_transition_allowed(PluginLifecycleStatus.DISCOVERED, PluginLifecycleStatus.VALIDATED) is True

    def test_is_transition_allowed_invalid(self) -> None:
        lm = PluginLifecycleManager()
        assert lm.is_transition_allowed(PluginLifecycleStatus.DISCOVERED, PluginLifecycleStatus.ACTIVE) is False

    def test_is_transition_allowed_same(self) -> None:
        lm = PluginLifecycleManager()
        assert lm.is_transition_allowed(PluginLifecycleStatus.DISCOVERED, PluginLifecycleStatus.DISCOVERED) is True

    def test_is_transition_allowed_removed_terminal(self) -> None:
        lm = PluginLifecycleManager()
        assert lm.is_transition_allowed(PluginLifecycleStatus.REMOVED, PluginLifecycleStatus.DISCOVERED) is False

    def test_get_history(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        lm.transition(lifecycle_plugin, PluginLifecycleStatus.VALIDATED, reason="Testing")
        history = lm.get_history(str(lifecycle_plugin.plugin_id))
        assert len(history) == 1
        assert history[0].to_status == PluginLifecycleStatus.VALIDATED
        assert history[0].reason == "Testing"

    def test_get_history_empty(self) -> None:
        lm = PluginLifecycleManager()
        assert lm.get_history("nonexistent") == []

    def test_get_all_history(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        lm.transition(lifecycle_plugin, PluginLifecycleStatus.VALIDATED)
        assert len(lm.get_all_history()) == 1

    def test_get_transition_history(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        lm.transition(lifecycle_plugin, PluginLifecycleStatus.VALIDATED, reason="Test")
        entries = lm.get_transition_history(str(lifecycle_plugin.plugin_id))
        assert len(entries) == 1
        assert entries[0]["to"] == "VALIDATED"
        assert entries[0]["reason"] == "Test"

    def test_clear(self, lifecycle_plugin: Plugin) -> None:
        lm = PluginLifecycleManager()
        lm.transition(lifecycle_plugin, PluginLifecycleStatus.VALIDATED)
        lm.clear()
        assert lm.get_all_history() == []


# ═════════════════════════════════════════════════════════════════════════════
# CapabilityRegistration
# ═════════════════════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    def test_register(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cap = PluginCapability(name="search", category="core")
        record = cr.register(sample_plugin, cap)
        assert record.name == "search"
        assert record.category == "core"
        assert record.status == "registered"
        assert record.plugin_id == sample_plugin.plugin_id

    def test_unregister(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cap = PluginCapability(name="search", category="core")
        record = cr.register(sample_plugin, cap)
        assert cr.unregister(str(record.capability_id)) is True
        retrieved = cr.get_capability(str(record.capability_id))
        assert retrieved is not None
        assert retrieved.status == "unregistered"

    def test_unregister_nonexistent(self) -> None:
        cr = CapabilityRegistration()
        assert cr.unregister("nonexistent") is False

    def test_update(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cap = PluginCapability(name="search", category="core")
        record = cr.register(sample_plugin, cap)
        cap.name = "advanced-search"
        cap.version = "2.0.0"
        assert cr.update(cap) is True
        retrieved = cr.get_capability(str(record.capability_id))
        assert retrieved is not None
        assert retrieved.name == "advanced-search"
        assert retrieved.version == "2.0.0"

    def test_update_nonexistent(self) -> None:
        cr = CapabilityRegistration()
        cap = PluginCapability(name="test", category="core")
        assert cr.update(cap) is False

    def test_discover(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cap1 = PluginCapability(name="search", category="core")
        cap2 = PluginCapability(name="analyze", category="analytics")
        cr.register(sample_plugin, cap1)
        cr.register(sample_plugin, cap2)
        records = cr.discover(sample_plugin)
        assert len(records) == 2

    def test_list_capabilities(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cap = PluginCapability(name="search", category="core")
        cr.register(sample_plugin, cap)
        all_caps = cr.list_capabilities()
        assert len(all_caps) == 1

    def test_list_capabilities_filtered(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cap = PluginCapability(name="search", category="core")
        cr.register(sample_plugin, cap)
        filtered = cr.list_capabilities(category="core")
        assert len(filtered) == 1
        filtered = cr.list_capabilities(category="nonexistent")
        assert filtered == []

    def test_count(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        assert cr.count() == 0
        cr.register(sample_plugin, PluginCapability(name="s", category="c"))
        assert cr.count() == 1

    def test_count_by_plugin(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cr.register(sample_plugin, PluginCapability(name="s1", category="c"))
        cr.register(sample_plugin, PluginCapability(name="s2", category="c"))
        assert cr.count_by_plugin(str(sample_plugin.plugin_id)) == 2

    def test_clear(self, sample_plugin: Plugin) -> None:
        cr = CapabilityRegistration()
        cr.register(sample_plugin, PluginCapability(name="s", category="c"))
        assert cr.clear() == 1
        assert cr.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# PluginCache
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginCache:
    def test_manifest_cache(self) -> None:
        cache = PluginCache()
        manifest = PluginManifest(plugin_name="test", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN)
        assert cache.get_manifest("test") is None
        cache.set_manifest("test", manifest)
        retrieved = cache.get_manifest("test")
        assert retrieved is not None
        assert retrieved.plugin_name == "test"

    def test_configuration_cache(self) -> None:
        cache = PluginCache()
        config = PluginConfiguration(plugin_id=uuid.uuid4())
        assert cache.get_configuration("test") is None
        cache.set_configuration("test", config)
        assert cache.get_configuration("test") is not None

    def test_dependencies_cache(self) -> None:
        cache = PluginCache()
        assert cache.get_dependencies("test") is None
        cache.set_dependencies("test", ["p1", "p2"])
        deps = cache.get_dependencies("test")
        assert deps is not None
        assert len(deps) == 2

    def test_capabilities_cache(self) -> None:
        cache = PluginCache()
        caps = [PluginCapability(name="s", category="c")]
        assert cache.get_capabilities("test") is None
        cache.set_capabilities("test", caps)
        retrieved = cache.get_capabilities("test")
        assert retrieved is not None
        assert len(retrieved) == 1

    def test_compatibility_result_cache(self) -> None:
        cache = PluginCache()
        result = CompatibilityResult(plugin_name="test")
        assert cache.get_compatibility_result("test") is None
        cache.set_compatibility_result("test", result)
        assert cache.get_compatibility_result("test") is not None

    def test_dependency_graph_cache(self) -> None:
        cache = PluginCache()
        graph = DependencyGraph(nodes={"a": ["b"]})
        assert cache.get_dependency_graph("test") is None
        cache.set_dependency_graph("test", graph)
        retrieved = cache.get_dependency_graph("test")
        assert retrieved is not None
        assert "a" in retrieved.nodes

    def test_invalidate(self) -> None:
        cache = PluginCache()
        manifest = PluginManifest(plugin_name="test", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN)
        cache.set_manifest("test", manifest)
        assert cache.invalidate("test") is True
        assert cache.get_manifest("test") is None

    def test_invalidate_nonexistent(self) -> None:
        cache = PluginCache()
        assert cache.invalidate("nonexistent") is False

    def test_clear(self) -> None:
        cache = PluginCache()
        manifest = PluginManifest(plugin_name="test", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN)
        cache.set_manifest("test", manifest)
        assert cache.clear() == 1
        assert cache.size() == 0

    def test_size(self) -> None:
        cache = PluginCache()
        assert cache.size() == 0
        manifest = PluginManifest(plugin_name="test", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN)
        cache.set_manifest("test", manifest)
        assert cache.size() == 1


# ═════════════════════════════════════════════════════════════════════════════
# PluginPolicyEngine
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginPolicyEngine:
    def test_installation_policy_allowed(self, sample_plugin: Plugin) -> None:
        pe = PluginPolicyEngine()
        violations = pe.check_installation_policy(sample_plugin)
        assert violations == []

    def test_installation_policy_restricted_domain(self, sample_plugin: Plugin) -> None:
        policy = PluginPolicy(
            plugin_id=uuid.uuid4(),
            name="restrictive",
            allowed_domains=[PluginDomain.ENERGY],
        )
        pe = PluginPolicyEngine(policy=policy)
        violations = pe.check_installation_policy(sample_plugin)
        assert len(violations) == 1

    def test_installation_policy_denied_capability(self) -> None:
        policy = PluginPolicy(
            plugin_id=uuid.uuid4(),
            name="deny",
            denied_capabilities=["search"],
        )
        pe = PluginPolicyEngine(policy=policy)
        manifest = PluginManifest(
            plugin_name="test", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
            capabilities=[PluginCapability(name="search", category="core")],
        )
        plugin = Plugin(name="test", version="1.0.0", manifest=manifest)
        violations = pe.check_installation_policy(plugin)
        assert len(violations) == 1

    def test_version_policy_valid(self, sample_plugin: Plugin) -> None:
        pe = PluginPolicyEngine()
        violations = pe.check_version_policy(sample_plugin, "2.0.0")
        assert violations == []

    def test_version_policy_empty(self, sample_plugin: Plugin) -> None:
        pe = PluginPolicyEngine()
        violations = pe.check_version_policy(sample_plugin, "")
        assert len(violations) == 1

    def test_sandbox_policy_valid(self) -> None:
        pe = PluginPolicyEngine()
        sandbox = PluginSandbox(plugin_id=uuid.uuid4(), namespace="ns", isolation_policy="strict")
        violations = pe.check_sandbox_policy(sandbox)
        assert violations == []

    def test_sandbox_policy_invalid_isolation(self) -> None:
        pe = PluginPolicyEngine()
        sandbox = PluginSandbox(plugin_id=uuid.uuid4(), namespace="ns", isolation_policy="custom")
        violations = pe.check_sandbox_policy(sandbox)
        assert len(violations) == 1

    def test_sandbox_policy_network_denied(self) -> None:
        policy = PluginPolicy(
            plugin_id=uuid.uuid4(),
            name="no-network",
            network_access=False,
        )
        pe = PluginPolicyEngine(policy=policy)
        sandbox = PluginSandbox(
            plugin_id=uuid.uuid4(),
            namespace="ns",
            permissions=["network"],
        )
        violations = pe.check_sandbox_policy(sandbox)
        assert len(violations) == 1

    def test_security_policy_system_without_owner(self) -> None:
        pe = PluginPolicyEngine()
        plugin = Plugin(name="sys", version="1.0.0", domain=PluginDomain.SYSTEM, owner_id="")
        violations = pe.check_security_policy(plugin)
        assert len(violations) == 1

    def test_security_policy_system_with_owner(self) -> None:
        pe = PluginPolicyEngine()
        plugin = Plugin(name="sys", version="1.0.0", domain=PluginDomain.SYSTEM, owner_id="admin")
        violations = pe.check_security_policy(plugin)
        assert violations == []

    def test_dependency_policy_optional_and_required(self) -> None:
        pe = PluginPolicyEngine()
        manifest = PluginManifest(
            plugin_name="test", plugin_version="1.0.0", plugin_type=PluginType.DOMAIN,
            dependencies=[PluginDependency(plugin_name="dep", optional=True, required=True)],
        )
        plugin = Plugin(name="test", version="1.0.0", manifest=manifest)
        violations = pe.check_dependency_policy(plugin)
        assert len(violations) == 1

    def test_check_all(self, sample_plugin: Plugin) -> None:
        pe = PluginPolicyEngine()
        violations = pe.check_all(sample_plugin)
        assert violations == []

    def test_set_policy(self) -> None:
        pe = PluginPolicyEngine()
        policy = PluginPolicy(plugin_id=uuid.uuid4(), name="custom")
        pe.set_policy(policy)
        assert pe.get_policy().name == "custom"

    def test_get_policy_default(self) -> None:
        pe = PluginPolicyEngine()
        policy = pe.get_policy()
        assert policy.name == ""


# ═════════════════════════════════════════════════════════════════════════════
# PluginTrace
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginTrace:
    def test_record(self) -> None:
        t = PluginTrace()
        record = TraceRecord(stage_name="test", operation="test-op")
        t.record(record)
        assert t.count() == 1

    def test_record_stage(self) -> None:
        t = PluginTrace()
        record = t.record_stage(
            stage_name="discovery",
            operation="discover",
            plugin_id="p1",
            domain="GENERAL",
        )
        assert record.stage_name == "discovery"
        assert record.operation == "discover"
        assert record.plugin_id == "p1"

    def test_record_discovery_stage(self) -> None:
        t = PluginTrace()
        record = t.record_discovery_stage(domain="ENERGY")
        assert record.stage_name == "discovery"
        assert record.operation == "discover"
        assert record.domain == "ENERGY"

    def test_record_validation_stage(self) -> None:
        t = PluginTrace()
        record = t.record_validation_stage(errors=["invalid"])
        assert record.stage_name == "validation"
        assert record.errors == ["invalid"]
        assert record.success is True

    def test_record_dependency_resolution_stage(self) -> None:
        t = PluginTrace()
        record = t.record_dependency_resolution_stage(plugin_id="p1")
        assert record.stage_name == "dependency_resolution"
        assert record.plugin_id == "p1"

    def test_record_compatibility_stage(self) -> None:
        t = PluginTrace()
        record = t.record_compatibility_stage(success=False)
        assert record.stage_name == "compatibility_check"
        assert record.success is False

    def test_record_sandbox_stage(self) -> None:
        t = PluginTrace()
        record = t.record_sandbox_stage(sandbox_id="sb1")
        assert record.stage_name == "sandbox_creation"
        assert record.sandbox_id == "sb1"

    def test_record_initialization_stage(self) -> None:
        t = PluginTrace()
        record = t.record_initialization_stage(duration_ms=45.2)
        assert record.stage_name == "initialization"
        assert record.duration_ms == 45.2

    def test_record_activation_stage(self) -> None:
        t = PluginTrace()
        record = t.record_activation_stage()
        assert record.stage_name == "activation"
        assert record.operation == "activate"

    def test_get_by_trace_id(self) -> None:
        t = PluginTrace()
        record = t.record_stage("discovery", "discover")
        results = t.get_by_trace_id(str(record.trace_id))
        assert len(results) == 1

    def test_get_by_operation(self) -> None:
        t = PluginTrace()
        t.record_stage("discovery", "discover")
        t.record_stage("validation", "validate")
        assert len(t.get_by_operation("discover")) == 1

    def test_get_by_stage(self) -> None:
        t = PluginTrace()
        t.record_stage("discovery", "discover")
        t.record_stage("validation", "validate")
        assert len(t.get_by_stage("discovery")) == 1

    def test_get_by_plugin_id(self) -> None:
        t = PluginTrace()
        t.record_stage("discovery", "discover", plugin_id="p1")
        assert len(t.get_by_plugin_id("p1")) == 1

    def test_get_recent(self) -> None:
        t = PluginTrace()
        t.record_stage("discovery", "discover")
        t.record_stage("validation", "validate")
        recent = t.get_recent(limit=5)
        assert len(recent) == 2

    def test_clear(self) -> None:
        t = PluginTrace()
        t.record_stage("discovery", "discover")
        assert t.count() == 1
        t.clear()
        assert t.count() == 0

    def test_count(self) -> None:
        t = PluginTrace()
        assert t.count() == 0
        t.record_stage("discovery", "discover")
        assert t.count() == 1


# ═════════════════════════════════════════════════════════════════════════════
# PluginMetricsCollector
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginMetricsCollector:
    def test_increment_plugins(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_plugins()
        snapshot = mc.snapshot()
        assert snapshot.executions_total == 0  # plugins_total maps to load attempts

    def test_increment_active_plugins(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_active_plugins()
        mc.decrement_active_plugins()
        mc.increment_active_plugins()
        # no direct assertion on active_plugins in snapshot

    def test_increment_validation_errors(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_validation_errors()
        mc.increment_validation_errors()
        snapshot = mc.snapshot()
        assert snapshot.errors_total >= 2

    def test_increment_compatibility_failures(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_compatibility_failures()
        snapshot = mc.snapshot()
        assert snapshot.errors_total >= 1

    def test_set_dependency_graph_size(self) -> None:
        mc = PluginMetricsCollector()
        mc.set_dependency_graph_size(5)

    def test_set_sandbox_count(self) -> None:
        mc = PluginMetricsCollector()
        mc.set_sandbox_count(3)

    def test_increment_load(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_load_attempts()
        mc.increment_load_successes()
        mc.increment_load_failures()
        snapshot = mc.snapshot()
        assert snapshot.executions_total == 1
        assert snapshot.executions_success == 1
        assert snapshot.executions_failed == 1

    def test_increment_discoveries(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_discoveries()

    def test_increment_capability_registrations(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_capability_registrations()

    def test_increment_initialization_attempts(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_initialization_attempts()

    def test_record_initialization_time(self) -> None:
        mc = PluginMetricsCollector()
        mc.record_initialization_time(100.0)
        mc.record_initialization_time(200.0)
        snapshot = mc.snapshot()
        assert snapshot.average_execution_time_ms == 150.0

    def test_increment_cache_hits(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_cache_hits()
        snapshot = mc.snapshot()
        assert snapshot.cache_hits == 1

    def test_increment_cache_misses(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_cache_misses()
        snapshot = mc.snapshot()
        assert snapshot.cache_misses == 1

    def test_reset(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_load_attempts()
        mc.increment_validation_errors()
        mc.record_initialization_time(50.0)
        mc.reset()
        snapshot = mc.snapshot()
        assert snapshot.executions_total == 0
        assert snapshot.errors_total == 0
        assert snapshot.average_execution_time_ms == 0.0

    def test_snapshot_empty(self) -> None:
        mc = PluginMetricsCollector()
        snapshot = mc.snapshot()
        assert snapshot.average_execution_time_ms == 0.0
        assert snapshot.cache_hits == 0
    def test_increment_plugins_with_domain(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_plugins(domain="ENERGY", plugin_type="DOMAIN")
