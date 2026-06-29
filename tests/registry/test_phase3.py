"""Phase 3 validation tests for the Registry Framework orchestration layer.

Tests cover RegistrySessionManager, RegistryConfidenceCalculator,
IntegrationHooks, RegistryCoordinator, RegistryManager, RegistryService,
enhanced models, pipeline integration, backward compatibility, and
edge cases.
"""

from __future__ import annotations

import uuid
from typing import Any

from adip.registry.contracts.models import (
    RegistryConfidence,
    RegistryDecision,
    RegistryEntry,
    RegistryExplainabilityMetadata,
    RegistryFilter,
    RegistryHealth,
    RegistrySession,
)
from adip.registry.enums import RegistryLifecycleStatus as RLS
from adip.registry.enums import RegistryScope, RegistryType
from adip.registry.orchestration.confidence import RegistryConfidenceCalculator
from adip.registry.orchestration.coordinator import RegistryCoordinator
from adip.registry.orchestration.manager import RegistryManager
from adip.registry.orchestration.session import RegistrySessionManager
from adip.registry.services.hooks import IntegrationHooks
from adip.registry.services.service import AuthResult, RegistryService

# ===================================================================
# Helpers
# ===================================================================

def _entry(
    name: str = "test-entry",
    version: str = "1.0.0",
    registry_type: RegistryType = RegistryType.CAPABILITY,
    scope: RegistryScope = RegistryScope.GLOBAL,
    status: RLS = RLS.REGISTERED,
    namespace: str = "default",
    tags: list[str] | None = None,
    owner_id: str = "user-1",
    metadata: dict[str, Any] | None = None,
) -> RegistryEntry:
    return RegistryEntry(
        entry_id=uuid.uuid4(),
        name=name,
        version=version,
        registry_type=registry_type,
        scope=scope,
        status=status,
        namespace=namespace,
        tags=tags or [],
        owner_id=owner_id,
        metadata=metadata or {},
    )


# ===================================================================
# RegistryConfidenceCalculator
# ===================================================================

class TestRegistryConfidenceCalculator:
    def test_calculate_empty(self) -> None:
        calc = RegistryConfidenceCalculator()
        confidence = calc.calculate()
        assert isinstance(confidence, RegistryConfidence)
        assert 0.0 <= confidence.overall_confidence <= 1.0
        assert confidence.metadata_completeness == 0.0

    def test_calculate_with_complete_entry(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="test", tags=["a"], metadata={"key": "val"})
        confidence = calc.calculate(entry=entry, validation_violations=[])
        assert confidence.overall_confidence > 0.5

    def test_calculate_with_validation_violations(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="test")
        confidence = calc.calculate(entry=entry, validation_violations=["invalid name"])
        assert confidence.validation_quality < 1.0

    def test_calculate_with_critical_violations(self) -> None:
        calc = RegistryConfidenceCalculator()
        confidence = calc.calculate(validation_violations=["entry name is required"])
        assert confidence.validation_quality == 0.0

    def test_calculate_with_policy_violations(self) -> None:
        calc = RegistryConfidenceCalculator()
        confidence = calc.calculate(policy_violations=["not allowed"])
        assert confidence.policy_compliance == 0.0

    def test_calculate_with_unresolved_dependencies(self) -> None:
        calc = RegistryConfidenceCalculator()
        confidence = calc.calculate(dependencies_resolved=False)
        assert confidence.dependency_integrity == 0.5

    def test_calculate_all_scores_in_range(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="test-entry", version="2.1.0", tags=["a"], owner_id="user")
        confidence = calc.calculate(
            entry=entry,
            validation_violations=[],
            policy_violations=[],
            dependencies_resolved=True,
        )
        assert 0.0 <= confidence.metadata_completeness <= 1.0
        assert 0.0 <= confidence.validation_quality <= 1.0
        assert 0.0 <= confidence.version_correctness <= 1.0
        assert 0.0 <= confidence.namespace_validity <= 1.0
        assert 0.0 <= confidence.policy_compliance <= 1.0
        assert 0.0 <= confidence.dependency_integrity <= 1.0
        assert 0.0 <= confidence.overall_confidence <= 1.0

    def test_version_correctness_semver(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="t", version="1.2.3")
        c = calc.calculate(entry=entry)
        assert c.version_correctness == 1.0

    def test_version_correctness_non_semver(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="t", version="latest")
        c = calc.calculate(entry=entry)
        assert c.version_correctness == 0.5

    def test_namespace_validity_valid(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="t", namespace="valid-ns")
        c = calc.calculate(entry=entry)
        assert c.namespace_validity == 1.0

    def test_namespace_validity_invalid(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="t", namespace="")
        c = calc.calculate(entry=entry)
        assert c.namespace_validity == 0.0


# ===================================================================
# RegistrySessionManager
# ===================================================================

class TestRegistrySessionManager:
    def test_create_session(self) -> None:
        mgr = RegistrySessionManager()
        session = mgr.create_session(
            registry_type=RegistryType.PLUGIN,
            operation="register",
            user_id="user-1",
            namespace="test-ns",
            correlation_id="corr-1",
            search_strategy="exact",
        )
        assert isinstance(session, RegistrySession)
        assert session.registry_type == RegistryType.PLUGIN
        assert session.operation == "register"
        assert session.user_id == "user-1"
        assert session.namespace == "test-ns"
        assert session.correlation_id == "corr-1"
        assert session.search_strategy == "exact"
        assert session.status == "ACTIVE"
        assert session.completed_at is None

    def test_get_session(self) -> None:
        mgr = RegistrySessionManager()
        created = mgr.create_session(operation="search")
        retrieved = mgr.get_session(str(created.session_id))
        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    def test_get_session_not_found(self) -> None:
        mgr = RegistrySessionManager()
        assert mgr.get_session("nonexistent") is None

    def test_complete_session(self) -> None:
        mgr = RegistrySessionManager()
        created = mgr.create_session(operation="register")
        completed = mgr.complete_session(str(created.session_id), status="COMPLETED")
        assert completed is not None
        assert completed.status == "COMPLETED"
        assert completed.completed_at is not None

    def test_complete_session_not_found(self) -> None:
        mgr = RegistrySessionManager()
        assert mgr.complete_session("nonexistent") is None

    def test_add_affected_entry(self) -> None:
        mgr = RegistrySessionManager()
        created = mgr.create_session(operation="register")
        updated = mgr.add_affected_entry(str(created.session_id), "entry-1")
        assert updated is not None
        assert "entry-1" in updated.entries_affected

    def test_add_affected_entry_dedup(self) -> None:
        mgr = RegistrySessionManager()
        created = mgr.create_session(operation="register")
        mgr.add_affected_entry(str(created.session_id), "entry-1")
        updated = mgr.add_affected_entry(str(created.session_id), "entry-1")
        assert updated is not None
        assert len(updated.entries_affected) == 1

    def test_add_affected_entry_not_found(self) -> None:
        mgr = RegistrySessionManager()
        assert mgr.add_affected_entry("nonexistent", "entry-1") is None

    def test_update_statistics(self) -> None:
        mgr = RegistrySessionManager()
        created = mgr.create_session(operation="register")
        mgr.update_statistics(str(created.session_id), {"validation_ms": 10.5})
        updated = mgr.update_statistics(str(created.session_id), {"policy_ms": 5.0})
        assert updated is not None
        assert updated.statistics["validation_ms"] == 10.5
        assert updated.statistics["policy_ms"] == 5.0

    def test_get_active_sessions(self) -> None:
        mgr = RegistrySessionManager()
        mgr.create_session(operation="register")
        mgr.create_session(operation="search")
        assert len(mgr.get_active_sessions()) == 2

    def test_get_active_sessions_after_completion(self) -> None:
        mgr = RegistrySessionManager()
        s1 = mgr.create_session(operation="register")
        mgr.create_session(operation="search")
        mgr.complete_session(str(s1.session_id))
        assert len(mgr.get_active_sessions()) == 1

    def test_clear(self) -> None:
        mgr = RegistrySessionManager()
        mgr.create_session(operation="register")
        assert mgr.clear() == 1
        assert len(mgr.get_active_sessions()) == 0


# ===================================================================
# IntegrationHooks
# ===================================================================

class TestIntegrationHooks:
    def test_register_hooks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        def cb(**kwargs: Any) -> None:
            calls.append(kwargs.get("hook_name", "called"))

        hooks.on_pre_register(lambda **kw: calls.append("pre_register"))
        hooks.on_post_register(lambda **kw: calls.append("post_register"))
        hooks.invoke_pre_register(entry="test")
        hooks.invoke_post_register(entry="test")
        assert calls == ["pre_register", "post_register"]

    def test_update_hooks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        hooks.on_pre_update(lambda **kw: calls.append("pre_update"))
        hooks.on_post_update(lambda **kw: calls.append("post_update"))
        hooks.invoke_pre_update(entry="test")
        hooks.invoke_post_update(entry="test")
        assert calls == ["pre_update", "post_update"]

    def test_delete_hooks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        hooks.on_pre_delete(lambda **kw: calls.append("pre_delete"))
        hooks.on_post_delete(lambda **kw: calls.append("post_delete"))
        hooks.invoke_pre_delete(entry_id="e1")
        hooks.invoke_post_delete(entry_id="e1")
        assert calls == ["pre_delete", "post_delete"]

    def test_search_hooks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        hooks.on_pre_search(lambda **kw: calls.append("pre_search"))
        hooks.on_post_search(lambda **kw: calls.append("post_search"))
        hooks.invoke_pre_search(query="test")
        hooks.invoke_post_search(results=[])
        assert calls == ["pre_search", "post_search"]

    def test_lookup_hooks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        hooks.on_pre_lookup(lambda **kw: calls.append("pre_lookup"))
        hooks.on_post_lookup(lambda **kw: calls.append("post_lookup"))
        hooks.invoke_pre_lookup(entry_id="e1")
        hooks.invoke_post_lookup(entry="test")
        assert calls == ["pre_lookup", "post_lookup"]

    def test_session_hooks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        hooks.on_session_started(lambda **kw: calls.append("session_started"))
        hooks.on_session_completed(lambda **kw: calls.append("session_completed"))
        hooks.invoke_session_started(session="s1")
        hooks.invoke_session_completed(session="s1")
        assert calls == ["session_started", "session_completed"]

    def test_error_hooks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        hooks.on_error(lambda **kw: calls.append("error"))
        hooks.invoke_error(operation="test", error=ValueError("test"))
        assert calls == ["error"]

    def test_exception_isolation(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        def failing(**kwargs: Any) -> None:
            raise RuntimeError("hook failed")

        def succeeding(**kwargs: Any) -> None:
            calls.append("succeeded")

        hooks.on_pre_register(failing)
        hooks.on_pre_register(succeeding)
        hooks.invoke_pre_register(entry="test")  # Should not raise
        assert calls == ["succeeded"]

    def test_multiple_callbacks(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []
        def make_cb(i: int):
            return lambda **kw: calls.append(str(i))
        for i in range(3):
            hooks.on_post_register(make_cb(i))
        hooks.invoke_post_register(entry="test")
        assert calls == ["0", "1", "2"]

    def test_global_hooks_singleton(self) -> None:
        from adip.registry.services.hooks import hooks as global_hooks
        assert isinstance(global_hooks, IntegrationHooks)


# ===================================================================
# RegistryCoordinator
# ===================================================================

class TestRegistryCoordinator:
    def test_register_entry(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="my-capability", owner_id="user-1")
        decision = coord.register_entry(entry, performed_by="user-1")
        assert isinstance(decision, RegistryDecision)
        assert decision.allowed
        assert decision.operation == "register"
        assert len(decision.reasoning) > 0
        assert decision.confidence > 0

    def test_register_entry_invalid(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="", owner_id="user-1")  # empty name = invalid
        decision = coord.register_entry(entry, performed_by="user-1")
        assert not decision.allowed
        assert len(decision.validation_result) > 0

    def test_get_entry_cached(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="cached-entry")
        coord.register_entry(entry)
        retrieved = coord.get_entry(str(entry.entry_id))
        assert retrieved is not None
        assert retrieved.name == "cached-entry"

    def test_get_entry_not_found(self) -> None:
        coord = RegistryCoordinator()
        assert coord.get_entry("nonexistent") is None

    def test_update_entry(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="update-me")
        coord.register_entry(entry)
        updated_entry = entry.model_copy(update={"name": "updated-name"})
        decision = coord.update_entry(updated_entry, performed_by="user-1")
        assert decision.allowed
        assert decision.operation == "update"
        retrieved = coord.get_entry(str(entry.entry_id))
        assert retrieved is not None
        assert retrieved.name == "updated-name"

    def test_update_entry_not_found(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="ghost")
        decision = coord.update_entry(entry)
        assert not decision.allowed
        assert "Entry not found" in decision.reasoning

    def test_delete_entry(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="delete-me")
        coord.register_entry(entry)
        decision = coord.delete_entry(str(entry.entry_id), performed_by="user-1")
        assert decision.allowed
        assert coord.get_entry(str(entry.entry_id)) is None

    def test_delete_entry_not_found(self) -> None:
        coord = RegistryCoordinator()
        decision = coord.delete_entry("nonexistent")
        assert not decision.allowed

    def test_search(self) -> None:
        coord = RegistryCoordinator()
        coord.register_entry(_entry(name="alpha"))
        coord.register_entry(_entry(name="beta"))
        results = coord.search(RegistryFilter(query="alpha"))
        assert len(results) >= 1
        assert any(r.entry.name == "alpha" for r in results)

    def test_search_no_results(self) -> None:
        coord = RegistryCoordinator()
        results = coord.search(RegistryFilter(query="nonexistent"))
        assert len(results) == 0

    def test_activate_entry(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="activate-me", status=RLS.VALIDATED)
        coord.register_entry(entry)
        decision = coord.activate_entry(str(entry.entry_id), performed_by="user-1")
        assert decision.allowed
        retrieved = coord.get_entry(str(entry.entry_id))
        assert retrieved is not None
        assert retrieved.status == RLS.ACTIVE

    def test_suspend_entry(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="suspend-me", status=RLS.VALIDATED)
        coord.register_entry(entry)
        coord.activate_entry(str(entry.entry_id))
        decision = coord.suspend_entry(str(entry.entry_id))
        assert decision.allowed

    def test_deprecate_entry(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="deprecate-me", status=RLS.VALIDATED)
        coord.register_entry(entry)
        coord.activate_entry(str(entry.entry_id))
        decision = coord.deprecate_entry(str(entry.entry_id), reason="no longer needed")
        assert decision.allowed

    def test_health(self) -> None:
        coord = RegistryCoordinator()
        health = coord.health()
        assert isinstance(health, RegistryHealth)
        assert health.overall_status in ("HEALTHY", "DEGRADED", "UNHEALTHY")
        assert health.entries_total >= 0

    def test_health_with_entries(self) -> None:
        coord = RegistryCoordinator()
        coord.register_entry(_entry(name="e1"))
        coord.register_entry(_entry(name="e2"))
        health = coord.health()
        assert health.entries_total >= 2

    def test_metrics(self) -> None:
        coord = RegistryCoordinator()
        metrics = coord.metrics()
        assert metrics is not None
        assert metrics.entries_total >= 0


# ===================================================================
# RegistryManager
# ===================================================================

class TestRegistryManager:
    def test_create_entry(self) -> None:
        mgr = RegistryManager()
        entry = _entry(name="mgr-test")
        decision = mgr.create_entry(entry, performed_by="user-1")
        assert decision.allowed

    def test_read_entry(self) -> None:
        mgr = RegistryManager()
        entry = _entry(name="mgr-read")
        mgr.create_entry(entry)
        retrieved = mgr.read_entry(str(entry.entry_id))
        assert retrieved is not None
        assert retrieved.name == "mgr-read"

    def test_read_entry_not_found(self) -> None:
        mgr = RegistryManager()
        assert mgr.read_entry("nonexistent") is None

    def test_update_entry(self) -> None:
        mgr = RegistryManager()
        entry = _entry(name="mgr-update")
        mgr.create_entry(entry)
        updated = entry.model_copy(update={"name": "mgr-updated"})
        decision = mgr.update_entry(updated, performed_by="user-1")
        assert decision.allowed

    def test_delete_entry(self) -> None:
        mgr = RegistryManager()
        entry = _entry(name="mgr-delete")
        mgr.create_entry(entry)
        decision = mgr.delete_entry(str(entry.entry_id), performed_by="user-1")
        assert decision.allowed

    def test_search_entries(self) -> None:
        mgr = RegistryManager()
        mgr.create_entry(_entry(name="search-a"))
        mgr.create_entry(_entry(name="search-b"))
        results = mgr.search_entries(query="search-a")
        assert len(results) >= 1

    def test_activate_entry(self) -> None:
        mgr = RegistryManager()
        entry = _entry(name="mgr-activate", status=RLS.VALIDATED)
        mgr.create_entry(entry)
        decision = mgr.activate_entry(str(entry.entry_id))
        assert decision.allowed

    def test_suspend_entry(self) -> None:
        mgr = RegistryManager()
        entry = _entry(name="mgr-suspend", status=RLS.VALIDATED)
        mgr.create_entry(entry)
        mgr.activate_entry(str(entry.entry_id))
        decision = mgr.suspend_entry(str(entry.entry_id))
        assert decision.allowed

    def test_deprecate_entry(self) -> None:
        mgr = RegistryManager()
        entry = _entry(name="mgr-deprecate", status=RLS.VALIDATED)
        mgr.create_entry(entry)
        mgr.activate_entry(str(entry.entry_id))
        decision = mgr.deprecate_entry(str(entry.entry_id), reason="test")
        assert decision.allowed

    def test_get_health(self) -> None:
        mgr = RegistryManager()
        health = mgr.get_health()
        assert isinstance(health, RegistryHealth)

    def test_get_metrics(self) -> None:
        mgr = RegistryManager()
        metrics = mgr.get_metrics()
        assert metrics is not None


# ===================================================================
# RegistryService
# ===================================================================

class TestRegistryService:
    def test_register_entry(self) -> None:
        svc = RegistryService()
        entry = _entry(name="svc-register")
        result = svc.register_entry(entry, user_id="user-1")
        assert result is not None
        assert result.name == "svc-register"

    def test_register_entry_auth_failure(self) -> None:
        def denying(user_id: str, operation: str) -> AuthResult:
            return AuthResult(authenticated=False, authorised=False)

        svc = RegistryService(auth_callback=denying)
        entry = _entry(name="denied")
        result = svc.register_entry(entry, user_id="user-1")
        assert result is None

    def test_get_entry(self) -> None:
        svc = RegistryService()
        entry = _entry(name="svc-get")
        svc.register_entry(entry, user_id="user-1")
        retrieved = svc.get_entry(str(entry.entry_id), user_id="user-1")
        assert retrieved is not None
        assert retrieved.name == "svc-get"

    def test_get_entry_not_found(self) -> None:
        svc = RegistryService()
        assert svc.get_entry("nonexistent") is None

    def test_get_entry_auth_failure(self) -> None:
        def denying(user_id: str, operation: str) -> AuthResult:
            return AuthResult(authenticated=False, authorised=False)

        svc = RegistryService(auth_callback=denying)
        assert svc.get_entry("any", user_id="user-1") is None

    def test_update_entry(self) -> None:
        svc = RegistryService()
        entry = _entry(name="svc-update")
        svc.register_entry(entry, user_id="user-1")
        updated = entry.model_copy(update={"name": "svc-updated"})
        result = svc.update_entry(updated, user_id="user-1")
        assert result is not None
        assert result.name == "svc-updated"

    def test_delete_entry(self) -> None:
        svc = RegistryService()
        entry = _entry(name="svc-delete")
        svc.register_entry(entry, user_id="user-1")
        deleted = svc.delete_entry(str(entry.entry_id), user_id="user-1")
        assert deleted is True
        assert svc.get_entry(str(entry.entry_id)) is None

    def test_search_entries(self) -> None:
        svc = RegistryService()
        svc.register_entry(_entry(name="svc-search-a"), user_id="user-1")
        svc.register_entry(_entry(name="svc-search-b"), user_id="user-1")
        results = svc.search_entries(RegistryFilter(query="svc-search-a"), user_id="user-1")
        assert len(results) >= 1

    def test_activate_entry(self) -> None:
        svc = RegistryService()
        entry = _entry(name="svc-activate", status=RLS.VALIDATED)
        svc.register_entry(entry, user_id="user-1")
        result = svc.activate_entry(str(entry.entry_id), user_id="user-1")
        assert result is not None
        assert result.status == RLS.ACTIVE

    def test_suspend_entry(self) -> None:
        svc = RegistryService()
        entry = _entry(name="svc-suspend", status=RLS.VALIDATED)
        svc.register_entry(entry, user_id="user-1")
        svc.activate_entry(str(entry.entry_id), user_id="user-1")
        result = svc.suspend_entry(str(entry.entry_id), user_id="user-1")
        assert result is not None
        assert result.status == RLS.SUSPENDED

    def test_deprecate_entry(self) -> None:
        svc = RegistryService()
        entry = _entry(name="svc-deprecate", status=RLS.VALIDATED)
        svc.register_entry(entry, user_id="user-1")
        svc.activate_entry(str(entry.entry_id), user_id="user-1")
        result = svc.deprecate_entry(str(entry.entry_id), user_id="user-1", reason="test")
        assert result is not None
        assert result.status == RLS.DEPRECATED

    def test_health(self) -> None:
        svc = RegistryService()
        health = svc.health()
        assert isinstance(health, RegistryHealth)

    def test_get_metrics(self) -> None:
        svc = RegistryService()
        metrics = svc.get_metrics()
        assert metrics is not None

    def test_custom_auth_callback(self) -> None:
        calls: list[str] = []

        def auth(user_id: str, operation: str) -> AuthResult:
            calls.append(f"{user_id}:{operation}")
            return AuthResult(authenticated=True, authorised=True)

        svc = RegistryService(auth_callback=auth)
        svc.register_entry(_entry(name="auth-test"), user_id="u1")
        assert "u1:register" in calls

    def test_custom_audit_callback(self) -> None:
        audits: list[tuple[str, str, dict]] = []

        def audit(operation: str, target: str, details: dict) -> None:
            audits.append((operation, target, details))

        svc = RegistryService(audit_callback=audit)
        svc.register_entry(_entry(name="audit-test"), user_id="u1")
        assert len(audits) >= 1
        op, target, details = audits[0]
        assert op == "register"
        assert target == "audit-test"

    def test_integration_hooks_invoked(self) -> None:
        calls: list[str] = []
        hooks = IntegrationHooks()
        hooks.on_pre_register(lambda **kw: calls.append("pre"))
        hooks.on_post_register(lambda **kw: calls.append("post"))

        svc = RegistryService(hooks=hooks)
        svc.register_entry(_entry(name="hook-test"), user_id="u1")
        assert "pre" in calls
        assert "post" in calls

    def test_hook_failure_isolation(self) -> None:
        hooks = IntegrationHooks()
        hooks.on_pre_register(lambda **kw: (_ for _ in ()).throw(RuntimeError("fail")))
        hooks.on_post_register(lambda **kw: None)

        svc = RegistryService(hooks=hooks)
        # Should not raise despite failing hook
        result = svc.register_entry(_entry(name="isolated-hook"), user_id="u1")
        assert result is not None

    def test_correlation_id_propagation(self) -> None:
        svc = RegistryService()
        entry = _entry(name="corr-test")
        result = svc.register_entry(entry, user_id="u1", correlation_id="my-corr-id")
        assert result is not None


# ===================================================================
# Enhanced Model Tests
# ===================================================================

class TestEnhancedModels:
    def test_registry_session_new_fields(self) -> None:
        session = RegistrySession(
            registry_type=RegistryType.PLUGIN,
            operation="register",
            search_strategy="exact",
            version_used="1.0.0",
            lifecycle_state="ACTIVE",
            statistics={"validation_ms": 10.5},
        )
        assert session.search_strategy == "exact"
        assert session.version_used == "1.0.0"
        assert session.lifecycle_state == "ACTIVE"
        assert session.statistics["validation_ms"] == 10.5

    def test_registry_session_defaults(self) -> None:
        session = RegistrySession()
        assert session.search_strategy == ""
        assert session.version_used == ""
        assert session.lifecycle_state == ""
        assert session.statistics == {}

    def test_registry_decision_new_fields(self) -> None:
        decision = RegistryDecision(
            entry_id=uuid.uuid4(),
            registry_type=RegistryType.TOOL,
            validation_result=["name is valid"],
            policy_result=["policy passed"],
            version_result="1.0.0",
            dependency_result="resolved",
            confidence=0.85,
        )
        assert decision.registry_type == RegistryType.TOOL
        assert decision.validation_result == ["name is valid"]
        assert decision.policy_result == ["policy passed"]
        assert decision.version_result == "1.0.0"
        assert decision.dependency_result == "resolved"
        assert decision.confidence == 0.85

    def test_registry_decision_defaults(self) -> None:
        decision = RegistryDecision(entry_id=uuid.uuid4())
        assert decision.registry_type == RegistryType.CAPABILITY
        assert decision.validation_result == []
        assert decision.policy_result == []
        assert decision.version_result == ""
        assert decision.dependency_result == ""

    def test_registry_health_new_fields(self) -> None:
        health = RegistryHealth(
            overall_status="HEALTHY",
            index_status="HEALTHY",
            dependency_graph_status="HEALTHY",
            average_latency_ms=15.5,
        )
        assert health.index_status == "HEALTHY"
        assert health.dependency_graph_status == "HEALTHY"
        assert health.average_latency_ms == 15.5

    def test_registry_health_defaults(self) -> None:
        health = RegistryHealth()
        assert health.index_status == "UNKNOWN"
        assert health.dependency_graph_status == "UNKNOWN"
        assert health.average_latency_ms == 0.0

    def test_registry_confidence_model(self) -> None:
        confidence = RegistryConfidence(
            overall_confidence=0.85,
            metadata_completeness=0.8,
            validation_quality=1.0,
            version_correctness=1.0,
            namespace_validity=1.0,
            policy_compliance=1.0,
            dependency_integrity=0.5,
        )
        assert confidence.overall_confidence == 0.85
        assert 0.0 <= confidence.metadata_completeness <= 1.0
        assert 0.0 <= confidence.validation_quality <= 1.0

    def test_registry_confidence_defaults(self) -> None:
        confidence = RegistryConfidence()
        assert confidence.overall_confidence == 0.0
        assert confidence.metadata_completeness == 0.0
        assert confidence.dependency_integrity == 0.0

    def test_registry_explainability_metadata(self) -> None:
        explain = RegistryExplainabilityMetadata(
            why_registered="Entry met all validation and policy checks",
            why_version_selected="Latest stable version 1.0.0",
            why_search_strategy_selected="Exact match for precise lookups",
        )
        assert explain.why_registered != ""
        assert explain.why_version_selected != ""
        assert explain.why_search_strategy_selected != ""

    def test_registry_explainability_defaults(self) -> None:
        explain = RegistryExplainabilityMetadata()
        assert explain.why_registered == ""
        assert explain.why_updated == ""
        assert explain.why_removed == ""
        assert explain.why_dependency_selected == ""

    def test_backward_compat_registry_session(self) -> None:
        """Phase 1 RegistrySession fields must still work."""
        session = RegistrySession(
            session_id=uuid.uuid4(),
            registry_type=RegistryType.CAPABILITY,
            operation="test",
            user_id="user-1",
            correlation_id="corr-1",
        )
        assert session.session_id is not None
        assert session.registry_type == RegistryType.CAPABILITY
        assert session.user_id == "user-1"

    def test_backward_compat_registry_decision(self) -> None:
        """Phase 1 RegistryDecision fields must still work."""
        decision = RegistryDecision(
            entry_id=uuid.uuid4(),
            operation="register",
            allowed=True,
            performed_by="user-1",
            validation_results=["passed"],
        )
        assert decision.operation == "register"
        assert decision.allowed is True
        assert decision.validation_results == ["passed"]


# ===================================================================
# Pipeline Integration
# ===================================================================

class TestPipelineIntegration:
    def test_full_register_lookup_pipeline(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="pipeline-test", tags=["test"])
        decision = coord.register_entry(entry)
        assert decision.allowed

        retrieved = coord.get_entry(str(entry.entry_id))
        assert retrieved is not None
        assert retrieved.name == "pipeline-test"

    def test_full_register_update_lookup_pipeline(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="pipeline-update")
        coord.register_entry(entry, performed_by="user-1")

        updated = entry.model_copy(update={"name": "pipeline-updated", "version": "1.1.0"})
        decision = coord.update_entry(updated, performed_by="user-1")
        assert decision.allowed

        retrieved = coord.get_entry(str(entry.entry_id))
        assert retrieved is not None
        assert retrieved.name == "pipeline-updated"

    def test_register_delete_lookup_pipeline(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="pipeline-delete")
        coord.register_entry(entry, performed_by="user-1")
        decision = coord.delete_entry(str(entry.entry_id), performed_by="user-1")
        assert decision.allowed
        assert coord.get_entry(str(entry.entry_id)) is None

    def test_register_search_pipeline(self) -> None:
        coord = RegistryCoordinator()
        coord.register_entry(_entry(name="unique-name-xyz"))
        results = coord.search(RegistryFilter(query="unique-name-xyz"))
        assert len(results) >= 1
        assert results[0].score >= 0.5

    def test_lifecycle_full_pipeline(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="lifecycle-full", status=RLS.VALIDATED)
        coord.register_entry(entry)

        # VALIDATED -> ACTIVE
        coord.activate_entry(str(entry.entry_id))
        e = coord.get_entry(str(entry.entry_id))
        assert e is not None
        assert e.status == RLS.ACTIVE

        # ACTIVE -> SUSPENDED
        coord.suspend_entry(str(entry.entry_id))
        e = coord.get_entry(str(entry.entry_id))
        assert e is not None
        assert e.status == RLS.SUSPENDED

        # SUSPENDED -> ACTIVE
        coord.activate_entry(str(entry.entry_id))
        e = coord.get_entry(str(entry.entry_id))
        assert e is not None
        assert e.status == RLS.ACTIVE

        # ACTIVE -> DEPRECATED
        coord.deprecate_entry(str(entry.entry_id), reason="replaced")
        e = coord.get_entry(str(entry.entry_id))
        assert e is not None
        assert e.status == RLS.DEPRECATED

    def test_metrics_collected_after_operations(self) -> None:
        coord = RegistryCoordinator()
        assert coord.metrics().entries_total == 0
        coord.register_entry(_entry(name="m1"))
        assert coord.metrics().entries_total == 1
        coord.register_entry(_entry(name="m2"))
        assert coord.metrics().entries_total == 2

    def test_trace_records_after_register(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="trace-test")
        coord.register_entry(entry)
        traces = coord.trace.get_by_operation("register")
        assert len(traces) >= 1

    def test_session_created_after_register(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="session-test")
        coord.register_entry(entry)
        # All sessions created via coordinator should be completed
        active = coord.session_manager.get_active_sessions()
        assert not any(s.correlation_id and s.operation == "register" for s in active)


# ===================================================================
# Edge Cases
# ===================================================================

class TestEdgeCases:
    def test_empty_name_registration(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="")
        decision = coord.register_entry(entry)
        assert not decision.allowed

    def test_invalid_version_registration(self) -> None:
        coord = RegistryCoordinator()
        entry = _entry(name="bad-version", version="abc")
        decision = coord.register_entry(entry)
        assert not decision.allowed

    def test_search_by_tags(self) -> None:
        coord = RegistryCoordinator()
        coord.register_entry(_entry(name="tagged-1", tags=["foo", "bar"]))
        results = coord.search(RegistryFilter(query="foo"))
        assert len(results) >= 1

    def test_search_namespace_scoped(self) -> None:
        coord = RegistryCoordinator()
        coord.register_entry(_entry(name="ns-test", namespace="custom-ns"))
        results = coord.search(RegistryFilter(query="ns-test", namespace="custom-ns"))
        assert len(results) >= 1

    def test_multiple_registrations_track_entries(self) -> None:
        coord = RegistryCoordinator()
        for i in range(5):
            coord.register_entry(_entry(name=f"multi-{i}"))
        assert len(coord.get_all_entries()) == 5

    def test_confidence_with_no_entry(self) -> None:
        calc = RegistryConfidenceCalculator()
        confidence = calc.calculate()
        assert isinstance(confidence, RegistryConfidence)
        assert confidence.overall_confidence >= 0.0

    def test_session_statistics_accumulate(self) -> None:
        mgr = RegistrySessionManager()
        s = mgr.create_session(operation="register")
        mgr.update_statistics(str(s.session_id), {"a": 1})
        mgr.update_statistics(str(s.session_id), {"b": 2})
        updated = mgr.get_session(str(s.session_id))
        assert updated is not None
        assert updated.statistics == {"a": 1, "b": 2}

    def test_global_hooks_singleton_type(self) -> None:
        from adip.registry.services.hooks import hooks
        assert isinstance(hooks, IntegrationHooks)

    def test_coordinator_health_status(self) -> None:
        coord = RegistryCoordinator()
        health = coord.health()
        assert health.overall_status == "HEALTHY"
        assert health.validator_status == "HEALTHY"
        assert health.searcher_status == "HEALTHY"
        assert health.cache_status == "HEALTHY"
        assert health.dependency_graph_status == "HEALTHY"

    def test_service_health_propagation(self) -> None:
        svc = RegistryService()
        health = svc.health()
        assert isinstance(health, RegistryHealth)
        assert health.entries_total >= 0

    def test_confidence_all_dimensions_independent(self) -> None:
        calc = RegistryConfidenceCalculator()
        entry = _entry(name="test", version="1.0.0", tags=["a"], owner_id="u")
        c1 = calc.calculate(entry=entry, validation_violations=[])
        c2 = calc.calculate(entry=entry, validation_violations=["error"])
        assert c1.validation_quality != c2.validation_quality
        assert c1.metadata_completeness == c2.metadata_completeness
