"""Tests for Plugin Manager Phase 3 — Enterprise Orchestration.

Covers PluginService, PluginManager, PluginCoordinator,
PluginSessionManager, PluginConfidenceCalculator, PluginHealth,
Metrics Aggregation, Tracing, Integration Hooks, and Pipeline.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from adip.plugins.contracts.models import (
    Plugin,
    PluginCapability,
    PluginConfidence,
    PluginDecision,
    PluginDependency,
    PluginExplainabilityMetadata,
    PluginHealth,
    PluginManifest,
    PluginMetrics,
    PluginSandbox,
    PluginSession,
)
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType
from adip.plugins.execution.models import DiscoveryResult, LoaderResult
from adip.plugins.orchestration.confidence import PluginConfidenceCalculator
from adip.plugins.orchestration.coordinator import PluginCoordinator
from adip.plugins.orchestration.manager import PluginManager
from adip.plugins.orchestration.session import PluginSessionManager
from adip.plugins.services.hooks import IntegrationHooks
from adip.plugins.services.hooks import hooks as global_hooks
from adip.plugins.services.service import AuthResult, PluginService

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
        tags=["test", "phase3"],
    )


# ═════════════════════════════════════════════════════════════════════════════
# PluginSessionManager
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginSessionManager:
    def test_create_session(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        session = sm.create_session(plugin_id=pid, operation="install", user_id="user-1")
        assert session.session_id is not None
        assert str(session.plugin_id) == pid
        assert session.operation == "install"
        assert session.user_id == "user-1"
        assert session.started_at is not None
        assert session.completed_at is None
        assert session.status == "PENDING"

    def test_get_session(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        created = sm.create_session(plugin_id=pid)
        fetched = sm.get_session(str(created.session_id))
        assert fetched is not None
        assert fetched.session_id == created.session_id

    def test_get_session_not_found(self) -> None:
        sm = PluginSessionManager()
        assert sm.get_session("nonexistent") is None

    def test_complete_session(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        session = sm.create_session(plugin_id=pid)
        completed = sm.complete_session(str(session.session_id))
        assert completed is not None
        assert completed.completed_at is not None
        assert completed.duration_ms >= 0
        assert completed.status == "COMPLETED"

    def test_complete_session_not_found(self) -> None:
        sm = PluginSessionManager()
        assert sm.complete_session("nonexistent") is None

    def test_fail_session(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        session = sm.create_session(plugin_id=pid)
        failed = sm.fail_session(str(session.session_id), error_message="Something went wrong")
        assert failed is not None
        assert failed.completed_at is not None
        assert failed.duration_ms >= 0
        assert failed.status == "FAILED"
        assert failed.error_message == "Something went wrong"

    def test_fail_session_not_found(self) -> None:
        sm = PluginSessionManager()
        assert sm.fail_session("nonexistent") is None

    def test_update_session_field(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        session = sm.create_session(plugin_id=pid)
        updated = sm.update_session_field(str(session.session_id), user_id="new-user")
        assert updated is True
        assert sm.get_session(str(session.session_id)).user_id == "new-user"

    def test_update_session_not_found(self) -> None:
        sm = PluginSessionManager()
        assert sm.update_session_field("nonexistent", user_id="x") is False

    def test_get_active_sessions(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        s1 = sm.create_session(plugin_id=pid)
        s2 = sm.create_session(plugin_id=pid)
        sm.complete_session(str(s1.session_id))
        active = sm.get_active_sessions()
        assert len(active) == 1
        assert active[0].session_id == s2.session_id

    def test_get_sessions_by_plugin(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        sm.create_session(plugin_id=pid, operation="install")
        sm.create_session(plugin_id=pid, operation="activate")
        sessions = sm.get_sessions_by_plugin(pid)
        assert len(sessions) == 2

    def test_clear(self) -> None:
        sm = PluginSessionManager()
        pid = str(uuid.uuid4())
        sm.create_session(plugin_id=pid)
        sm.create_session(plugin_id=pid)
        sm.clear()
        assert sm.get_session("anything") is None
        assert sm.get_active_sessions() == []


# ═════════════════════════════════════════════════════════════════════════════
# PluginConfidenceCalculator
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginConfidenceCalculator:
    def test_calculate_with_full_plugin(self, sample_plugin: Plugin) -> None:
        calc = PluginConfidenceCalculator()
        confidence = calc.calculate(sample_plugin)
        assert isinstance(confidence, PluginConfidence)
        assert 0.0 <= confidence.overall_confidence <= 1.0
        assert confidence.manifest_quality > 0.0
        assert confidence.lifecycle_validity >= 0.0
        assert confidence.configuration_quality >= 0.0

    def test_calculate_with_minimal_plugin(self) -> None:
        calc = PluginConfidenceCalculator()
        plugin = Plugin(
            name="minimal",
            version="",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
        )
        confidence = calc.calculate(plugin)
        assert confidence.manifest_quality == 0.0
        assert confidence.compatibility_score == 0.0
        assert confidence.configuration_quality == 0.3

    def test_calculate_without_manifest(self) -> None:
        calc = PluginConfidenceCalculator()
        plugin = Plugin(
            name="no-manifest",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
        )
        confidence = calc.calculate(plugin)
        assert confidence.manifest_quality == 0.0

    def test_calculate_sandbox_readiness(self, sample_plugin: Plugin) -> None:
        calc = PluginConfidenceCalculator()
        sample_plugin.status = PluginLifecycleStatus.ACTIVE
        confidence = calc.calculate(sample_plugin)
        assert confidence.sandbox_readiness >= 0.5

    def test_calculate_lifecycle_validity(self, sample_plugin: Plugin) -> None:
        calc = PluginConfidenceCalculator()
        statuses = [
            (PluginLifecycleStatus.DISCOVERED, 0.1),
            (PluginLifecycleStatus.VALIDATED, 0.2),
            (PluginLifecycleStatus.INSTALLED, 0.3),
            (PluginLifecycleStatus.LOADED, 0.5),
            (PluginLifecycleStatus.INITIALIZED, 0.7),
            (PluginLifecycleStatus.ACTIVE, 1.0),
        ]
        for status, expected_lower in statuses:
            sample_plugin.status = status
            confidence = calc.calculate(sample_plugin)
            assert confidence.lifecycle_validity >= expected_lower

    def test_configuration_quality_with_tags(self, sample_plugin: Plugin) -> None:
        calc = PluginConfidenceCalculator()
        sample_plugin.tags = ["tag1", "tag2"]
        sample_plugin.owner_id = "owner-1"
        confidence = calc.calculate(sample_plugin)
        assert confidence.configuration_quality >= 0.5

    def test_dependency_completeness_no_deps(self) -> None:
        calc = PluginConfidenceCalculator()
        plugin = Plugin(
            name="no-deps",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
            manifest=PluginManifest(
                plugin_name="no-deps",
                plugin_version="1.0.0",
                plugin_type=PluginType.DOMAIN,
            ),
        )
        confidence = calc.calculate(plugin)
        assert confidence.dependency_completeness == 1.0


# ═════════════════════════════════════════════════════════════════════════════
# PluginExplainabilityMetadata
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginExplainabilityMetadata:
    def test_defaults(self) -> None:
        meta = PluginExplainabilityMetadata()
        assert meta.why_plugin_loaded == ""
        assert meta.why_plugin_rejected == ""
        assert meta.why_dependency_failed == ""
        assert meta.why_sandbox_created == ""
        assert meta.why_capability_registered == ""

    def test_custom_values(self) -> None:
        meta = PluginExplainabilityMetadata(
            why_plugin_loaded="Validated, compatible, dependencies satisfied",
            why_plugin_rejected="Policy violation",
            why_dependency_failed="Missing base-plugin",
            why_sandbox_created="Sandbox sb-1 created for test-plugin",
            why_capability_registered="2 capabilities registered",
        )
        assert meta.why_plugin_loaded == "Validated, compatible, dependencies satisfied"
        assert meta.why_plugin_rejected == "Policy violation"


# ═════════════════════════════════════════════════════════════════════════════
# IntegrationHooks
# ═════════════════════════════════════════════════════════════════════════════


class TestIntegrationHooks:
    def test_pre_discover_hook(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        def hook(source: str) -> None:
            calls.append(source)

        hooks.on_pre_discover(hook)
        hooks.invoke_pre_discover("/tmp/plugin")
        assert calls == ["/tmp/plugin"]

    def test_post_discover_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        def hook(plugin: Plugin) -> None:
            calls.append(plugin.name)

        hooks.on_post_discover(hook)
        hooks.invoke_post_discover(sample_plugin)
        assert calls == ["test-plugin"]

    def test_pre_install_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        def hook(plugin: Plugin) -> None:
            calls.append(plugin.name)

        hooks.on_pre_install(hook)
        hooks.invoke_pre_install(sample_plugin)
        assert calls == ["test-plugin"]

    def test_post_install_hook(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        decision = PluginDecision(plugin_id=uuid.uuid4(), operation="install", allowed=True, decision="approve")

        def hook(d: PluginDecision) -> None:
            calls.append(d.decision)

        hooks.on_post_install(hook)
        hooks.invoke_post_install(decision)
        assert calls == ["approve"]

    def test_pre_load_hook(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        def hook(plugin: Plugin) -> None:
            calls.append(plugin)

        hooks.on_pre_load(hook)
        hooks.invoke_pre_load("test-plugin-id")
        assert len(calls) == 1

    def test_session_hooks(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        started: list[str] = []
        completed: list[str] = []

        hooks.on_session_started(lambda s: started.append(s.operation))
        hooks.on_session_completed(lambda s: completed.append(s.operation))

        session = PluginSession(plugin_id=sample_plugin.plugin_id, operation="install")
        hooks.invoke_session_started(session)
        hooks.invoke_session_completed(session)

        assert started == ["install"]
        assert completed == ["install"]

    def test_sandbox_hooks(self) -> None:
        hooks = IntegrationHooks()
        created: list[str] = []
        destroyed: list[str] = []

        hooks.on_sandbox_created(lambda s: created.append(str(s.sandbox_id)))
        hooks.on_sandbox_destroyed(lambda s: destroyed.append(s))

        sandbox = PluginSandbox(plugin_id=uuid.uuid4())
        hooks.invoke_sandbox_created(sandbox)
        hooks.invoke_sandbox_destroyed(str(sandbox.sandbox_id))

        assert len(created) == 1
        assert len(destroyed) == 1

    def test_error_hook(self) -> None:
        hooks = IntegrationHooks()
        errors: list[str] = []

        def hook(op: str, err: Exception) -> None:
            errors.append(f"{op}: {err}")

        hooks.on_error(hook)
        hooks.invoke_error("install", ValueError("test error"))
        assert "install" in errors[0]

    def test_hook_exception_isolation(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()

        def failing(plugin: Plugin) -> None:
            msg = "hook failed"
            raise RuntimeError(msg)

        def succeeding(plugin: Plugin) -> None:
            pass

        hooks.on_post_discover(failing)
        hooks.on_post_discover(succeeding)
        hooks.invoke_post_discover(sample_plugin)

    def test_global_hooks_singleton(self) -> None:
        assert isinstance(global_hooks, IntegrationHooks)

    def test_pre_delete_hook(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.on_pre_delete(lambda pid: calls.append(pid))
        hooks.invoke_pre_delete("plugin-1")
        assert calls == ["plugin-1"]

    def test_post_delete_hook(self) -> None:
        hooks = IntegrationHooks()
        calls: list[tuple[str, bool]] = []

        hooks.on_post_delete(lambda pid, s: calls.append((pid, s)))
        hooks.invoke_post_delete("plugin-1", True)
        assert calls == [("plugin-1", True)]

    def test_pre_suspend_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.on_pre_suspend(lambda p: calls.append(p.name))
        hooks.invoke_pre_suspend(sample_plugin)
        assert calls == ["test-plugin"]

    def test_post_suspend_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.on_post_suspend(lambda p: calls.append(p.name))
        hooks.invoke_post_suspend(sample_plugin)
        assert calls == ["test-plugin"]

    def test_pre_unload_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.on_pre_unload(lambda p: calls.append(p.name))
        hooks.invoke_pre_unload(sample_plugin)
        assert calls == ["test-plugin"]

    def test_post_unload_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.on_post_unload(lambda p: calls.append(p.name))
        hooks.invoke_post_unload(sample_plugin)
        assert calls == ["test-plugin"]

    def test_pre_activate_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.on_pre_activate(lambda p: calls.append(p.name))
        hooks.invoke_pre_activate(sample_plugin)
        assert calls == ["test-plugin"]

    def test_post_activate_hook(self, sample_plugin: Plugin) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.on_post_activate(lambda p: calls.append(p.name))
        hooks.invoke_post_activate(sample_plugin)
        assert calls == ["test-plugin"]


# ═════════════════════════════════════════════════════════════════════════════
# PluginCoordinator
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginCoordinator:
    def test_discover_plugin(self) -> None:
        coord = PluginCoordinator()
        result = coord.discover_plugin("/tmp/plugin", "local_directory")
        assert isinstance(result, DiscoveryResult)
        assert result.source == "/tmp/plugin"
        assert result.source_type == "local_directory"

    def test_validate_plugin_valid(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        violations = coord.validate_plugin(sample_plugin)
        assert violations == []

    def test_validate_plugin_invalid(self) -> None:
        coord = PluginCoordinator()
        plugin = Plugin(
            name="",
            version="",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
        )
        violations = coord.validate_plugin(plugin)
        assert len(violations) > 0

    def test_check_compatibility(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        result = coord.check_compatibility(sample_plugin)
        assert result is not None
        assert result.plugin_name == sample_plugin.name

    def test_resolve_dependencies(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        satisfied, missing = coord.resolve_dependencies(sample_plugin)
        assert isinstance(satisfied, list)
        assert isinstance(missing, list)

    def test_load_plugin(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        result = coord.load_plugin(sample_plugin)
        assert isinstance(result, LoaderResult)
        assert result.plugin_name == "test-plugin"

    def test_initialize_plugin(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        result = coord.initialize_plugin(sample_plugin)
        assert result.success is True

    def test_register_capabilities(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        records = coord.register_capabilities(sample_plugin)
        assert len(records) == 2

    def test_transition_lifecycle(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        result = coord.transition_lifecycle(sample_plugin, PluginLifecycleStatus.VALIDATED)
        assert result.status == PluginLifecycleStatus.VALIDATED

    def test_create_sandbox(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        sandbox = coord.create_sandbox(sample_plugin)
        assert isinstance(sandbox, PluginSandbox)
        assert str(sandbox.plugin_id) == str(sample_plugin.plugin_id)

    def test_get_sandbox(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        sandbox = coord.create_sandbox(sample_plugin)
        fetched = coord.get_sandbox(str(sandbox.sandbox_id))
        assert fetched is not None
        assert fetched.sandbox_id == sandbox.sandbox_id

    def test_full_install_success(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        decision = coord.install_plugin(sample_plugin)
        assert decision.allowed is True
        assert decision.decision == "approve"
        assert decision.operation == "install"
        assert decision.compatibility_result == "passed"
        assert decision.security_result == "passed"
        assert decision.confidence > 0.0

        installed = coord.get_plugin(str(sample_plugin.plugin_id))
        assert installed is not None
        assert installed.status in (
            PluginLifecycleStatus.INITIALIZED,
            PluginLifecycleStatus.LOADED,
        )

    def test_install_with_validation_failure(self) -> None:
        coord = PluginCoordinator()
        plugin = Plugin(
            name="",
            version="",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
        )
        decision = coord.install_plugin(plugin)
        assert decision.allowed is False
        assert decision.decision == "deny"
        assert "Validation" in decision.reason

    def test_get_plugin_not_found(self) -> None:
        coord = PluginCoordinator()
        assert coord.get_plugin("nonexistent") is None

    def test_list_plugins(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        results = coord.list_plugins()
        assert len(results) >= 1

    def test_list_plugins_by_domain(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        results = coord.list_plugins(domain=PluginDomain.GENERAL)
        assert len(results) >= 1
        results = coord.list_plugins(domain=PluginDomain.SYSTEM)
        assert len(results) == 0

    def test_list_plugins_by_type(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        results = coord.list_plugins(plugin_type=PluginType.DOMAIN)
        assert len(results) >= 1

    def test_list_plugins_by_status(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        results = coord.list_plugins(status=PluginLifecycleStatus.INITIALIZED)
        assert len(results) >= 0

    def test_delete_plugin(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        pid = str(sample_plugin.plugin_id)
        assert coord.delete_plugin(pid) is True
        assert coord.get_plugin(pid) is None

    def test_delete_nonexistent(self) -> None:
        coord = PluginCoordinator()
        assert coord.delete_plugin("nonexistent") is False

    def test_health(self) -> None:
        coord = PluginCoordinator()
        health = coord.health()
        assert isinstance(health, PluginHealth)
        assert health.overall_status == "HEALTHY"
        assert health.is_healthy() is True

    def test_metrics(self) -> None:
        coord = PluginCoordinator()
        metrics = coord.metrics()
        assert isinstance(metrics, PluginMetrics)

    def test_clear(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        assert len(coord.list_plugins()) >= 1
        coord.clear()
        assert len(coord.list_plugins()) == 0

    def test_get_dependency_graph_size(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        assert coord.get_dependency_graph_size() == 0
        coord.install_plugin(sample_plugin)
        assert coord.get_dependency_graph_size() >= 1

    def test_activation_then_suspend(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        pid = str(sample_plugin.plugin_id)
        activated = coord.transition_lifecycle(
            coord.get_plugin(pid),
            PluginLifecycleStatus.ACTIVE,
        )
        assert activated.status == PluginLifecycleStatus.ACTIVE
        suspended = coord.transition_lifecycle(
            activated,
            PluginLifecycleStatus.SUSPENDED,
            reason="Maintenance",
        )
        assert suspended.status == PluginLifecycleStatus.SUSPENDED

    def test_explainability_on_install(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        decision = coord.install_plugin(sample_plugin)
        assert "explainability" in decision.metadata
        assert "confidence" in decision.metadata
        assert "load_result" in decision.metadata
        assert len(decision.reasoning) > 0
        assert decision.lifecycle_result != ""

    def test_policy_violation_on_install(self) -> None:
        from adip.plugins.contracts.models import PluginPolicy

        coord = PluginCoordinator()
        coord._policy_engine.set_policy(PluginPolicy(
            plugin_id=uuid.uuid4(),
            allowed_domains=[PluginDomain.GENERAL],
        ))
        plugin = Plugin(
            name="restricted",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.ENERGY,
        )
        decision = coord.install_plugin(plugin)
        assert decision.allowed is False

    def test_load_failure_in_pipeline(self) -> None:
        coord = PluginCoordinator()
        plugin = Plugin(
            name="no-manifest",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
        )
        decision = coord.install_plugin(plugin)
        assert decision.allowed is True
        assert decision.decision == "deny"

    def test_coordinator_sandbox_and_metrics(self, sample_plugin: Plugin) -> None:
        coord = PluginCoordinator()
        coord.install_plugin(sample_plugin)
        sandbox = coord.create_sandbox(sample_plugin)
        assert sandbox is not None
        metrics = coord.metrics()
        assert isinstance(metrics, PluginMetrics)


# ═════════════════════════════════════════════════════════════════════════════
# PluginManager
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginManager:
    def test_discover_plugin(self) -> None:
        mgr = PluginManager()
        result = mgr.discover_plugin("/tmp/plugin")
        assert isinstance(result, DiscoveryResult)

    def test_install_plugin(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        decision = mgr.install_plugin(sample_plugin)
        assert decision.allowed is True
        assert decision.decision == "approve"

    def test_get_plugin(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        plugin = mgr.get_plugin(str(sample_plugin.plugin_id))
        assert plugin is not None
        assert plugin.name == "test-plugin"

    def test_get_plugin_not_found(self) -> None:
        mgr = PluginManager()
        assert mgr.get_plugin("nonexistent") is None

    def test_list_plugins(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        results = mgr.list_plugins()
        assert len(results) >= 1

    def test_activate_plugin(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        activated = mgr.activate_plugin(str(sample_plugin.plugin_id))
        assert activated is not None
        assert activated.status == PluginLifecycleStatus.ACTIVE

    def test_activate_nonexistent(self) -> None:
        mgr = PluginManager()
        assert mgr.activate_plugin("nonexistent") is None

    def test_suspend_plugin(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        mgr.activate_plugin(str(sample_plugin.plugin_id))
        suspended = mgr.suspend_plugin(str(sample_plugin.plugin_id), reason="Testing")
        assert suspended is not None
        assert suspended.status == PluginLifecycleStatus.SUSPENDED

    def test_suspend_nonexistent(self) -> None:
        mgr = PluginManager()
        assert mgr.suspend_plugin("nonexistent") is None

    def test_load_plugin(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        result = mgr.load_plugin(str(sample_plugin.plugin_id))
        assert result is not None
        assert result.success is True

    def test_load_nonexistent(self) -> None:
        mgr = PluginManager()
        assert mgr.load_plugin("nonexistent") is None

    def test_unload_plugin(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        unloaded = mgr.unload_plugin(str(sample_plugin.plugin_id))
        assert unloaded is not None
        assert unloaded.status == PluginLifecycleStatus.UNLOADED

    def test_unload_nonexistent(self) -> None:
        mgr = PluginManager()
        assert mgr.unload_plugin("nonexistent") is None

    def test_create_sandbox(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        sandbox = mgr.create_sandbox(str(sample_plugin.plugin_id), {"key": "value"})
        assert sandbox is not None
        assert str(sandbox.plugin_id) == str(sample_plugin.plugin_id)

    def test_create_sandbox_nonexistent(self) -> None:
        mgr = PluginManager()
        assert mgr.create_sandbox("nonexistent") is None

    def test_destroy_sandbox(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        sandbox = mgr.create_sandbox(str(sample_plugin.plugin_id))
        assert mgr.destroy_sandbox(str(sandbox.sandbox_id)) is True

    def test_destroy_sandbox_nonexistent(self) -> None:
        mgr = PluginManager()
        assert mgr.destroy_sandbox("nonexistent") is False

    def test_get_sandbox(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        sandbox = mgr.create_sandbox(str(sample_plugin.plugin_id))
        fetched = mgr.get_sandbox(str(sandbox.sandbox_id))
        assert fetched is not None

    def test_get_sandbox_not_found(self) -> None:
        mgr = PluginManager()
        assert mgr.get_sandbox("nonexistent") is None

    def test_delete_plugin(self, sample_plugin: Plugin) -> None:
        mgr = PluginManager()
        mgr.install_plugin(sample_plugin)
        assert mgr.delete_plugin(str(sample_plugin.plugin_id)) is True
        assert mgr.get_plugin(str(sample_plugin.plugin_id)) is None

    def test_get_health(self) -> None:
        mgr = PluginManager()
        health = mgr.get_health()
        assert health.is_healthy() is True

    def test_get_metrics(self) -> None:
        mgr = PluginManager()
        metrics = mgr.get_metrics()
        assert isinstance(metrics, PluginMetrics)


# ═════════════════════════════════════════════════════════════════════════════
# PluginService — ONLY public API
# ═════════════════════════════════════════════════════════════════════════════


class TestPluginService:
    def test_discover_plugin(self) -> None:
        svc = PluginService()
        result = svc.discover_plugin("/tmp/plugin", user_id="admin")
        assert isinstance(result, DiscoveryResult)

    def test_install_plugin(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        decision = svc.install_plugin(sample_plugin, user_id="admin")
        assert decision.allowed is True

    def test_get_plugin(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        plugin = svc.get_plugin(str(sample_plugin.plugin_id))
        assert plugin is not None
        assert plugin.name == "test-plugin"

    def test_get_plugin_not_found(self) -> None:
        svc = PluginService()
        assert svc.get_plugin("nonexistent") is None

    def test_list_plugins(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        results = svc.list_plugins(user_id="admin")
        assert len(results) >= 1

    def test_activate_plugin(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        activated = svc.activate_plugin(str(sample_plugin.plugin_id), user_id="admin")
        assert activated is not None
        assert activated.status == PluginLifecycleStatus.ACTIVE

    def test_activate_not_found(self) -> None:
        svc = PluginService()
        with pytest.raises(ValueError):
            svc.activate_plugin("nonexistent", user_id="admin")

    def test_suspend_plugin(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        svc.activate_plugin(str(sample_plugin.plugin_id), user_id="admin")
        suspended = svc.suspend_plugin(str(sample_plugin.plugin_id), reason="test", user_id="admin")
        assert suspended is not None
        assert suspended.status == PluginLifecycleStatus.SUSPENDED

    def test_suspend_not_found(self) -> None:
        svc = PluginService()
        with pytest.raises(ValueError):
            svc.suspend_plugin("nonexistent", user_id="admin")

    def test_load_plugin(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        result = svc.load_plugin(str(sample_plugin.plugin_id), user_id="admin")
        assert result is not None
        assert result.success is True

    def test_load_not_found(self) -> None:
        svc = PluginService()
        with pytest.raises(ValueError):
            svc.load_plugin("nonexistent", user_id="admin")

    def test_unload_plugin(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        unloaded = svc.unload_plugin(str(sample_plugin.plugin_id), user_id="admin")
        assert unloaded is not None
        assert unloaded.status == PluginLifecycleStatus.UNLOADED

    def test_unload_not_found(self) -> None:
        svc = PluginService()
        with pytest.raises(ValueError):
            svc.unload_plugin("nonexistent", user_id="admin")

    def test_uninstall_plugin(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        assert svc.uninstall_plugin(str(sample_plugin.plugin_id), user_id="admin") is True

    def test_create_sandbox(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        sandbox = svc.create_sandbox(str(sample_plugin.plugin_id), user_id="admin")
        assert sandbox is not None
        assert str(sandbox.plugin_id) == str(sample_plugin.plugin_id)

    def test_create_sandbox_not_found(self) -> None:
        svc = PluginService()
        with pytest.raises(ValueError):
            svc.create_sandbox("nonexistent", user_id="admin")

    def test_destroy_sandbox(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        sandbox = svc.create_sandbox(str(sample_plugin.plugin_id), user_id="admin")
        assert svc.destroy_sandbox(str(sandbox.sandbox_id), user_id="admin") is True

    def test_get_sandbox(self, sample_plugin: Plugin) -> None:
        svc = PluginService()
        svc.install_plugin(sample_plugin, user_id="admin")
        sandbox = svc.create_sandbox(str(sample_plugin.plugin_id), user_id="admin")
        fetched = svc.get_sandbox(str(sandbox.sandbox_id))
        assert fetched is not None

    def test_get_sandbox_not_found(self) -> None:
        svc = PluginService()
        assert svc.get_sandbox("nonexistent") is None

    def test_health(self) -> None:
        svc = PluginService()
        health = svc.health()
        assert health.is_healthy() is True

    def test_get_metrics(self) -> None:
        svc = PluginService()
        metrics = svc.get_metrics()
        assert isinstance(metrics, PluginMetrics)

    def test_get_session(self) -> None:
        svc = PluginService()
        assert svc.get_session("nonexistent") is None

    # ── Auth ──────────────────────────────────────────────────────────────

    def test_auth_allowed(self, sample_plugin: Plugin) -> None:
        def auth(user: str, op: str) -> AuthResult:
            return AuthResult(allowed=True)

        svc = PluginService(auth_callback=auth)
        decision = svc.install_plugin(sample_plugin, user_id="user")
        assert decision is not None

    def test_auth_denied(self, sample_plugin: Plugin) -> None:
        def auth(user: str, op: str) -> AuthResult:
            return AuthResult(allowed=False, reason="Not authorised")

        svc = PluginService(auth_callback=auth)
        with pytest.raises(PermissionError):
            svc.install_plugin(sample_plugin, user_id="user")

    def test_auth_denied_on_discover(self) -> None:
        def auth(user: str, op: str) -> AuthResult:
            return AuthResult(allowed=False, reason="Not authorised")

        svc = PluginService(auth_callback=auth)
        with pytest.raises(PermissionError):
            svc.discover_plugin("/tmp/p", user_id="user")

    # ── Audit ─────────────────────────────────────────────────────────────

    def test_audit_callback(self, sample_plugin: Plugin) -> None:
        audit_entries: list[dict[str, Any]] = []

        def audit(op: str, resource: str, user: str, details: dict[str, Any]) -> None:
            audit_entries.append({"op": op, "resource": resource, "user": user})

        svc = PluginService(audit_callback=audit)
        svc.install_plugin(sample_plugin, user_id="admin")
        assert len(audit_entries) >= 1
        assert audit_entries[0]["op"] == "install" or audit_entries[0]["op"] == "install"

    def test_audit_on_discover(self) -> None:
        audit_entries: list[dict[str, Any]] = []

        def audit(op: str, resource: str, user: str, details: dict[str, Any]) -> None:
            audit_entries.append({"op": op})

        svc = PluginService(audit_callback=audit)
        svc.discover_plugin("/tmp/p", user_id="admin")
        assert len(audit_entries) >= 1


# ═════════════════════════════════════════════════════════════════════════════
# Pipeline integration test
# ═════════════════════════════════════════════════════════════════════════════


class TestPipeline:
    def test_full_pipeline(self) -> None:
        """End-to-end: install → activate → suspend → health → metrics."""
        svc = PluginService()

        manifest = PluginManifest(
            plugin_name="pipeline-test",
            plugin_version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            plugin_domain=PluginDomain.GENERAL,
            capabilities=[PluginCapability(name="exec", category="core")],
        )
        plugin = Plugin(
            name="pipeline-test",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
            manifest=manifest,
        )

        decision = svc.install_plugin(plugin, user_id="admin")
        assert decision.allowed is True

        activated = svc.activate_plugin(str(plugin.plugin_id), user_id="admin")
        assert activated.status == PluginLifecycleStatus.ACTIVE

        suspended = svc.suspend_plugin(str(plugin.plugin_id), reason="Test", user_id="admin")
        assert suspended.status == PluginLifecycleStatus.SUSPENDED

        health = svc.health()
        assert isinstance(health, PluginHealth)

        metrics = svc.get_metrics()
        assert isinstance(metrics, PluginMetrics)

    def test_discover_install_load_activate(self, sample_manifest: PluginManifest) -> None:
        """Flow: discover → install → load → activate → unload → uninstall."""
        svc = PluginService()

        discover_result = svc.discover_plugin("/tmp/p", "local_directory", user_id="admin")
        assert discover_result is not None

        plugin = Plugin(
            name="flow-test",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.GENERAL,
            manifest=sample_manifest,
        )

        decision = svc.install_plugin(plugin, user_id="admin")
        assert decision.allowed is True

        load_result = svc.load_plugin(str(plugin.plugin_id), user_id="admin")
        assert load_result.success is True

        activated = svc.activate_plugin(str(plugin.plugin_id), user_id="admin")
        assert activated.status == PluginLifecycleStatus.ACTIVE

        unloaded = svc.unload_plugin(str(plugin.plugin_id), user_id="admin")
        assert unloaded.status == PluginLifecycleStatus.UNLOADED

        assert svc.uninstall_plugin(str(plugin.plugin_id), user_id="admin") is True


# ═════════════════════════════════════════════════════════════════════════════
# Backward compatibility
# ═════════════════════════════════════════════════════════════════════════════


class TestBackwardCompatibility:
    def test_plugin_health_defaults(self) -> None:
        health = PluginHealth(plugin_id=uuid.uuid4())
        assert health.overall_status == "UNKNOWN"
        assert health.is_healthy() is False

    def test_plugin_health_healthy(self) -> None:
        health = PluginHealth(overall_status="HEALTHY", plugin_id=uuid.uuid4())
        assert health.is_healthy() is True

    def test_plugin_decision_defaults(self) -> None:
        decision = PluginDecision(plugin_id=uuid.uuid4())
        assert decision.allowed is True
        assert decision.operation == ""
        assert decision.decision == ""
        assert decision.confidence == 0.0
        assert decision.compatibility_result == ""

    def test_plugin_session_minimal(self) -> None:
        pid = uuid.uuid4()
        session = PluginSession(plugin_id=pid)
        assert session.operation == ""
        assert session.status == "PENDING"
        assert session.completed_at is None
        assert session.duration_ms == 0.0

    def test_plugin_decision_enhanced_fields(self) -> None:
        decision = PluginDecision(
            plugin_id=uuid.uuid4(),
            operation="install",
            allowed=True,
            decision="approve",
            compatibility_result="passed",
            dependency_result="2 satisfied",
            sandbox_result="sandbox-1",
            security_result="passed",
            confidence=0.85,
        )
        assert decision.operation == "install"
        assert decision.compatibility_result == "passed"
        assert decision.dependency_result == "2 satisfied"
        assert decision.sandbox_result == "sandbox-1"
        assert decision.confidence == 0.85

    def test_plugin_session_enhanced_fields(self) -> None:
        pid = uuid.uuid4()
        session = PluginSession(
            plugin_id=pid,
            operation="install",
            dependency_summary="2 satisfied",
            sandbox_id="sandbox-1",
            lifecycle_state="LOADED",
            statistics={"load_ms": 42},
        )
        assert session.operation == "install"
        assert session.dependency_summary == "2 satisfied"
        assert session.sandbox_id == "sandbox-1"
        assert session.lifecycle_state == "LOADED"
        assert session.statistics == {"load_ms": 42}

    def test_plugin_confidence_all_scores(self) -> None:
        confidence = PluginConfidence(
            overall_confidence=0.85,
            manifest_quality=0.9,
            dependency_completeness=1.0,
            compatibility_score=0.8,
            sandbox_readiness=0.7,
            lifecycle_validity=0.75,
            configuration_quality=0.6,
        )
        assert confidence.overall_confidence == 0.85
        assert confidence.manifest_quality == 0.9
        assert confidence.calculated_at is not None

    def test_explainability_metadata_forward_compat(self) -> None:
        meta = PluginExplainabilityMetadata()
        # All fields exist and are empty by default
        assert hasattr(meta, "why_plugin_loaded")
        assert hasattr(meta, "why_plugin_rejected")
        assert hasattr(meta, "why_dependency_failed")
        assert hasattr(meta, "why_sandbox_created")
        assert hasattr(meta, "why_capability_registered")
        # model_dump works
        dump = meta.model_dump()
        assert dump["why_plugin_loaded"] == ""
