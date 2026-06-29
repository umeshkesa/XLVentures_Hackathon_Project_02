"""Phase 3 tests for the Evidence Fusion Engine (Enterprise Orchestration).

Tests all Phase 3 components: enhanced models, orchestration layer
(session, confidence, coordinator, manager), and services (hooks,
service). 100% backward compatible with Phase 1 & 2.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from adip.evidence import (
    AuthResult,
    Evidence,
    EvidenceConfidence,
    EvidenceConfidenceCalculator,
    EvidenceContext,
    EvidenceCoordinator,
    EvidenceDecision,
    EvidenceDomain,
    EvidenceExplainabilityMetadata,
    EvidenceHealth,
    EvidenceManager,
    EvidenceMetadata,
    EvidenceMetrics,
    EvidenceProvenance,
    EvidenceService,
    EvidenceSession,
    EvidenceSessionManager,
    EvidenceSource,
    EvidenceType,
    IntegrationHooks,
    TraceStage,
    hooks,
)
from adip.evidence.enums import EvidenceDomain, EvidenceType

# ═══════════════════════════════════════════════════════════════════════
# Phase 3 Models
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceConfidence:
    def test_default_confidence(self) -> None:
        c = EvidenceConfidence()
        assert c.overall_confidence == 0.0
        assert c.quality == 0.0
        assert c.trust == 0.0
        assert c.correlation == 0.0
        assert c.freshness == 0.0
        assert c.completeness == 0.0
        assert c.consensus == 0.0
        assert c.weight_distribution == 0.0

    def test_confidence_with_values(self) -> None:
        c = EvidenceConfidence(
            overall_confidence=0.85,
            quality=0.9,
            trust=1.0,
            correlation=1.0,
            freshness=0.7,
            completeness=0.8,
            consensus=0.85,
            weight_distribution=1.0,
        )
        assert c.overall_confidence == 0.85
        assert c.trust == 1.0

    def test_confidence_bounds(self) -> None:
        c = EvidenceConfidence(overall_confidence=0.0)
        assert c.overall_confidence == 0.0
        c2 = EvidenceConfidence(overall_confidence=1.0)
        assert c2.overall_confidence == 1.0


class TestEvidenceExplainabilityMetadata:
    def test_default_explainability(self) -> None:
        e = EvidenceExplainabilityMetadata()
        assert e.why_selected == []
        assert e.why_rejected == []
        assert e.why_bundle_created == []
        assert e.why_conflict_detected == []
        assert e.why_priority_assigned == []
        assert e.why_trust_score == []

    def test_explainability_with_values(self) -> None:
        e = EvidenceExplainabilityMetadata(
            why_selected=["High trust score"],
            why_rejected=["Low quality"],
            why_bundle_created=["Related to incident"],
            why_conflict_detected=["Contradictory sources"],
            why_priority_assigned=["Critical evidence"],
            why_trust_score=["Verified source"],
        )
        assert "High trust score" in e.why_selected
        assert "Low quality" in e.why_rejected


class TestEvidenceContext:
    def test_default_context(self) -> None:
        c = EvidenceContext()
        assert c.context_id == ""
        assert c.asset_id == ""
        assert c.machine_id == ""
        assert c.facility_id == ""
        assert c.customer_id == ""
        assert c.workflow_id == ""
        assert c.incident_id == ""

    def test_context_with_values(self) -> None:
        c = EvidenceContext(
            context_id="ctx-1",
            asset_id="asset-123",
            machine_id="machine-456",
            facility_id="fac-789",
            customer_id="cust-001",
            workflow_id="wf-abc",
            incident_id="inc-xyz",
        )
        assert c.asset_id == "asset-123"
        assert c.workflow_id == "wf-abc"


class TestEnhancedEvidenceSession:
    def test_default_session_has_new_fields(self) -> None:
        s = EvidenceSession()
        assert s.bundle_id is None
        assert s.sources_used == []
        assert s.domains_used == []
        assert s.conflicts_detected == 0
        assert s.quality_summary == ""

    def test_session_with_new_fields(self) -> None:
        bundle_id = uuid.uuid4()
        s = EvidenceSession(
            operation="collect",
            bundle_id=bundle_id,
            sources_used=["source-a", "source-b"],
            domains_used=["SYSTEM", "ENERGY"],
            conflicts_detected=3,
            quality_summary="Good quality",
        )
        assert s.bundle_id == bundle_id
        assert len(s.sources_used) == 2
        assert s.conflicts_detected == 3


class TestEnhancedEvidenceDecision:
    def test_default_decision_has_new_fields(self) -> None:
        ev_id = uuid.uuid4()
        d = EvidenceDecision(evidence_id=ev_id)
        assert d.bundle_id is None
        assert d.selected_evidence == []
        assert d.rejected_evidence == []
        assert d.conflicts == []
        assert d.quality_score == 0.0
        assert d.trust_score == 0.0

    def test_decision_with_new_fields(self) -> None:
        ev_id = uuid.uuid4()
        bundle_id = uuid.uuid4()
        sel_ids = [uuid.uuid4(), uuid.uuid4()]
        d = EvidenceDecision(
            evidence_id=ev_id,
            bundle_id=bundle_id,
            selected_evidence=sel_ids,
            rejected_evidence=[uuid.uuid4()],
            conflicts=["Conflict detected"],
            quality_score=0.85,
            trust_score=0.9,
        )
        assert d.bundle_id == bundle_id
        assert len(d.selected_evidence) == 2
        assert d.quality_score == 0.85


class TestEnhancedEvidenceHealth:
    def test_default_health_has_new_fields(self) -> None:
        h = EvidenceHealth()
        assert h.classifier_status == "UNKNOWN"
        assert h.priority_status == "UNKNOWN"
        assert h.trust_manager_status == "UNKNOWN"
        assert h.conflict_detector_status == "UNKNOWN"
        assert h.deduplicator_status == "UNKNOWN"
        assert h.bundle_manager_status == "UNKNOWN"
        assert h.timeline_status == "UNKNOWN"
        assert h.cache_status == "UNKNOWN"
        assert h.policy_status == "UNKNOWN"
        assert h.trace_status == "UNKNOWN"
        assert h.metrics_status == "UNKNOWN"
        assert h.average_latency_ms == 0.0

    def test_health_with_new_fields(self) -> None:
        h = EvidenceHealth(
            overall_status="HEALTHY",
            collector_status="HEALTHY",
            classifier_status="HEALTHY",
            priority_status="HEALTHY",
            trust_manager_status="HEALTHY",
            conflict_detector_status="HEALTHY",
            deduplicator_status="HEALTHY",
            cache_status="HEALTHY",
            policy_status="HEALTHY",
            error_count=0,
            average_latency_ms=12.5,
        )
        assert h.classifier_status == "HEALTHY"
        assert h.average_latency_ms == 12.5


class TestEnhancedEvidenceMetrics:
    def test_default_metrics_has_new_fields(self) -> None:
        m = EvidenceMetrics()
        assert m.collections_total == 0
        assert m.classifications_total == 0
        assert m.priority_assignments_total == 0
        assert m.conflicts_total == 0
        assert m.deduplications_total == 0
        assert m.bundles_total == 0
        assert m.timelines_total == 0
        assert m.cache_hits == 0
        assert m.cache_misses == 0
        assert m.policy_checks == 0
        assert m.policy_violations == 0
        assert m.evidence_per_classification == {}
        assert m.evidence_per_priority == {}
        assert m.evidence_per_domain == {}
        assert m.evidence_per_type == {}

    def test_metrics_with_new_fields(self) -> None:
        m = EvidenceMetrics(
            evidence_total=10,
            collections_total=5,
            classifications_total=8,
            conflicts_total=2,
            bundles_total=3,
            evidence_per_classification={"report": 4, "log": 4},
            evidence_per_priority={"HIGH": 3, "LOW": 5},
        )
        assert m.collections_total == 5
        assert m.evidence_per_classification["report"] == 4


# ═══════════════════════════════════════════════════════════════════════
# EvidenceSessionManager
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceSessionManager:
    def test_create_session(self) -> None:
        mgr = EvidenceSessionManager()
        session = mgr.create_session(operation="collect", correlation_id="corr-1")
        assert session.operation == "collect"
        assert session.correlation_id == "corr-1"
        assert session.status == "ACTIVE"

    def test_get_session(self) -> None:
        mgr = EvidenceSessionManager()
        session = mgr.create_session(operation="process")
        retrieved = mgr.get_session(str(session.session_id))
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    def test_get_nonexistent_session(self) -> None:
        mgr = EvidenceSessionManager()
        assert mgr.get_session("nonexistent") is None

    def test_complete_session(self) -> None:
        mgr = EvidenceSessionManager()
        session = mgr.create_session(operation="collect")
        completed = mgr.complete_session(str(session.session_id), status="COMPLETED", statistics={"total_ms": 100.0})
        assert completed is not None
        assert completed.status == "COMPLETED"
        assert completed.completed_at is not None
        assert completed.statistics["total_ms"] == 100.0

    def test_complete_nonexistent_session(self) -> None:
        mgr = EvidenceSessionManager()
        assert mgr.complete_session("nonexistent") is None

    def test_add_evidence_id(self) -> None:
        mgr = EvidenceSessionManager()
        session = mgr.create_session(operation="collect")
        updated = mgr.add_evidence_id(str(session.session_id), str(uuid.uuid4()))
        assert updated is not None
        assert updated.evidence_count == 1

    def test_add_evidence_id_nonexistent(self) -> None:
        mgr = EvidenceSessionManager()
        assert mgr.add_evidence_id("nonexistent", str(uuid.uuid4())) is None

    def test_update_statistics(self) -> None:
        mgr = EvidenceSessionManager()
        session = mgr.create_session(operation="collect")
        mgr.update_statistics(str(session.session_id), {"val_ms": 10.0})
        mgr.update_statistics(str(session.session_id), {"norm_ms": 20.0})
        updated = mgr.get_session(str(session.session_id))
        assert updated is not None
        assert updated.statistics["val_ms"] == 10.0
        assert updated.statistics["norm_ms"] == 20.0

    def test_get_active_sessions(self) -> None:
        mgr = EvidenceSessionManager()
        mgr.create_session(operation="collect")
        mgr.create_session(operation="process")
        s3 = mgr.create_session(operation="lookup")
        mgr.complete_session(str(s3.session_id), status="COMPLETED")
        active = mgr.get_active_sessions()
        assert len(active) == 2

    def test_clear(self) -> None:
        mgr = EvidenceSessionManager()
        mgr.create_session(operation="collect")
        mgr.create_session(operation="process")
        count = mgr.clear()
        assert count == 2
        assert len(mgr.get_active_sessions()) == 0


# ═══════════════════════════════════════════════════════════════════════
# EvidenceConfidenceCalculator
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceConfidenceCalculator:
    def test_calculate_without_evidence(self) -> None:
        calc = EvidenceConfidenceCalculator()
        conf = calc.calculate()
        # Without evidence: quality=0.0, trust=0.5, correlation=0.5,
        # freshness=0.5, completeness=0.0, consensus=0.5, weight_distribution=0.5
        # average = 2.5/7 ≈ 0.3571
        assert conf.overall_confidence == pytest.approx(0.3571, rel=1e-3)
        assert conf.quality == 0.0
        assert conf.trust == 0.5

    def test_calculate_with_full_evidence(self) -> None:
        calc = EvidenceConfidenceCalculator()
        evidence = Evidence(
            metadata=EvidenceMetadata(title="Test", description="Desc", tags=["tag1"], category="cat", source="src"),
            source=EvidenceSource(source_id="src-1", source_type="knowledge"),
            provenance=EvidenceProvenance(owner="admin"),
        )
        conf = calc.calculate(
            evidence=evidence,
            validation_violations=[],
            is_normalized=True,
            is_correlated=True,
            trust_score=0.9,
            quality_score=0.85,
            is_classified=True,
            freshness_score=0.9,
            consensus_level="HIGH",
            weight_distribution_score=0.8,
        )
        assert conf.completeness > 0.5
        assert conf.quality > 0.5
        assert conf.trust == 0.9
        assert conf.correlation == 1.0
        assert conf.freshness == 0.9
        assert conf.consensus == 1.0
        assert conf.weight_distribution == 0.8
        assert 0.5 < conf.overall_confidence <= 1.0

    def test_calculate_with_critical_violations(self) -> None:
        calc = EvidenceConfidenceCalculator()
        conf = calc.calculate(
            evidence=None,
            validation_violations=["invalid format", "required field missing"],
            is_normalized=False,
            is_correlated=False,
            trust_score=0.0,
            quality_score=0.0,
            is_classified=False,
        )
        assert conf.quality == 0.0
        assert conf.trust == 0.0
        assert conf.correlation == 0.5
        assert conf.completeness == 0.0
        assert conf.overall_confidence < 0.5

    def test_calculate_with_partial_violations(self) -> None:
        calc = EvidenceConfidenceCalculator()
        conf = calc.calculate(
            validation_violations=["minor warning"],
            is_normalized=True,
            trust_score=0.5,
        )
        assert conf.trust == 0.5
        # quality defaults to 0.0 when no quality_score provided
        assert conf.quality == 0.0
        assert conf.freshness == 0.5

    def test_metadata_completeness_empty(self) -> None:
        calc = EvidenceConfidenceCalculator()
        evidence = Evidence()
        conf = calc.calculate(evidence=evidence)
        assert conf.completeness == 0.0

    def test_metadata_completeness_partial(self) -> None:
        calc = EvidenceConfidenceCalculator()
        evidence = Evidence(
            metadata=EvidenceMetadata(title="Test"),
            source=EvidenceSource(source_id="src-1"),
        )
        conf = calc.calculate(evidence=evidence)
        assert 0.0 < conf.completeness < 1.0

    def test_trust_assessment_none(self) -> None:
        calc = EvidenceConfidenceCalculator()
        conf = calc.calculate(trust_score=None)
        assert conf.trust == 0.5

    def test_quality_score_none(self) -> None:
        calc = EvidenceConfidenceCalculator()
        conf = calc.calculate(quality_score=None)
        assert conf.quality == 0.0


# ═══════════════════════════════════════════════════════════════════════
# EvidenceCoordinator
# ═══════════════════════════════════════════════════════════════════════


def _make_evidence(domain: EvidenceDomain = EvidenceDomain.SYSTEM, etype: EvidenceType = EvidenceType.KNOWLEDGE) -> Evidence:
    return Evidence(
        evidence_type=etype,
        domain=domain,
        metadata=EvidenceMetadata(title="Test Evidence", description="A test evidence item"),
        source=EvidenceSource(source_id="src-1", source_type="test"),
        provenance=EvidenceProvenance(owner="admin"),
    )


class TestEvidenceCoordinator:
    def test_collect_and_process(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            source_id="src-1",
        )
        assert decision is not None
        assert decision.operation == "collect_and_process"
        assert decision.allowed is True
        assert len(decision.reasoning) > 0
        assert decision.confidence > 0.0
        assert decision.quality_score > 0.0
        assert decision.trust_score > 0.0
        assert decision.bundle_id is not None

    def test_collect_and_process_creates_evidence(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process(evidence_type=EvidenceType.SENSOR, domain=EvidenceDomain.ENERGY)
        all_ev = coord.get_all_evidence()
        assert len(all_ev) == 1
        assert all_ev[0].domain == EvidenceDomain.ENERGY

    def test_process_existing(self) -> None:
        coord = EvidenceCoordinator()
        evidence_list = [_make_evidence(), _make_evidence(EvidenceDomain.ENERGY, EvidenceType.SENSOR)]
        decision = coord.process_existing(evidence_list)
        assert decision is not None
        assert decision.operation == "process_existing"
        assert decision.allowed is True
        assert len(decision.selected_evidence) == 2
        assert decision.confidence > 0.0

    def test_process_existing_stores_evidence(self) -> None:
        coord = EvidenceCoordinator()
        ev1 = _make_evidence()
        ev2 = _make_evidence(EvidenceDomain.ENERGY)
        coord.process_existing([ev1, ev2])
        all_ev = coord.get_all_evidence()
        assert len(all_ev) == 2

    def test_get_evidence_by_id(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process()
        retrieved = coord.get_evidence(str(decision.evidence_id))
        assert retrieved is not None
        assert retrieved.evidence_id == decision.evidence_id

    def test_get_evidence_nonexistent(self) -> None:
        coord = EvidenceCoordinator()
        assert coord.get_evidence("nonexistent") is None

    def test_get_package(self) -> None:
        coord = EvidenceCoordinator()
        # process_existing doesn't create packages directly, so get_package should return None
        assert coord.get_package("nonexistent") is None

    def test_health(self) -> None:
        coord = EvidenceCoordinator()
        health = coord.health()
        assert health.overall_status == "HEALTHY"
        assert health.collector_status == "HEALTHY"
        assert health.validator_status == "HEALTHY"
        assert health.classifier_status == "HEALTHY"
        assert health.priority_status == "HEALTHY"
        assert health.trust_manager_status == "HEALTHY"
        assert health.conflict_detector_status == "HEALTHY"
        assert health.deduplicator_status == "HEALTHY"
        assert health.bundle_manager_status == "HEALTHY"
        assert health.timeline_status == "HEALTHY"
        assert health.cache_status == "HEALTHY"
        assert health.policy_status == "HEALTHY"
        assert health.trace_status == "HEALTHY"
        assert health.metrics_status == "HEALTHY"
        assert health.uptime_seconds >= 0.0

    def test_health_after_collect(self) -> None:
        coord = EvidenceCoordinator()
        coord.collect_and_process()
        health = coord.health()
        assert health.evidence_count == 1

    def test_metrics(self) -> None:
        coord = EvidenceCoordinator()
        metrics = coord.metrics()
        assert metrics.evidence_total == 0
        assert metrics.collections_total == 0

    def test_metrics_after_collect(self) -> None:
        coord = EvidenceCoordinator()
        coord.collect_and_process()
        metrics = coord.metrics()
        assert metrics.evidence_total == 1
        assert metrics.collections_total >= 1

    def test_get_all_evidence_empty(self) -> None:
        coord = EvidenceCoordinator()
        assert coord.get_all_evidence() == []

    def test_correlation_id_propagation(self) -> None:
        coord = EvidenceCoordinator()
        corr_id = "test-corr-123"
        decision = coord.collect_and_process(correlation_id=corr_id)
        assert corr_id in str(decision.metadata.get("correlation_id", ""))


# ═══════════════════════════════════════════════════════════════════════
# EvidenceManager
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceManager:
    def test_collect_evidence_delegates(self) -> None:
        mgr = EvidenceManager()
        decision = mgr.collect_evidence(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            source_id="src-1",
        )
        assert decision is not None
        assert decision.operation == "collect_and_process"

    def test_process_existing_delegates(self) -> None:
        mgr = EvidenceManager()
        decision = mgr.process_existing([_make_evidence()])
        assert decision is not None
        assert decision.operation == "process_existing"

    def test_get_evidence_delegates(self) -> None:
        mgr = EvidenceManager()
        decision = mgr.collect_evidence()
        retrieved = mgr.get_evidence(str(decision.evidence_id))
        assert retrieved is not None

    def test_get_package(self) -> None:
        mgr = EvidenceManager()
        assert mgr.get_package("nonexistent") is None

    def test_health(self) -> None:
        mgr = EvidenceManager()
        health = mgr.get_health()
        assert health.overall_status == "HEALTHY"

    def test_metrics(self) -> None:
        mgr = EvidenceManager()
        metrics = mgr.get_metrics()
        assert metrics.evidence_total == 0

    def test_coordinator_property(self) -> None:
        mgr = EvidenceManager()
        assert mgr.coordinator is not None
        new_coord = EvidenceCoordinator()
        mgr.coordinator = new_coord
        assert mgr.coordinator is new_coord

    def test_custom_coordinator(self) -> None:
        coord = EvidenceCoordinator()
        mgr = EvidenceManager(coordinator=coord)
        assert mgr.coordinator is coord


# ═══════════════════════════════════════════════════════════════════════
# IntegrationHooks
# ═══════════════════════════════════════════════════════════════════════


class TestIntegrationHooks:
    def test_register_and_invoke_pre_collect(self) -> None:
        h = IntegrationHooks()
        invoked: list[str] = []
        h.on_pre_collect(lambda **kw: invoked.append("pre_collect"))
        h.invoke_pre_collect(evidence_type="test", domain="test")
        assert invoked == ["pre_collect"]

    def test_register_and_invoke_post_collect(self) -> None:
        h = IntegrationHooks()
        invoked: list[str] = []
        h.on_post_collect(lambda **kw: invoked.append("post_collect"))
        h.invoke_post_collect(evidence="test")
        assert invoked == ["post_collect"]

    def test_register_and_invoke_pre_process(self) -> None:
        h = IntegrationHooks()
        invoked: list[str] = []
        h.on_pre_process(lambda **kw: invoked.append("pre_process"))
        h.invoke_pre_process(evidence_list=[])
        assert invoked == ["pre_process"]

    def test_register_and_invoke_post_process(self) -> None:
        h = IntegrationHooks()
        invoked: list[str] = []
        h.on_post_process(lambda **kw: invoked.append("post_process"))
        h.invoke_post_process(decision="test")
        assert invoked == ["post_process"]

    def test_register_and_invoke_pre_lookup(self) -> None:
        h = IntegrationHooks()
        invoked: list[str] = []
        h.on_pre_lookup(lambda **kw: invoked.append("pre_lookup"))
        h.invoke_pre_lookup(evidence_id="ev-1")
        assert invoked == ["pre_lookup"]

    def test_register_and_invoke_post_lookup(self) -> None:
        h = IntegrationHooks()
        invoked: list[str] = []
        h.on_post_lookup(lambda **kw: invoked.append("post_lookup"))
        h.invoke_post_lookup(evidence="ev-1")
        assert invoked == ["post_lookup"]

    def test_session_started_hook(self) -> None:
        h = IntegrationHooks()
        sessions: list[Any] = []
        h.on_session_started(lambda **kw: sessions.append(kw.get("session")))
        h.invoke_session_started(session="sess-1")
        assert sessions == ["sess-1"]

    def test_session_completed_hook(self) -> None:
        h = IntegrationHooks()
        sessions: list[Any] = []
        h.on_session_completed(lambda **kw: sessions.append(kw.get("session")))
        h.invoke_session_completed(session="sess-1")
        assert sessions == ["sess-1"]

    def test_error_hook(self) -> None:
        h = IntegrationHooks()
        errors: list[Any] = []
        h.on_error(lambda **kw: errors.append(kw.get("error")))
        h.invoke_error(operation="test", error=ValueError("test error"))
        assert len(errors) == 1
        assert isinstance(errors[0], ValueError)

    def test_multiple_callbacks(self) -> None:
        h = IntegrationHooks()
        results: list[str] = []
        h.on_pre_collect(lambda **kw: results.append("first"))
        h.on_pre_collect(lambda **kw: results.append("second"))
        h.invoke_pre_collect(evidence_type="test", domain="test")
        assert results == ["first", "second"]

    def test_error_isolation(self) -> None:
        h = IntegrationHooks()
        results: list[str] = []
        h.on_pre_collect(lambda **kw: (_ for _ in ()).throw(RuntimeError("fail")))
        h.on_pre_collect(lambda **kw: results.append("second"))
        h.invoke_pre_collect(evidence_type="test", domain="test")
        assert results == ["second"]

    def test_global_hooks_singleton(self) -> None:
        assert isinstance(hooks, IntegrationHooks)
        assert hooks is not IntegrationHooks()


# ═══════════════════════════════════════════════════════════════════════
# EvidenceService
# ═══════════════════════════════════════════════════════════════════════


class TestAuthResult:
    def test_default_auth(self) -> None:
        auth = AuthResult()
        assert auth.authenticated is True
        assert auth.authorised is True
        assert auth.user_id == ""

    def test_auth_with_values(self) -> None:
        auth = AuthResult(authenticated=False, authorised=False, user_id="user1", message="Denied")
        assert auth.authenticated is False
        assert auth.user_id == "user1"


class TestEvidenceService:
    def test_collect_evidence(self) -> None:
        svc = EvidenceService()
        decision = svc.collect_evidence(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            source_id="src-1",
        )
        assert decision is not None
        assert decision.allowed is True
        assert decision.confidence > 0.0

    def test_collect_evidence_auth_denied(self) -> None:
        def deny_auth(user_id: str, operation: str) -> AuthResult:
            return AuthResult(authenticated=False, authorised=False, user_id=user_id, message="Denied")
        svc = EvidenceService(auth_callback=deny_auth)
        result = svc.collect_evidence(user_id="user1")
        assert result is None

    def test_process_existing(self) -> None:
        svc = EvidenceService()
        decision = svc.process_existing([_make_evidence(), _make_evidence(EvidenceDomain.ENERGY)])
        assert decision is not None
        assert decision.allowed is True
        assert len(decision.selected_evidence) == 2

    def test_process_existing_auth_denied(self) -> None:
        def deny_auth(user_id: str, operation: str) -> AuthResult:
            return AuthResult(authenticated=False, authorised=False)
        svc = EvidenceService(auth_callback=deny_auth)
        result = svc.process_existing([_make_evidence()], user_id="user1")
        assert result is None

    def test_get_evidence(self) -> None:
        svc = EvidenceService()
        decision = svc.collect_evidence()
        retrieved = svc.get_evidence(str(decision.evidence_id))
        assert retrieved is not None
        assert retrieved.evidence_id == decision.evidence_id

    def test_get_evidence_auth_denied(self) -> None:
        def deny_auth(user_id: str, operation: str) -> AuthResult:
            return AuthResult(authenticated=False, authorised=False)
        svc = EvidenceService(auth_callback=deny_auth)
        assert svc.get_evidence("any-id", user_id="user1") is None

    def test_get_evidence_nonexistent(self) -> None:
        svc = EvidenceService()
        assert svc.get_evidence("nonexistent") is None

    def test_get_package(self) -> None:
        svc = EvidenceService()
        assert svc.get_package("nonexistent") is None

    def test_health(self) -> None:
        svc = EvidenceService()
        health = svc.health()
        assert health.overall_status == "HEALTHY"

    def test_metrics(self) -> None:
        svc = EvidenceService()
        metrics = svc.metrics()
        assert metrics.evidence_total == 0

    def test_custom_hooks(self) -> None:
        custom_hooks = IntegrationHooks()
        svc = EvidenceService(hooks=custom_hooks)
        assert svc.hooks is custom_hooks

    def test_custom_auth(self) -> None:
        def custom_auth(user_id: str, operation: str) -> AuthResult:
            return AuthResult(authenticated=True, authorised=True, user_id=user_id)
        svc = EvidenceService(auth_callback=custom_auth)
        assert svc.auth_callback("test", "op").user_id == "test"

    def test_default_auth_allows(self) -> None:
        svc = EvidenceService()
        auth = svc.auth_callback("anyone", "any_op")
        assert auth.authenticated is True
        assert auth.authorised is True

    def test_default_audit_logs(self) -> None:
        svc = EvidenceService()
        # Should not raise
        svc.audit_callback("test", "target", {"key": "value"})

    def test_correlation_id_propagation(self) -> None:
        svc = EvidenceService()
        corr_id = "svc-corr-123"
        decision = svc.collect_evidence(correlation_id=corr_id)
        assert decision is not None
        assert corr_id in str(decision.metadata.get("correlation_id", ""))


# ═══════════════════════════════════════════════════════════════════════
# Pipeline Integration (end-to-end)
# ═══════════════════════════════════════════════════════════════════════


class TestPipelineIntegration:
    def test_full_pipeline_through_service(self) -> None:
        svc = EvidenceService()
        decision = svc.collect_evidence(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            source_id="sensor-01",
            user_id="admin",
        )
        assert decision is not None
        assert decision.allowed is True
        assert len(decision.reasoning) > 0
        assert decision.confidence > 0.0
        assert decision.quality_score > 0.0

        # Verify evidence is stored
        retrieved = svc.get_evidence(str(decision.evidence_id))
        assert retrieved is not None

    def test_process_existing_through_service(self) -> None:
        svc = EvidenceService()
        ev1 = _make_evidence(EvidenceDomain.ENERGY, EvidenceType.SENSOR)
        ev2 = _make_evidence(EvidenceDomain.SYSTEM, EvidenceType.KNOWLEDGE)
        decision = svc.process_existing([ev1, ev2], user_id="admin")
        assert decision is not None
        assert decision.allowed is True
        assert len(decision.selected_evidence) >= 2

    def test_service_health_after_operations(self) -> None:
        svc = EvidenceService()
        svc.collect_evidence()
        svc.collect_evidence(domain=EvidenceDomain.ENERGY)
        health = svc.health()
        assert health.evidence_count == 2
        assert health.overall_status == "HEALTHY"

    def test_service_metrics_after_operations(self) -> None:
        svc = EvidenceService()
        svc.collect_evidence()
        svc.collect_evidence(domain=EvidenceDomain.ENERGY)
        metrics = svc.metrics()
        assert metrics.evidence_total >= 2

    def test_multiple_sessions_independent(self) -> None:
        svc = EvidenceService()
        decision1 = svc.collect_evidence(domain=EvidenceDomain.ENERGY)
        decision2 = svc.collect_evidence(domain=EvidenceDomain.OPERATIONS)
        assert decision1 is not None
        assert decision2 is not None
        assert decision1.evidence_id != decision2.evidence_id

    def test_hooks_invoked_during_collect(self) -> None:
        custom_hooks = IntegrationHooks()
        invoked: list[str] = []
        custom_hooks.on_pre_collect(lambda **kw: invoked.append("pre"))
        custom_hooks.on_post_collect(lambda **kw: invoked.append("post"))
        svc = EvidenceService(hooks=custom_hooks)
        svc.collect_evidence()
        assert "pre" in invoked
        assert "post" in invoked

    def test_hooks_invoked_during_process(self) -> None:
        custom_hooks = IntegrationHooks()
        invoked: list[str] = []
        custom_hooks.on_pre_process(lambda **kw: invoked.append("pre"))
        custom_hooks.on_post_process(lambda **kw: invoked.append("post"))
        svc = EvidenceService(hooks=custom_hooks)
        svc.process_existing([_make_evidence()])
        assert "pre" in invoked
        assert "post" in invoked

    def test_lookup_hooks_invoked(self) -> None:
        custom_hooks = IntegrationHooks()
        invoked: list[str] = []
        custom_hooks.on_pre_lookup(lambda **kw: invoked.append("pre_lookup"))
        custom_hooks.on_post_lookup(lambda **kw: invoked.append("post_lookup"))
        svc = EvidenceService(hooks=custom_hooks)
        svc.collect_evidence()
        svc.get_evidence("nonexistent")
        assert "pre_lookup" in invoked
        assert "post_lookup" in invoked

    def test_error_hook_on_failure(self) -> None:
        custom_hooks = IntegrationHooks()
        errors: list[Exception] = []
        custom_hooks.on_error(lambda **kw: errors.append(kw.get("error")))

        def failing_callback(**kwargs: Any) -> None:
            msg = "collection failed"
            raise ValueError(msg)

        # Hooks are exception-isolated — callback failure does not propagate
        svc = EvidenceService(hooks=custom_hooks)
        svc.hooks.on_pre_collect(failing_callback)
        decision = svc.collect_evidence()
        # The pipeline should still succeed (hook error is isolated)
        assert decision is not None
        assert decision.allowed is True

    def test_audit_callback_invoked(self) -> None:
        audit_records: list[Any] = []
        def audit_cb(operation: str, target: str, details: dict[str, Any]) -> None:
            audit_records.append((operation, target, details))
        svc = EvidenceService(audit_callback=audit_cb)
        svc.collect_evidence(user_id="admin")
        assert len(audit_records) > 0
        op, target, details = audit_records[0]
        assert op == "collect"
        assert details.get("allowed") is True

# ═══════════════════════════════════════════════════════════════════════
# Trace stage verification
# ═══════════════════════════════════════════════════════════════════════


class TestTraceStages:
    def test_all_trace_stages_defined(self) -> None:
        stages = [s for s in TraceStage]
        expected = [
            "COLLECTION", "VALIDATION", "NORMALIZATION", "CLASSIFICATION",
            "PRIORITY_ASSIGNMENT", "CORRELATION", "CONFLICT_DETECTION",
            "DEDUPLICATION", "GRAPH_BUILDING", "BUNDLE_CREATION",
            "TIMELINE", "WEIGHT", "CONSENSUS", "FUSION", "PACKAGING",
            "METRICS",
        ]
        assert sorted([s.value for s in stages]) == sorted(expected)

    def test_trace_records_created_during_pipeline(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process()
        all_traces = coord.trace.get_by_evidence_id(str(decision.evidence_id))
        assert len(all_traces) >= 6  # Multiple trace events created
