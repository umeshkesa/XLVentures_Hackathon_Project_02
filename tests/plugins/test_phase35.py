from __future__ import annotations

import uuid

from adip.plugins.contracts.models import (
    Plugin,
    PluginConfidence,
    PluginDecision,
    PluginExplainabilityMetadata,
    PluginHealth,
    PluginManifest,
    PluginMetrics,
    PluginSandbox,
)
from adip.plugins.enums import (
    PluginDomain,
    PluginType,
)
from adip.plugins.execution.dependency_graph import PluginDependencyGraph
from adip.plugins.execution.metrics import PluginMetricsCollector
from adip.plugins.execution.models import DependencyGraph
from adip.plugins.execution.trace import PluginTrace
from adip.plugins.orchestration.confidence import PluginConfidenceCalculator
from adip.plugins.orchestration.coordinator import PluginCoordinator

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plugin(**overrides: object) -> Plugin:
    defaults: dict[str, object] = {
        "name": "test-plugin",
        "version": "1.0.0",
        "plugin_type": PluginType.DOMAIN,
        "domain": PluginDomain.ENERGY,
        "manifest": PluginManifest(
            plugin_name="test-plugin",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.ENERGY,
            entry_point="main.py",
        ),
    }
    defaults.update(overrides)
    return Plugin(**defaults)


# ===================================================================
# PluginDecision Phase 3.5 enhancements
# ===================================================================

class TestPluginDecisionPhase35:
    def test_lifecycle_result_default(self) -> None:
        d = PluginDecision(plugin_id=uuid.uuid4(), operation="install", allowed=True)
        assert d.lifecycle_result == ""

    def test_lifecycle_result_custom(self) -> None:
        d = PluginDecision(
            plugin_id=uuid.uuid4(),
            operation="install",
            allowed=True,
            lifecycle_result="DISCOVERED->VALIDATED->INSTALLED",
        )
        assert d.lifecycle_result == "DISCOVERED->VALIDATED->INSTALLED"

    def test_reasoning_default(self) -> None:
        d = PluginDecision(plugin_id=uuid.uuid4(), operation="install", allowed=True)
        assert d.reasoning == []

    def test_reasoning_mutable(self) -> None:
        d = PluginDecision(
            plugin_id=uuid.uuid4(),
            operation="install",
            allowed=True,
            reasoning=["Step 1"],
        )
        d.reasoning.append("Step 2")
        assert d.reasoning == ["Step 1", "Step 2"]


# ===================================================================
# PluginConfidence Phase 3.5 enhancements
# ===================================================================

class TestPluginConfidencePhase35:
    def test_signature_status_default(self) -> None:
        c = PluginConfidence()
        assert c.signature_status == "unknown"

    def test_signature_status_verified(self) -> None:
        c = PluginConfidence(signature_status="verified")
        assert c.signature_status == "verified"

    def test_signature_status_settable(self) -> None:
        c = PluginConfidence(signature_status="unverified")
        assert c.signature_status == "unverified"

    def test_confidence_new_fields_compatible(self) -> None:
        c = PluginConfidence(
            overall_confidence=0.85,
            manifest_quality=0.9,
            signature_status="verified",
        )
        assert c.overall_confidence == 0.85
        assert c.manifest_quality == 0.9
        assert c.signature_status == "verified"


# ===================================================================
# PluginTrace Phase 3.5 enhancements
# ===================================================================

class TestPluginTracePhase35:
    def test_record_registration_stage(self) -> None:
        trace = PluginTrace()
        trace.record_registration_stage(
            plugin_id=str(uuid.uuid4()),
            domain="ENERGY",
        )
        assert trace.count() == 1
        rec = trace.get_recent()[0]
        assert rec.stage_name == "registration"

    def test_registration_stage_correlation_id(self) -> None:
        trace = PluginTrace()
        trace.record_registration_stage(
            plugin_id=str(uuid.uuid4()),
            correlation_id="corr-001",
        )
        assert trace.get_recent()[0].correlation_id == "corr-001"

    def test_registration_stage_duration_ms(self) -> None:
        trace = PluginTrace()
        trace.record_registration_stage(
            plugin_id=str(uuid.uuid4()),
            duration_ms=12.5,
        )
        assert trace.get_recent()[0].duration_ms == 12.5

    def test_all_eight_dedicated_stage_methods(self) -> None:
        pid = str(uuid.uuid4())
        trace = PluginTrace()
        rec1 = trace.record_discovery_stage(domain="ENERGY")
        rec2 = trace.record_validation_stage(domain="ENERGY", duration_ms=5.0)
        rec3 = trace.record_dependency_resolution_stage(plugin_id=pid)
        rec4 = trace.record_compatibility_stage(plugin_id=pid)
        rec5 = trace.record_sandbox_stage(sandbox_id="sbx-1", plugin_id=pid)
        rec6 = trace.record_initialization_stage(plugin_id=pid, duration_ms=3.2)
        rec7 = trace.record_registration_stage(plugin_id=pid)
        rec8 = trace.record_activation_stage(plugin_id=pid)
        records = trace.get_recent(10)
        stages = [r.stage_name for r in records]
        assert rec1.stage_name == "discovery"
        assert rec2.stage_name == "validation"
        assert rec3.stage_name == "dependency_resolution"
        assert rec4.stage_name == "compatibility_check"
        assert rec5.stage_name == "sandbox_creation"
        assert rec6.stage_name == "initialization"
        assert rec7.stage_name == "registration"
        assert rec8.stage_name == "activation"
        assert len(records) == 8
        assert len(set(stages)) == 8


# ===================================================================
# PluginHealth Phase 3.5 enhancements
# ===================================================================

class TestPluginHealthPhase35:
    def test_discovery_status_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.discovery_status == "UNKNOWN"

    def test_validation_status_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.validation_status == "UNKNOWN"

    def test_dep_resolver_status_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.dependency_resolver_status == "UNKNOWN"

    def test_compatibility_status_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.compatibility_status == "UNKNOWN"

    def test_lifecycle_status_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.lifecycle_status == "UNKNOWN"

    def test_average_load_time_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.average_load_time_ms == 0.0

    def test_error_rate_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.error_rate == 0.0

    def test_active_plugins_default(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4())
        assert h.active_plugins == 0

    def test_all_new_fields_settable(self) -> None:
        h = PluginHealth(
            plugin_id=uuid.uuid4(),
            plugin_name="energy-monitor",
            discovery_status="DISCOVERED",
            validation_status="VALIDATED",
            dependency_resolver_status="RESOLVED",
            compatibility_status="COMPATIBLE",
            lifecycle_status="ACTIVE",
            average_load_time_ms=150.0,
            error_rate=0.05,
            active_plugins=3,
            overall_status="HEALTHY",
        )
        assert h.discovery_status == "DISCOVERED"
        assert h.validation_status == "VALIDATED"
        assert h.dependency_resolver_status == "RESOLVED"
        assert h.compatibility_status == "COMPATIBLE"
        assert h.lifecycle_status == "ACTIVE"
        assert h.average_load_time_ms == 150.0
        assert h.error_rate == 0.05
        assert h.active_plugins == 3
        assert h.is_healthy() is True


# ===================================================================
# DependencyGraph Phase 3.5 enhancements
# ===================================================================

class TestDependencyGraphPhase35:
    def test_root_plugins_default(self) -> None:
        g = DependencyGraph()
        assert g.root_plugins == []

    def test_leaf_plugins_default(self) -> None:
        g = DependencyGraph()
        assert g.leaf_plugins == []

    def test_circular_dependency_reports_default(self) -> None:
        g = DependencyGraph()
        assert g.circular_dependency_reports == []

    def test_dependency_depth_default(self) -> None:
        g = DependencyGraph()
        assert g.dependency_depth == 0

    def test_load_order_default(self) -> None:
        g = DependencyGraph()
        assert g.load_order == []

    def test_unused_dependencies_default(self) -> None:
        g = DependencyGraph()
        assert g.unused_dependencies == []

    def test_graph_with_all_new_fields(self) -> None:
        g = DependencyGraph(
            nodes={"a": [], "b": ["a"]},
            root_plugins=["a"],
            leaf_plugins=["b"],
            circular_dependency_reports=[["a", "b", "a"]],
            dependency_depth=2,
            load_order=["a", "b"],
            unused_dependencies=["c"],
        )
        assert g.root_plugins == ["a"]
        assert g.leaf_plugins == ["b"]
        assert g.circular_dependency_reports == [["a", "b", "a"]]
        assert g.dependency_depth == 2
        assert g.load_order == ["a", "b"]
        assert g.unused_dependencies == ["c"]
        assert g.nodes == {"a": [], "b": ["a"]}


# ===================================================================
# PluginSandbox Phase 3.5 enhancements
# ===================================================================

class TestPluginSandboxPhase35:
    def test_health_default(self) -> None:
        s = PluginSandbox(plugin_id=uuid.uuid4(), namespace="ns")
        assert s.health == "UNKNOWN"

    def test_lifecycle_default(self) -> None:
        s = PluginSandbox(plugin_id=uuid.uuid4(), namespace="ns")
        assert s.lifecycle == "created"

    def test_assigned_capabilities_default(self) -> None:
        s = PluginSandbox(plugin_id=uuid.uuid4(), namespace="ns")
        assert s.assigned_capabilities == []

    def test_sandbox_with_all_new_fields(self) -> None:
        s = PluginSandbox(
            plugin_id=uuid.uuid4(),
            namespace="energy",
            health="HEALTHY",
            lifecycle="ACTIVE",
            assigned_capabilities=["infer", "train"],
            isolation_policy="strict",
        )
        assert s.health == "HEALTHY"
        assert s.lifecycle == "ACTIVE"
        assert s.assigned_capabilities == ["infer", "train"]
        assert s.isolation_policy == "strict"


# ===================================================================
# PluginExplainabilityMetadata Phase 3.5 enhancements
# ===================================================================

class TestExplainabilityMetadataPhase35:
    def test_why_dependency_selected_default(self) -> None:
        m = PluginExplainabilityMetadata()
        assert m.why_dependency_selected == ""

    def test_why_dependency_selected_custom(self) -> None:
        m = PluginExplainabilityMetadata(
            why_dependency_selected="Required for energy calculations"
        )
        assert m.why_dependency_selected == "Required for energy calculations"

    def test_why_dependency_failed_default(self) -> None:
        m = PluginExplainabilityMetadata()
        assert m.why_dependency_failed == ""

    def test_why_dependency_failed_custom(self) -> None:
        m = PluginExplainabilityMetadata(why_dependency_failed="Version mismatch")
        assert m.why_dependency_failed == "Version mismatch"


# ===================================================================
# PluginMetrics Phase 3.5 enhancements
# ===================================================================

class TestPluginMetricsPhase35:
    def test_lifecycle_transitions_default(self) -> None:
        m = PluginMetrics(plugin_id=uuid.uuid4())
        assert m.lifecycle_transitions == 0

    def test_dependency_failures_default(self) -> None:
        m = PluginMetrics(plugin_id=uuid.uuid4())
        assert m.dependency_failures == 0

    def test_load_latency_default(self) -> None:
        m = PluginMetrics(plugin_id=uuid.uuid4())
        assert m.load_latency_ms == 0.0

    def test_domain_usage_default(self) -> None:
        m = PluginMetrics(plugin_id=uuid.uuid4())
        assert m.domain_usage == {}

    def test_plugin_types_default(self) -> None:
        m = PluginMetrics(plugin_id=uuid.uuid4())
        assert m.plugin_types == {}

    def test_metrics_all_new_fields(self) -> None:
        m = PluginMetrics(
            plugin_id=uuid.uuid4(),
            lifecycle_transitions=5,
            dependency_failures=2,
            load_latency_ms=15.0,
            domain_usage={"ENERGY": 3},
            plugin_types={"DOMAIN": 2},
            executions_total=100,
            errors_total=3,
        )
        assert m.lifecycle_transitions == 5
        assert m.dependency_failures == 2
        assert m.load_latency_ms == 15.0
        assert m.domain_usage == {"ENERGY": 3}
        assert m.plugin_types == {"DOMAIN": 2}


# ===================================================================
# PluginMetricsCollector Phase 3.5 enhancements
# ===================================================================

class TestPluginMetricsCollectorPhase35:
    def test_increment_lifecycle_transitions(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_lifecycle_transitions()
        assert mc.snapshot().lifecycle_transitions == 1
        mc.increment_lifecycle_transitions()
        assert mc.snapshot().lifecycle_transitions == 2

    def test_increment_dependency_failures(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_dependency_failures()
        assert mc.snapshot().dependency_failures == 1

    def test_increment_domain_via_plugins(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_plugins(domain="ENERGY", plugin_type="DOMAIN")
        snapshot = mc.snapshot()
        assert snapshot.domain_usage == {"ENERGY": 1}
        assert snapshot.plugin_types == {"DOMAIN": 1}

    def test_increment_domain_and_type_multiple(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_plugins(domain="ENERGY", plugin_type="DOMAIN")
        mc.increment_plugins(domain="ENERGY", plugin_type="DOMAIN")
        mc.increment_plugins(domain="SYSTEM", plugin_type="SYSTEM")
        snapshot = mc.snapshot()
        assert snapshot.domain_usage == {"ENERGY": 2, "SYSTEM": 1}
        assert snapshot.plugin_types == {"DOMAIN": 2, "SYSTEM": 1}

    def test_record_load_time(self) -> None:
        mc = PluginMetricsCollector()
        mc.record_load_time(15.0)
        assert mc.snapshot().load_latency_ms == 15.0

    def test_reset_clears_new_fields(self) -> None:
        mc = PluginMetricsCollector()
        mc.increment_lifecycle_transitions()
        mc.increment_dependency_failures()
        mc.increment_plugins(domain="ENERGY", plugin_type="DOMAIN")
        mc.reset()
        snapshot = mc.snapshot()
        assert snapshot.lifecycle_transitions == 0
        assert snapshot.dependency_failures == 0
        assert snapshot.domain_usage == {}
        assert snapshot.plugin_types == {}


# ===================================================================
# PluginDependencyGraph Phase 3.5 enhancements
# ===================================================================

class TestPluginDependencyGraphPhase35:
    def test_create_populates_new_fields(self) -> None:
        p = _plugin()
        graph = PluginDependencyGraph()
        result = graph.create([p])
        assert isinstance(result, DependencyGraph)
        assert isinstance(result.root_plugins, list)
        assert isinstance(result.leaf_plugins, list)
        assert isinstance(result.dependency_depth, int)
        assert isinstance(result.load_order, list)
        assert isinstance(result.unused_dependencies, list)
        assert isinstance(result.circular_dependency_reports, list)

    def test_graph_roots_and_leaves(self) -> None:
        p_a = _plugin(name="plugin-a")
        p_b = _plugin(name="plugin-b")
        # No overlapping data, just check create works
        graph = PluginDependencyGraph()
        result = graph.create([p_a, p_b])
        assert "plugin-a" in result.nodes
        assert "plugin-b" in result.nodes


# ===================================================================
# PluginConfidenceCalculator Phase 3.5 enhancements
# ===================================================================

class TestConfidenceCalculatorPhase35:
    def test_signature_status_included(self) -> None:
        calc = PluginConfidenceCalculator()
        p = _plugin()
        c = calc.calculate(p)
        assert c.signature_status in ("verified", "unverified", "unknown")

    def test_confidence_calculation_returns_confidence(self) -> None:
        calc = PluginConfidenceCalculator()
        p = _plugin()
        c = calc.calculate(p)
        assert hasattr(c, "overall_confidence")
        assert hasattr(c, "signature_status")


# ===================================================================
# PluginCoordinator Phase 3.5 integration
# ===================================================================

class TestCoordinatorPhase35:
    def test_install_plugin_has_lifecycle_result(self) -> None:
        coord = PluginCoordinator()
        p = _plugin()
        decision = coord.install_plugin(p)
        assert decision.lifecycle_result != ""

    def test_install_plugin_has_reasoning(self) -> None:
        coord = PluginCoordinator()
        p = _plugin()
        decision = coord.install_plugin(p)
        assert len(decision.reasoning) > 0

    def test_health_enhanced_fields(self) -> None:
        coord = PluginCoordinator()
        p = _plugin()
        coord.install_plugin(p)
        health = coord.health()
        assert health.average_load_time_ms >= 0.0
        assert health.discovery_status != ""

    def test_metrics_enhanced_fields(self) -> None:
        coord = PluginCoordinator()
        p = _plugin()
        coord.install_plugin(p)
        metrics = coord.metrics()
        assert metrics.lifecycle_transitions >= 0
        assert isinstance(metrics.domain_usage, dict)


# ===================================================================
# Backward Compatibility
# ===================================================================

class TestBackwardCompatibilityPhase35:
    def test_plugin_health_backward_compat(self) -> None:
        h = PluginHealth(plugin_id=uuid.uuid4(), overall_status="HEALTHY")
        assert h.overall_status == "HEALTHY"
        assert h.discovery_status == "UNKNOWN"
        assert h.active_plugins == 0
        assert h.error_rate == 0.0

    def test_plugin_decision_backward_compat(self) -> None:
        d = PluginDecision(plugin_id=uuid.uuid4(), operation="install", allowed=True)
        assert d.allowed is True
        assert d.lifecycle_result == ""
        assert d.reasoning == []

    def test_plugin_confidence_backward_compat(self) -> None:
        c = PluginConfidence(overall_confidence=0.9)
        assert c.overall_confidence == 0.9
        assert c.signature_status == "unknown"

    def test_sandbox_backward_compat(self) -> None:
        s = PluginSandbox(plugin_id=uuid.uuid4(), namespace="ns")
        assert s.namespace == "ns"
        assert s.health == "UNKNOWN"
        assert s.lifecycle == "created"
        assert s.assigned_capabilities == []

    def test_dependency_graph_backward_compat(self) -> None:
        g = DependencyGraph()
        assert g.nodes == {}
        assert g.root_plugins == []
        assert g.dependency_depth == 0

    def test_metrics_backward_compat(self) -> None:
        m = PluginMetrics(plugin_id=uuid.uuid4(), executions_total=10)
        assert m.executions_total == 10
        assert m.lifecycle_transitions == 0
        assert m.domain_usage == {}

    def test_explainability_backward_compat(self) -> None:
        m = PluginExplainabilityMetadata(why_plugin_loaded="Completed")
        assert m.why_plugin_loaded == "Completed"
        assert m.why_dependency_selected == ""
        assert m.why_dependency_failed == ""
