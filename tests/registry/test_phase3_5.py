"""Phase 3.5 tests: Interface freeze, enhanced trace/metrics/confidence/coordinator.

Tests cover:
1. Interface __frozen__ markers on all 9 interfaces
2. RegistryTrace dedicated stage methods (cache, audit, policy, dependency, metrics)
3. RegistryMetricsCollector new counters
4. RegistryConfidenceCalculator 7th dimension (search_result_quality)
5. RegistryCoordinator uses new trace stages and populates new fields
6. Edge cases for new functionality
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from adip.registry.contracts.models import (
    RegistryEntry,
    RegistryFilter,
)
from adip.registry.enums import RegistryScope, RegistryType
from adip.registry.execution.metrics import RegistryMetricsCollector
from adip.registry.execution.trace import RegistryTrace
from adip.registry.interfaces import (
    BaseRegistry,
    RegistryCache,
    RegistryCoordinator,
    RegistryHealthChecker,
    RegistryLifecycleManager,
    RegistryManager,
    RegistrySearcher,
    RegistryService,
    RegistryValidator,
    RegistryVersionManager,
)
from adip.registry.orchestration.confidence import RegistryConfidenceCalculator
from adip.registry.orchestration.coordinator import RegistryCoordinator as RegistryCoordinatorImpl

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Interface Frozen Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestInterfaceFrozen:
    """All 9 registry interfaces must carry __frozen__ = True."""

    def test_base_registry_frozen(self):
        assert BaseRegistry.__frozen__ is True

    def test_registry_service_frozen(self):
        assert RegistryService.__frozen__ is True

    def test_registry_manager_frozen(self):
        assert RegistryManager.__frozen__ is True

    def test_registry_coordinator_frozen(self):
        assert RegistryCoordinator.__frozen__ is True

    def test_registry_validator_frozen(self):
        assert RegistryValidator.__frozen__ is True

    def test_registry_searcher_frozen(self):
        assert RegistrySearcher.__frozen__ is True

    def test_registry_version_manager_frozen(self):
        assert RegistryVersionManager.__frozen__ is True

    def test_registry_lifecycle_manager_frozen(self):
        assert RegistryLifecycleManager.__frozen__ is True

    def test_registry_health_checker_frozen(self):
        assert RegistryHealthChecker.__frozen__ is True

    def test_registry_cache_frozen(self):
        assert RegistryCache.__frozen__ is True

    def test_all_nine_interfaces_have_frozen_marker(self):
        interfaces = [
            BaseRegistry, RegistryService, RegistryManager, RegistryCoordinator,
            RegistryValidator, RegistrySearcher, RegistryVersionManager,
            RegistryLifecycleManager, RegistryHealthChecker, RegistryCache,
        ]
        for iface in interfaces:
            assert hasattr(iface, "__frozen__"), f"{iface.__name__} missing __frozen__"
            assert iface.__frozen__ is True, f"{iface.__name__}.__frozen__ is not True"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. RegistryTrace — Dedicated Stage Methods
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistryTracePhase35:
    """Phase 3.5 dedicated trace stage methods."""

    def test_record_cache_stage(self):
        trace = RegistryTrace()
        r = trace.record_cache_stage(
            operation="set",
            entry_id=str(uuid.uuid4()),
            registry_type="CAPABILITY",
            correlation_id="corr-1",
            cache_hit=True,
            duration_ms=5.0,
        )
        assert r.stage_name == "cache"
        assert r.operation == "set"
        assert r.success is True
        assert r.duration_ms == 5.0
        assert r.namespace == "hit"

    def test_record_cache_stage_miss(self):
        trace = RegistryTrace()
        r = trace.record_cache_stage(
            operation="get",
            cache_hit=False,
        )
        assert r.namespace == "miss"

    def test_record_audit_stage(self):
        trace = RegistryTrace()
        r = trace.record_audit_stage(
            operation="registration",
            entry_id=str(uuid.uuid4()),
            entry_name="test-entry",
            registry_type="CAPABILITY",
            correlation_id="corr-1",
            success=True,
            duration_ms=3.0,
        )
        assert r.stage_name == "audit"
        assert r.operation == "registration"
        assert r.entry_name == "test-entry"
        assert r.success is True

    def test_record_audit_stage_failure(self):
        trace = RegistryTrace()
        r = trace.record_audit_stage(
            operation="registration",
            success=False,
            errors=["audit failed"],
        )
        assert r.success is False
        assert "audit failed" in r.errors

    def test_record_policy_stage_no_violations(self):
        trace = RegistryTrace()
        r = trace.record_policy_stage(
            operation="register",
            entry_id=str(uuid.uuid4()),
            registry_type="CAPABILITY",
            violations=[],
            duration_ms=2.0,
        )
        assert r.stage_name == "policy"
        assert r.success is True
        assert r.operation == "register"

    def test_record_policy_stage_with_violations(self):
        trace = RegistryTrace()
        r = trace.record_policy_stage(
            operation="register",
            violations=["not allowed"],
            duration_ms=2.0,
        )
        assert r.success is False
        assert "not allowed" in r.errors

    def test_record_dependency_stage_no_cycles(self):
        trace = RegistryTrace()
        r = trace.record_dependency_stage(
            operation="register",
            entry_id=str(uuid.uuid4()),
            has_cycles=False,
            duration_ms=4.0,
        )
        assert r.stage_name == "dependency"
        assert r.success is True
        assert r.namespace == "ok"

    def test_record_dependency_stage_with_cycles(self):
        trace = RegistryTrace()
        r = trace.record_dependency_stage(
            operation="register",
            has_cycles=True,
            errors=["circular dependency detected"],
            duration_ms=4.0,
        )
        assert r.success is False
        assert r.namespace == "cycle_detected"

    def test_record_metrics_stage(self):
        trace = RegistryTrace()
        r = trace.record_metrics_stage(
            operation="register",
            registry_type="CAPABILITY",
            correlation_id="corr-1",
            duration_ms=1.0,
        )
        assert r.stage_name == "metrics"
        assert r.operation == "register"
        assert r.success is True


# ═══════════════════════════════════════════════════════════════════════════════
# 3. RegistryMetricsCollector — New Counters
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistryMetricsCollectorPhase35:
    """Phase 3.5 counters on RegistryMetricsCollector."""

    def test_increment_validation_failures(self):
        m = RegistryMetricsCollector()
        assert m.snapshot().validation_failures_total == 0
        m.increment_validation_failures()
        assert m.snapshot().validation_failures_total == 1
        m.increment_validation_failures()
        assert m.snapshot().validation_failures_total == 2

    def test_increment_updates(self):
        m = RegistryMetricsCollector()
        assert m.snapshot().updates_total == 0
        m.increment_updates()
        assert m.snapshot().updates_total == 1

    def test_record_cache_usage(self):
        m = RegistryMetricsCollector()
        m.record_cache_usage("key1")
        m.record_cache_usage("key1")
        m.record_cache_usage("key2")
        # Internal tracking; doesn't raise
        m.increment_cache_hits()
        snap = m.snapshot()
        assert snap.cache_hits == 1

    def test_increment_search_strategy(self):
        m = RegistryMetricsCollector()
        m.increment_search_strategy("exact")
        m.increment_search_strategy("exact")
        m.increment_search_strategy("prefix")
        snap = m.snapshot()
        assert snap.search_strategy_usage.get("exact") == 2
        assert snap.search_strategy_usage.get("prefix") == 1

    def test_increment_namespace_usage(self):
        m = RegistryMetricsCollector()
        m.increment_namespace_usage("default")
        m.increment_namespace_usage("default")
        m.increment_namespace_usage("custom")
        snap = m.snapshot()
        assert snap.namespace_usage.get("default") == 2
        assert snap.namespace_usage.get("custom") == 1

    def test_increment_registry_type_usage(self):
        m = RegistryMetricsCollector()
        m.increment_registry_type_usage("CAPABILITY")
        m.increment_registry_type_usage("SERVICE")
        snap = m.snapshot()
        assert snap.registry_types.get("CAPABILITY") == 1
        assert snap.registry_types.get("SERVICE") == 1

    def test_cache_hit_ratio(self):
        m = RegistryMetricsCollector()
        # No hits or misses → ratio = 0.0
        assert m.snapshot().cache_hit_ratio == 0.0
        # 1 hit, 0 misses → ratio = 1.0
        m.increment_cache_hits()
        assert m.snapshot().cache_hit_ratio == 1.0
        # 1 hit, 1 miss → ratio = 0.5
        m.increment_cache_misses()
        assert m.snapshot().cache_hit_ratio == 0.5

    def test_snapshot_includes_all_phase35_fields(self):
        m = RegistryMetricsCollector()
        m.increment_validation_failures()
        m.increment_updates()
        m.increment_search_strategy("exact")
        m.increment_namespace_usage("default")
        m.increment_registry_type_usage("CAPABILITY")
        m.increment_cache_hits()
        snap = m.snapshot()
        assert snap.validation_failures_total >= 0
        assert snap.updates_total >= 0
        assert snap.cache_hit_ratio >= 0.0
        assert isinstance(snap.search_strategy_usage, dict)
        assert isinstance(snap.namespace_usage, dict)
        assert isinstance(snap.registry_types, dict)

    def test_reset_clears_phase35_counters(self):
        m = RegistryMetricsCollector()
        m.increment_validation_failures()
        m.increment_updates()
        m.increment_search_strategy("exact")
        m.reset()
        snap = m.snapshot()
        assert snap.validation_failures_total == 0
        assert snap.updates_total == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. RegistryConfidenceCalculator — 7th Dimension
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistryConfidenceCalculatorPhase35:
    """Phase 3.5 adds search_result_quality as 7th dimension."""

    def test_search_result_quality_returns_7_dimensions(self):
        calc = RegistryConfidenceCalculator()
        conf = calc.calculate()
        assert conf.search_result_quality == 1.0  # None → neutral
        # Verify all 7 dimensions exist
        dims = [
            conf.metadata_completeness,
            conf.validation_quality,
            conf.version_correctness,
            conf.namespace_validity,
            conf.policy_compliance,
            conf.dependency_integrity,
            conf.search_result_quality,
        ]
        assert len(dims) == 7
        assert all(0.0 <= d <= 1.0 for d in dims)

    def test_search_result_quality_with_results(self):
        calc = RegistryConfidenceCalculator()
        conf = calc.calculate(search_result_count=5)
        assert conf.search_result_quality == 1.0

    def test_search_result_quality_no_results(self):
        calc = RegistryConfidenceCalculator()
        conf = calc.calculate(search_result_count=0)
        assert conf.search_result_quality == 0.5

    def test_search_result_quality_none_is_neutral(self):
        calc = RegistryConfidenceCalculator()
        conf = calc.calculate(search_result_count=None)
        assert conf.search_result_quality == 1.0

    def test_overall_confidence_includes_search_result_quality(self):
        calc = RegistryConfidenceCalculator()
        # All high, but search results empty
        entry = RegistryEntry(
            entry_id=uuid.uuid4(),
            name="test",
            version="1.0.0",
            owner_id="owner",
            namespace="ns",
            tags=["tag"],
            metadata={"key": "val"},
        )
        conf = calc.calculate(
            entry=entry,
            validation_violations=[],
            policy_violations=[],
            dependencies_resolved=True,
            search_result_count=0,
        )
        # 6 dimensions at 1.0 + search_result_quality at 0.5 = 6.5/7 ≈ 0.9286
        assert conf.overall_confidence == round(6.5 / 7, 4)

    def test_search_result_quality_separate_from_other_dimensions(self):
        calc = RegistryConfidenceCalculator()
        # Terrible metadata but great search results
        conf = calc.calculate(
            search_result_count=10,
        )
        assert conf.metadata_completeness == 0.0  # No entry
        assert conf.search_result_quality == 1.0  # Good results
        # Overall should be between 0 and 1
        assert 0.0 <= conf.overall_confidence <= 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 5. RegistryCoordinator Uses New Trace/Metrics/Confidence
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistryCoordinatorPhase35:
    """Coordinator Phase 3.5 enhancements: trace stages, new counters, health."""

    @pytest.fixture
    def coordinator(self):
        return RegistryCoordinatorImpl()

    def _make_entry(self, **overrides: Any) -> RegistryEntry:
        kwargs = dict(
            entry_id=uuid.uuid4(),
            name="test-entry",
            version="1.0.0",
            owner_id="user1",
            namespace="default",
            tags=["test"],
            metadata={"key": "val"},
            registry_type=RegistryType.CAPABILITY,
            scope=RegistryScope.GLOBAL,
        )
        kwargs.update(overrides)
        return RegistryEntry(**kwargs)

    def test_register_entry_uses_policy_trace(self, coordinator):
        entry = self._make_entry()
        decision = coordinator.register_entry(entry, performed_by="user1")
        traces = coordinator.trace.get_by_stage("policy")
        assert len(traces) >= 1
        trace = traces[0]
        assert trace.stage_name == "policy"
        assert trace.operation == "register"

    def test_register_entry_uses_cache_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        traces = coordinator.trace.get_by_stage("cache")
        assert len(traces) >= 1

    def test_register_entry_uses_audit_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        traces = coordinator.trace.get_by_stage("audit")
        assert len(traces) >= 1

    def test_register_entry_uses_dependency_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        traces = coordinator.trace.get_by_stage("dependency")
        assert len(traces) >= 1

    def test_register_entry_uses_metrics_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        traces = coordinator.trace.get_by_stage("metrics")
        assert len(traces) >= 1

    def test_register_entry_increments_namespace_usage(self, coordinator):
        entry = self._make_entry(namespace="custom-ns")
        coordinator.register_entry(entry, performed_by="user1")
        snap = coordinator.metrics_collector.snapshot()
        assert snap.namespace_usage.get("custom-ns", 0) >= 1

    def test_register_entry_increments_registry_type_usage(self, coordinator):
        entry = self._make_entry(registry_type=RegistryType.AGENT)
        coordinator.register_entry(entry, performed_by="user1")
        snap = coordinator.metrics_collector.snapshot()
        assert snap.registry_types.get("AGENT", 0) >= 1

    def test_update_entry_uses_policy_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        updated = entry.model_copy(update={"name": "updated-entry"})
        decision = coordinator.update_entry(updated, performed_by="user1")
        traces = coordinator.trace.get_by_stage("policy")
        policy_traces = [t for t in traces if t.operation == "update"]
        assert len(policy_traces) >= 1

    def test_update_entry_uses_cache_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        updated = entry.model_copy(update={"name": "updated-entry"})
        coordinator.update_entry(updated, performed_by="user1")
        traces = coordinator.trace.get_by_stage("cache")
        cache_traces = [t for t in traces if t.operation == "update"]
        assert len(cache_traces) >= 1

    def test_update_entry_uses_version_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        updated = entry.model_copy(update={"name": "updated-entry"})
        coordinator.update_entry(updated, performed_by="user1")
        traces = coordinator.trace.get_by_stage("version")
        assert len(traces) >= 2  # one from register, one from update

    def test_update_entry_increments_updates_metric(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        updated = entry.model_copy(update={"name": "updated-entry"})
        coordinator.update_entry(updated, performed_by="user1")
        snap = coordinator.metrics_collector.snapshot()
        assert snap.updates_total >= 1

    def test_delete_entry_uses_policy_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        decision = coordinator.delete_entry(str(entry.entry_id), performed_by="user1")
        traces = coordinator.trace.get_by_stage("policy")
        policy_traces = [t for t in traces if t.operation == "delete"]
        assert len(policy_traces) >= 1

    def test_delete_entry_uses_cache_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        coordinator.delete_entry(str(entry.entry_id), performed_by="user1")
        traces = coordinator.trace.get_by_stage("cache")
        cache_traces = [t for t in traces if t.operation == "invalidate"]
        assert len(cache_traces) >= 1

    def test_delete_entry_uses_audit_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        coordinator.delete_entry(str(entry.entry_id), performed_by="user1")
        traces = coordinator.trace.get_by_stage("audit")
        audit_traces = [t for t in traces if t.operation == "removal"]
        assert len(audit_traces) >= 1

    def test_search_uses_cache_trace_on_hit(self, coordinator):
        entry = self._make_entry(name="searchable")
        coordinator.register_entry(entry, performed_by="user1")
        # First search caches results
        filter_obj = RegistryFilter(query="searchable")
        coordinator.search(filter_obj)
        # Second search hits cache
        results = coordinator.search(filter_obj)
        traces = coordinator.trace.get_by_stage("cache")
        cache_traces = [t for t in traces if t.operation == "search_hit"]
        assert len(cache_traces) >= 1

    def test_search_uses_metrics_trace(self, coordinator):
        entry = self._make_entry(name="searchable")
        coordinator.register_entry(entry, performed_by="user1")
        filter_obj = RegistryFilter(query="searchable")
        coordinator.search(filter_obj)
        traces = coordinator.trace.get_by_stage("metrics")
        assert len(traces) >= 1

    def test_validation_failure_increments_counter(self, coordinator):
        # Create entry with empty name → validation should fail
        entry = self._make_entry(name="")
        decision = coordinator.register_entry(entry, performed_by="user1")
        if not decision.allowed:
            snap = coordinator.metrics_collector.snapshot()
            assert snap.validation_failures_total >= 1

    def test_health_includes_policy_status(self, coordinator):
        health = coordinator.health()
        assert hasattr(health, "policy_status")
        assert health.policy_status == "HEALTHY"

    def test_session_statistics_include_new_fields(self, coordinator):
        entry = self._make_entry()
        decision = coordinator.register_entry(entry, performed_by="user1")
        session_id = decision.metadata.get("session_id", "")
        session = coordinator.session_manager.get_session(session_id)
        if session:
            stats = session.statistics or {}
            assert "audit_ms" in stats
            assert "confidence_ms" in stats

    def test_coordinator_metrics_uses_new_counters(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        updated = entry.model_copy(update={"name": "updated-entry"})
        coordinator.update_entry(updated, performed_by="user1")
        metrics = coordinator.metrics()
        assert metrics.updates_total >= 1
        assert metrics.namespace_usage.get("default", 0) >= 1

    def test_register_entry_uses_version_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        traces = coordinator.trace.get_by_stage("version")
        assert len(traces) >= 1

    def test_register_entry_uses_index_trace(self, coordinator):
        entry = self._make_entry()
        coordinator.register_entry(entry, performed_by="user1")
        traces = coordinator.trace.get_by_stage("index")
        assert len(traces) >= 1

    def test_registration_session_has_complete_statistics(self, coordinator):
        entry = self._make_entry()
        decision = coordinator.register_entry(entry, performed_by="user1")
        session_id = decision.metadata.get("session_id", "")
        session = coordinator.session_manager.get_session(session_id)
        if session:
            assert session.statistics is not None


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCasesPhase35:
    """Edge cases for Phase 3.5 enhancements."""

    def test_trace_stages_are_independent(self):
        trace = RegistryTrace()
        trace.record_cache_stage(operation="set")
        trace.record_audit_stage(operation="registration")
        trace.record_policy_stage(operation="register", violations=[])
        trace.record_dependency_stage(operation="register")
        trace.record_metrics_stage(operation="register")
        assert len(trace.get_by_stage("cache")) == 1
        assert len(trace.get_by_stage("audit")) == 1
        assert len(trace.get_by_stage("policy")) == 1
        assert len(trace.get_by_stage("dependency")) == 1
        assert len(trace.get_by_stage("metrics")) == 1
        assert trace.count() == 5

    def test_cache_trace_never_fails(self):
        trace = RegistryTrace()
        r = trace.record_cache_stage(operation="get", cache_hit=False, errors=["not found"])
        assert r.success is True  # Cache stage always succeeds

    def test_policy_trace_fails_on_violations(self):
        trace = RegistryTrace()
        r = trace.record_policy_stage(operation="register", violations=["blocked"])
        assert r.success is False
        assert "blocked" in r.errors

    def test_dependency_trace_fails_on_cycles(self):
        trace = RegistryTrace()
        r = trace.record_dependency_stage(operation="register", has_cycles=True)
        assert r.success is False
        assert r.namespace == "cycle_detected"

    def test_metrics_collector_cache_usage(self):
        m = RegistryMetricsCollector()
        m.record_cache_usage("key1")
        m.record_cache_usage("key2")
        m.record_cache_usage("key1")
        # Internal tracking; snapshot doesn't expose cache_usage dict
        # but the operations should not raise
        m.increment_cache_hits()
        snap = m.snapshot()
        assert snap.cache_hits == 1

    def test_confidence_with_all_none_search_result(self):
        calc = RegistryConfidenceCalculator()
        conf = calc.calculate()
        assert conf.search_result_quality == 1.0  # neutral

    def test_confidence_search_only_dimension_differs(self):
        calc = RegistryConfidenceCalculator()
        # Only search result quality differs
        conf_with = calc.calculate(search_result_count=10)
        conf_without = calc.calculate(search_result_count=0)
        assert conf_with.search_result_quality == 1.0
        assert conf_without.search_result_quality == 0.5
        assert conf_with.overall_confidence > conf_without.overall_confidence

    def test_coordinator_trace_stages_after_blocked_register(self):
        coordinator = RegistryCoordinatorImpl()
        # Entry with empty name should fail validation
        entry = RegistryEntry(
            entry_id=uuid.uuid4(),
            name="",
            version="1.0.0",
            owner_id="user1",
            namespace="default",
        )
        decision = coordinator.register_entry(entry, performed_by="user1")
        assert not decision.allowed
        # Even blocked operations should have policy trace
        policy_traces = coordinator.trace.get_by_stage("policy")
        assert len(policy_traces) >= 1
