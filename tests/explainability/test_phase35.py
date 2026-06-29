"""Comprehensive tests for the Explainability Engine Phase 3.5 (Enterprise Refinement).

Tests all Phase 3.5 components:
  1. Enhanced Contract Models (why-fields, new confidence/health/metrics/session/decision fields)
  2. AudienceValidator (permissions, detail level, sections, policy compliance)
  3. ExplanationReview (narratives, citations, trace, audience, templates, policies)
  4. ExplanationVersionManager (create, get, history, active, compare, clear, count)
  5. ExplanationReadiness (READY, REVIEW_REQUIRED, INCOMPLETE)
  6. ExplanationLineage (evidence, reasoning, recommendation, explanation, query)
  7. ExplanationSnapshot (create, get, get_by_explanation, clear, count)
  8. 5-Dimension Confidence Calculator (weighted average, all fields)
  9. Enhanced Integration Hooks (decision_review, action_manager, action_engine)
 10. Enhanced ExplainabilityMetricsCollector (new counters, snapshot)
 11. Enhanced Coordinator Pipeline (review, versioning, readiness, lineage, snapshot stages)
 12. Pipeline Integration (full pipeline from request to snapshot)
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from adip.explainability.contracts.models import (
    ExplanationAudience,
    ExplanationCitation,
    ExplanationConfidence,
    ExplanationDecision,
    ExplanationHealth,
    ExplanationMetadata,
    ExplanationMetrics,
    ExplanationNarrative,
    ExplanationPackage,
    ExplanationPolicy,
    ExplanationRequest,
    ExplanationSession,
)
from adip.explainability.enums import (
    CitationType,
    ExplanationLayer,
    ExplanationStatus,
)
from adip.explainability.execution.audience_validator import AudienceValidator
from adip.explainability.execution.metrics import ExplainabilityMetricsCollector
from adip.explainability.execution.models import (
    ExplainabilityMetrics,
    ExplanationTimeline,
    QualityScore,
    TraceRecord,
)
from adip.explainability.execution.quality_manager import ExplanationQualityManager
from adip.explainability.execution.trace import ExplainabilityTrace
from adip.explainability.orchestration.audit_package import ExplanationAuditPackage
from adip.explainability.orchestration.compliance import ExplanationCompliance
from adip.explainability.orchestration.confidence import ExplanationConfidenceCalculator
from adip.explainability.orchestration.coordinator import ExplainabilityCoordinatorImpl
from adip.explainability.orchestration.export_profiles import ExplanationExportProfiles
from adip.explainability.orchestration.justification import ExplanationJustification
from adip.explainability.orchestration.lineage import ExplanationLineage
from adip.explainability.orchestration.readiness import ExplanationReadiness
from adip.explainability.orchestration.review import ExplanationReview
from adip.explainability.orchestration.snapshot import ExplanationSnapshot
from adip.explainability.orchestration.version_manager import ExplanationVersionManager
from adip.explainability.services.hooks import IntegrationHooks

# =============================================================================
# 1. Enhanced Contract Models
# =============================================================================


class TestExplainabilityMetadataEnhanced:
    """Test ExplainabilityMetadata with Phase 3.5 why-fields."""

    def test_defaults(self) -> None:
        m = ExplanationMetadata()
        assert m.why_narrative == ""
        assert m.why_citation == ""
        assert m.why_trace == ""
        assert m.why_template == ""
        assert m.why_policy == ""
        assert m.why_audience == ""

    def test_with_values(self) -> None:
        m = ExplanationMetadata(
            title="Test",
            why_narrative="Chosen for best readability",
            why_citation="Selected due to high relevance",
            why_trace="Recorded for compliance audit",
            why_template="Used executive template",
            why_policy="Applied safety policy",
            why_audience="Targeted at engineers",
        )
        assert m.why_narrative == "Chosen for best readability"
        assert m.why_citation == "Selected due to high relevance"
        assert m.why_trace == "Recorded for compliance audit"
        assert m.why_template == "Used executive template"
        assert m.why_policy == "Applied safety policy"
        assert m.why_audience == "Targeted at engineers"

    def test_backward_compatible(self) -> None:
        m = ExplanationMetadata(title="Legacy", tags=["old"])
        assert m.title == "Legacy"
        assert m.tags == ["old"]
        assert m.why_narrative == ""


class TestConfidenceEnhanced:
    """Test ExplanationConfidence with Phase 3.5 evidence_coverage and consistency."""

    def test_defaults(self) -> None:
        c = ExplanationConfidence()
        assert c.overall_confidence == 0.0
        assert c.narrative_quality == 0.0
        assert c.citation_accuracy == 0.0
        assert c.completeness == 0.0
        assert c.audience_coverage == 0.0
        assert c.evidence_coverage == 0.0
        assert c.consistency == 0.0

    def test_with_values(self) -> None:
        c = ExplanationConfidence(
            overall_confidence=0.85,
            narrative_quality=0.9,
            citation_accuracy=0.8,
            completeness=0.7,
            audience_coverage=0.75,
            evidence_coverage=0.82,
            consistency=0.88,
        )
        assert c.overall_confidence == 0.85
        assert c.evidence_coverage == 0.82
        assert c.consistency == 0.88

    def test_backward_compatible(self) -> None:
        c = ExplanationConfidence(
            overall_confidence=0.5,
            narrative_quality=0.6,
        )
        assert c.evidence_coverage == 0.0
        assert c.consistency == 0.0


class TestHealthEnhanced:
    """Test ExplanationHealth with Phase 3.5 status fields."""

    def test_defaults(self) -> None:
        h = ExplanationHealth()
        assert h.narrative_status == ""
        assert h.citation_status == ""
        assert h.trace_status == ""
        assert h.formatter_status == ""
        assert h.template_status == ""
        assert h.policy_status == ""

    def test_with_values(self) -> None:
        h = ExplanationHealth(
            overall_status="HEALTHY",
            coordinator_status="HEALTHY",
            narrative_builder_status="HEALTHY",
            citation_builder_status="HEALTHY",
            audience_formatter_status="HEALTHY",
            validator_status="HEALTHY",
            narrative_status="HEALTHY",
            citation_status="HEALTHY",
            trace_status="HEALTHY",
            formatter_status="HEALTHY",
            template_status="HEALTHY",
            policy_status="HEALTHY",
            explanation_count=10,
            error_count=1,
            average_latency_ms=150.0,
        )
        assert h.narrative_status == "HEALTHY"
        assert h.citation_status == "HEALTHY"
        assert h.trace_status == "HEALTHY"
        assert h.formatter_status == "HEALTHY"
        assert h.template_status == "HEALTHY"
        assert h.policy_status == "HEALTHY"

    def test_backward_compatible(self) -> None:
        h = ExplanationHealth(overall_status="DEGRADED")
        assert h.overall_status == "DEGRADED"
        assert h.narrative_status == ""


class TestMetricsEnhanced:
    """Test ExplanationMetrics with Phase 3.5 new fields."""

    def test_defaults(self) -> None:
        m = ExplanationMetrics()
        assert m.sessions_total == 0
        assert m.audiences_total == 0
        assert m.templates_total == 0
        assert m.citation_coverage == 0.0
        assert m.average_quality == 0.0

    def test_with_values(self) -> None:
        m = ExplanationMetrics(
            explanations_total=10,
            narratives_total=25,
            citations_total=50,
            packages_total=9,
            validated_total=8,
            failed_total=1,
            explanations_per_domain={"ENERGY": 5},
            explanations_per_layer={"ENGINEER": 6},
            average_confidence=0.78,
            average_completeness=0.82,
            sessions_total=12,
            audiences_total=4,
            templates_total=3,
            citation_coverage=0.65,
            average_quality=0.75,
        )
        assert m.sessions_total == 12
        assert m.audiences_total == 4
        assert m.templates_total == 3
        assert m.citation_coverage == 0.65
        assert m.average_quality == 0.75

    def test_backward_compatible(self) -> None:
        m = ExplanationMetrics(explanations_total=5)
        assert m.explanations_total == 5
        assert m.sessions_total == 0


class TestSessionEnhanced:
    """Test ExplanationSession with Phase 3.5 audience, template, policy, source_sessions."""

    def test_defaults(self) -> None:
        rid = uuid.uuid4()
        s = ExplanationSession(request_id=rid)
        assert s.audience == ""
        assert s.template == ""
        assert s.policy == ""
        assert s.source_sessions == []

    def test_with_values(self) -> None:
        rid = uuid.uuid4()
        s = ExplanationSession(
            request_id=rid,
            audience="ENGINEER",
            template="executive_template",
            policy="safety_policy_v2",
            source_sessions=["session-1", "session-2"],
        )
        assert s.audience == "ENGINEER"
        assert s.template == "executive_template"
        assert s.policy == "safety_policy_v2"
        assert s.source_sessions == ["session-1", "session-2"]


class TestDecisionEnhanced:
    """Test ExplanationDecision with Phase 3.5 readiness field."""

    def test_defaults(self) -> None:
        rid = uuid.uuid4()
        d = ExplanationDecision(result_id=rid)
        assert d.readiness == ""

    def test_with_values(self) -> None:
        rid = uuid.uuid4()
        d = ExplanationDecision(result_id=rid, readiness="READY")
        assert d.readiness == "READY"

    def test_backward_compatible(self) -> None:
        rid = uuid.uuid4()
        d = ExplanationDecision(result_id=rid, conclusion="Test")
        assert d.conclusion == "Test"
        assert d.readiness == ""


# =============================================================================
# 2. AudienceValidator
# =============================================================================


class TestAudienceValidator:
    def test_validate_audience_permissions_violation(self) -> None:
        av = AudienceValidator()
        policy = ExplanationPolicy(
            name="engineer_only",
            allowed_layers=[ExplanationLayer.ENGINEER],
        )
        violations = av.validate_audience_permissions(ExplanationLayer.EXECUTIVE, policy)
        assert len(violations) == 1
        assert "not in allowed layers" in violations[0]

    def test_validate_audience_permissions_allowed(self) -> None:
        av = AudienceValidator()
        policy = ExplanationPolicy(
            name="all_layers",
            allowed_layers=[
                ExplanationLayer.EXECUTIVE,
                ExplanationLayer.MANAGER,
                ExplanationLayer.ENGINEER,
            ],
        )
        violations = av.validate_audience_permissions(ExplanationLayer.EXECUTIVE, policy)
        assert violations == []

    def test_validate_audience_permissions_empty_allowed_layers(self) -> None:
        av = AudienceValidator()
        policy = ExplanationPolicy(name="no_restrictions", allowed_layers=[])
        violations = av.validate_audience_permissions(ExplanationLayer.ENGINEER, policy)
        assert violations == []

    def test_validate_detail_level_invalid(self) -> None:
        av = AudienceValidator()
        violations = av.validate_detail_level(ExplanationLayer.ENGINEER, "very_high")
        assert len(violations) == 1
        assert "Invalid detail level" in violations[0]

    def test_validate_detail_level_valid_high(self) -> None:
        av = AudienceValidator()
        violations = av.validate_detail_level(ExplanationLayer.ENGINEER, "high")
        assert violations == []

    def test_validate_detail_level_valid_medium(self) -> None:
        av = AudienceValidator()
        violations = av.validate_detail_level(ExplanationLayer.ENGINEER, "medium")
        assert violations == []

    def test_validate_detail_level_valid_low(self) -> None:
        av = AudienceValidator()
        violations = av.validate_detail_level(ExplanationLayer.ENGINEER, "low")
        assert violations == []

    def test_validate_detail_level_case_insensitive(self) -> None:
        av = AudienceValidator()
        violations = av.validate_detail_level(ExplanationLayer.ENGINEER, "HIGH")
        assert violations == []

    def test_validate_detail_level_empty(self) -> None:
        av = AudienceValidator()
        violations = av.validate_detail_level(ExplanationLayer.ENGINEER, "")
        assert violations == []

    def test_validate_required_sections_missing(self) -> None:
        av = AudienceValidator()
        violations = av.validate_required_sections(ExplanationLayer.ENGINEER, ["summary"])
        assert len(violations) == 3
        assert any("evidence" in v for v in violations)
        assert any("reasoning" in v for v in violations)
        assert any("recommendation" in v for v in violations)

    def test_validate_required_sections_all_present(self) -> None:
        av = AudienceValidator()
        violations = av.validate_required_sections(
            ExplanationLayer.ENGINEER,
            ["summary", "evidence", "reasoning", "recommendation"],
        )
        assert violations == []

    def test_validate_required_sections_empty(self) -> None:
        av = AudienceValidator()
        violations = av.validate_required_sections(ExplanationLayer.ENGINEER, [])
        assert len(violations) == 4

    def test_validate_policy_compliance_returns_all_violations(self) -> None:
        av = AudienceValidator()
        policy = ExplanationPolicy(
            name="exec_only",
            allowed_layers=[ExplanationLayer.EXECUTIVE],
        )
        violations = av.validate_policy_compliance(
            ExplanationLayer.ENGINEER,
            policy,
            "invalid_level",
            ["summary"],
        )
        assert len(violations) >= 2

    def test_validate_policy_compliance_clean(self) -> None:
        av = AudienceValidator()
        policy = ExplanationPolicy(
            name="all_layers",
            allowed_layers=[ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE],
        )
        violations = av.validate_policy_compliance(
            ExplanationLayer.ENGINEER,
            policy,
            "high",
            ["summary", "evidence", "reasoning", "recommendation"],
        )
        assert violations == []

    def test_register_and_get_audience(self) -> None:
        av = AudienceValidator()
        audience = ExplanationAudience(
            layer=ExplanationLayer.ENGINEER,
            name="Engineers",
            required_detail_level="high",
        )
        av.register_audience(audience)
        retrieved = av.get_audience(str(audience.audience_id))
        assert retrieved is not None
        assert retrieved.name == "Engineers"

    def test_get_audience_not_found(self) -> None:
        av = AudienceValidator()
        assert av.get_audience("nonexistent") is None

    def test_register_and_get_policy(self) -> None:
        av = AudienceValidator()
        policy = ExplanationPolicy(name="test_policy", allowed_layers=[ExplanationLayer.ENGINEER])
        av.register_policy(policy)
        retrieved = av.get_policy(str(policy.policy_id))
        assert retrieved is not None
        assert retrieved.name == "test_policy"

    def test_get_policy_not_found(self) -> None:
        av = AudienceValidator()
        assert av.get_policy("nonexistent") is None


# =============================================================================
# 3. ExplanationReview
# =============================================================================


class TestExplanationReview:
    def test_review_narratives_empty(self) -> None:
        r = ExplanationReview()
        warnings = r.review_narratives([])
        assert warnings == []

    def test_review_narratives_valid(self) -> None:
        r = ExplanationReview()
        narratives = [
            ExplanationNarrative(
                package_id=uuid.uuid4(),
                title="Test",
                content="Content",
                audience=ExplanationLayer.ENGINEER,
            ),
        ]
        warnings = r.review_narratives(narratives)
        assert warnings == []

    def test_review_narratives_missing_title(self) -> None:
        r = ExplanationReview()
        narratives = [
            ExplanationNarrative(
                package_id=uuid.uuid4(),
                title="",
                content="Content",
                audience=ExplanationLayer.ENGINEER,
            ),
        ]
        warnings = r.review_narratives(narratives)
        assert len(warnings) == 1
        assert "missing title" in warnings[0]

    def test_review_narratives_missing_content(self) -> None:
        r = ExplanationReview()
        narratives = [
            ExplanationNarrative(
                package_id=uuid.uuid4(),
                title="Test",
                content="",
                audience=ExplanationLayer.ENGINEER,
            ),
        ]
        warnings = r.review_narratives(narratives)
        assert len(warnings) == 1
        assert "missing content" in warnings[0]

    def test_review_narratives_missing_audience(self) -> None:
        r = ExplanationReview()
        # Create a dict-like object without audience
        narrative = type("Narrative", (), {"title": "Test", "content": "Content", "audience": None})()
        warnings = r.review_narratives([narrative])
        assert len(warnings) == 1
        assert "missing audience" in warnings[0]

    def test_review_narratives_multiple_issues(self) -> None:
        r = ExplanationReview()
        narratives = [
            ExplanationNarrative(
                package_id=uuid.uuid4(),
                title="",
                content="",
                audience=ExplanationLayer.ENGINEER,
            ),
        ]
        warnings = r.review_narratives(narratives)
        assert len(warnings) == 2

    def test_review_citations_empty(self) -> None:
        r = ExplanationReview()
        warnings = r.review_citations([])
        assert warnings == []

    def test_review_citations_valid(self) -> None:
        r = ExplanationReview()
        citations = [
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type=CitationType.EVIDENCE,
                source_id="src-1",
                source_type="evidence",
                excerpt="Some excerpt",
            ),
        ]
        warnings = r.review_citations(citations)
        assert warnings == []

    def test_review_citations_missing_source_id(self) -> None:
        r = ExplanationReview()
        citations = [
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type=CitationType.EVIDENCE,
                source_id="",
                source_type="evidence",
                excerpt="Some excerpt",
            ),
        ]
        warnings = r.review_citations(citations)
        assert len(warnings) == 1
        assert "missing source_id" in warnings[0]

    def test_review_citations_missing_source_type(self) -> None:
        r = ExplanationReview()
        citations = [
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type=CitationType.EVIDENCE,
                source_id="src-1",
                source_type="",
                excerpt="Some excerpt",
            ),
        ]
        warnings = r.review_citations(citations)
        assert len(warnings) == 1
        assert "missing source_type" in warnings[0]

    def test_review_citations_missing_excerpt(self) -> None:
        r = ExplanationReview()
        citations = [
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type=CitationType.EVIDENCE,
                source_id="src-1",
                source_type="evidence",
                excerpt="",
            ),
        ]
        warnings = r.review_citations(citations)
        assert len(warnings) == 1
        assert "missing excerpt" in warnings[0]

    def test_review_trace_complete(self) -> None:
        r = ExplanationReview()
        traces = [
            TraceRecord(stage_name="INITIALIZED"),
            TraceRecord(stage_name="VALIDATION"),
            TraceRecord(stage_name="QUALITY"),
            TraceRecord(stage_name="CONFIDENCE"),
            TraceRecord(stage_name="COMPLETED"),
        ]
        warnings = r.review_trace(traces)
        assert warnings == []

    def test_review_trace_missing_stages(self) -> None:
        r = ExplanationReview()
        traces = [
            TraceRecord(stage_name="INITIALIZED"),
            TraceRecord(stage_name="COMPLETED"),
        ]
        warnings = r.review_trace(traces)
        assert len(warnings) >= 3

    def test_review_trace_empty(self) -> None:
        r = ExplanationReview()
        warnings = r.review_trace([])
        assert len(warnings) == 5

    def test_review_audience_valid(self) -> None:
        r = ExplanationReview()
        warnings = r.review_audience(ExplanationLayer.ENGINEER)
        assert warnings == []

    def test_review_audience_executive(self) -> None:
        r = ExplanationReview()
        warnings = r.review_audience(ExplanationLayer.EXECUTIVE)
        assert warnings == []

    def test_review_audience_invalid_string(self) -> None:
        r = ExplanationReview()
        warnings = r.review_audience("INVALID_AUDIENCE")
        assert len(warnings) == 1
        assert "Invalid audience type" in warnings[0]

    def test_review_templates_valid(self) -> None:
        r = ExplanationReview()
        template = type("Template", (), {"sections": ["summary", "evidence"]})()
        warnings = r.review_templates([template])
        assert warnings == []

    def test_review_templates_no_sections(self) -> None:
        r = ExplanationReview()
        template = type("Template", (), {"sections": None})()
        warnings = r.review_templates([template])
        assert len(warnings) == 1
        assert "no sections" in warnings[0]

    def test_review_templates_empty_list(self) -> None:
        r = ExplanationReview()
        warnings = r.review_templates([])
        assert warnings == []

    def test_review_policies_valid(self) -> None:
        r = ExplanationReview()
        policy = type("Policy", (), {"allowed_layers": [ExplanationLayer.ENGINEER]})()
        warnings = r.review_policies([policy])
        assert warnings == []

    def test_review_policies_no_allowed_layers(self) -> None:
        r = ExplanationReview()
        policy = type("Policy", (), {"allowed_layers": None})()
        warnings = r.review_policies([policy])
        assert len(warnings) == 1
        assert "no allowed_layers" in warnings[0]

    def test_review_runs_all_reviews(self) -> None:
        r = ExplanationReview()
        package = ExplanationPackage(result_id=uuid.uuid4())
        narratives = [
            ExplanationNarrative(
                package_id=uuid.uuid4(),
                title="Test",
                content="Content",
                audience=ExplanationLayer.ENGINEER,
            ),
        ]
        citations = [
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type=CitationType.EVIDENCE,
                source_id="src-1",
                source_type="evidence",
                excerpt="Excerpt",
            ),
        ]
        policies = [type("Policy", (), {"allowed_layers": [ExplanationLayer.ENGINEER]})()]
        results = r.review(package, narratives, citations, policies)
        assert isinstance(results, dict)
        assert "narratives" in results
        assert "citations" in results
        assert "audience" in results
        assert "policies" in results

    def test_review_no_primary_narrative(self) -> None:
        r = ExplanationReview()
        package = ExplanationPackage(result_id=uuid.uuid4(), primary_narrative=None)
        results = r.review(package, [], [], [])
        assert "No primary narrative" in results.get("audience", [])


# =============================================================================
# 4. ExplanationVersionManager
# =============================================================================


class TestExplanationVersionManager:
    def test_create_version(self) -> None:
        vm = ExplanationVersionManager()
        version = vm.create_version(explanation_id="exp-1")
        assert version is not None
        assert version["explanation_id"] == "exp-1"
        assert version["version_number"] == 1
        assert version["is_active"] is False
        assert version["narrative_count"] == 0
        assert version["citation_count"] == 0
        assert version["trace_count"] == 0
        assert "version_id" in version
        assert "created_at" in version

    def test_create_version_with_data(self) -> None:
        vm = ExplanationVersionManager()
        version = vm.create_version(
            explanation_id="exp-1",
            narratives=[{"id": "n-1"}],
            citations=[{"id": "c-1"}, {"id": "c-2"}],
            trace=[{"stage": "INITIALIZED"}],
        )
        assert version["narrative_count"] == 1
        assert version["citation_count"] == 2
        assert version["trace_count"] == 1

    def test_get_version_found(self) -> None:
        vm = ExplanationVersionManager()
        created = vm.create_version(explanation_id="exp-1")
        retrieved = vm.get_version(created["version_id"])
        assert retrieved is not None
        assert retrieved["version_id"] == created["version_id"]

    def test_get_version_not_found(self) -> None:
        vm = ExplanationVersionManager()
        assert vm.get_version("nonexistent") is None

    def test_get_version_history(self) -> None:
        vm = ExplanationVersionManager()
        vm.create_version(explanation_id="exp-1")
        vm.create_version(explanation_id="exp-1")
        vm.create_version(explanation_id="exp-1")
        history = vm.get_version_history("exp-1")
        assert len(history) == 3

    def test_get_version_history_empty(self) -> None:
        vm = ExplanationVersionManager()
        assert vm.get_version_history("nonexistent") == []

    def test_get_active_version_returns_latest_by_default(self) -> None:
        vm = ExplanationVersionManager()
        v1 = vm.create_version(explanation_id="exp-1")
        v2 = vm.create_version(explanation_id="exp-1")
        active = vm.get_active_version("exp-1")
        assert active is not None
        assert active["version_id"] == v2["version_id"]

    def test_get_active_version_nonexistent(self) -> None:
        vm = ExplanationVersionManager()
        assert vm.get_active_version("nonexistent") is None

    def test_set_active_version(self) -> None:
        vm = ExplanationVersionManager()
        v1 = vm.create_version(explanation_id="exp-1")
        v2 = vm.create_version(explanation_id="exp-1")
        result = vm.set_active_version("exp-1", v1["version_id"])
        assert result is True
        active = vm.get_active_version("exp-1")
        assert active is not None
        assert active["version_id"] == v1["version_id"]
        assert active["is_active"] is True

    def test_set_active_version_unknown(self) -> None:
        vm = ExplanationVersionManager()
        result = vm.set_active_version("exp-1", "nonexistent")
        assert result is False

    def test_set_active_version_wrong_explanation(self) -> None:
        vm = ExplanationVersionManager()
        v1 = vm.create_version(explanation_id="exp-1")
        result = vm.set_active_version("exp-2", v1["version_id"])
        assert result is False

    def test_compare_versions(self) -> None:
        vm = ExplanationVersionManager()
        v1 = vm.create_version(explanation_id="exp-1", narratives=[{"id": "n-1"}])
        v2 = vm.create_version(explanation_id="exp-1", narratives=[{"id": "n-1"}, {"id": "n-2"}])
        comparison = vm.compare_versions(v1["version_id"], v2["version_id"])
        assert comparison["version_1_exists"] is True
        assert comparison["version_2_exists"] is True
        assert comparison["narrative_count_changed"] is True

    def test_compare_versions_identical(self) -> None:
        vm = ExplanationVersionManager()
        v1 = vm.create_version(explanation_id="exp-1")
        v2 = vm.create_version(explanation_id="exp-1")
        comparison = vm.compare_versions(v1["version_id"], v2["version_id"])
        assert comparison["narrative_count_changed"] is False
        assert comparison["citation_count_changed"] is False

    def test_compare_versions_one_missing(self) -> None:
        vm = ExplanationVersionManager()
        v1 = vm.create_version(explanation_id="exp-1")
        comparison = vm.compare_versions(v1["version_id"], "nonexistent")
        assert comparison["version_1_exists"] is True
        assert comparison["version_2_exists"] is False

    def test_clear(self) -> None:
        vm = ExplanationVersionManager()
        vm.create_version(explanation_id="exp-1")
        vm.clear()
        assert vm.count() == 0

    def test_count(self) -> None:
        vm = ExplanationVersionManager()
        assert vm.count() == 0
        vm.create_version(explanation_id="exp-1")
        assert vm.count() == 1
        vm.create_version(explanation_id="exp-1")
        assert vm.count() == 2


# =============================================================================
# 5. ExplanationReadiness
# =============================================================================


class TestExplanationReadiness:
    def test_assess_ready(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.8,
            quality_score=0.8,
            review_results={},
        )
        assert status == "READY"

    def test_assess_ready_no_warnings(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.7,
            quality_score=0.7,
            review_results={"narratives": [], "citations": []},
        )
        assert status == "READY"

    def test_assess_review_required_low_confidence(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.5,
            quality_score=0.8,
            review_results={},
        )
        assert status == "REVIEW_REQUIRED"

    def test_assess_review_required_low_quality(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.8,
            quality_score=0.5,
            review_results={},
        )
        assert status == "REVIEW_REQUIRED"

    def test_assess_review_required_with_warnings(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.8,
            quality_score=0.8,
            review_results={"narratives": ["Missing title"]},
        )
        assert status == "REVIEW_REQUIRED"

    def test_assess_incomplete_low_confidence(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.3,
            quality_score=0.8,
            review_results={},
        )
        assert status == "INCOMPLETE"

    def test_assess_incomplete_low_quality(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.8,
            quality_score=0.3,
            review_results={},
        )
        assert status == "INCOMPLETE"

    def test_assess_incomplete_both_low(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.4,
            quality_score=0.4,
            review_results={},
        )
        assert status == "INCOMPLETE"

    def test_assess_with_correlation_id(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.9,
            quality_score=0.9,
            review_results={},
            correlation_id="cid-123",
        )
        assert status == "READY"


# =============================================================================
# 6. ExplanationLineage
# =============================================================================


class TestExplanationLineage:
    def test_record_evidence(self) -> None:
        ll = ExplanationLineage()
        entry = ll.record_evidence(source_id="ev-1", explanation_id="exp-1")
        assert entry["source_type"] == "evidence"
        assert entry["source_id"] == "ev-1"
        assert entry["explanation_id"] == "exp-1"
        assert "entry_id" in entry

    def test_record_reasoning(self) -> None:
        ll = ExplanationLineage()
        entry = ll.record_reasoning(source_id="rs-1", explanation_id="exp-1")
        assert entry["source_type"] == "reasoning"
        assert entry["source_id"] == "rs-1"

    def test_record_recommendation(self) -> None:
        ll = ExplanationLineage()
        entry = ll.record_recommendation(source_id="rc-1", explanation_id="exp-1")
        assert entry["source_type"] == "recommendation"
        assert entry["source_id"] == "rc-1"

    def test_record_explanation(self) -> None:
        ll = ExplanationLineage()
        entry = ll.record_explanation(source_id="exp-0", explanation_id="exp-1")
        assert entry["source_type"] == "explanation"
        assert entry["source_id"] == "exp-0"

    def test_get_lineage(self) -> None:
        ll = ExplanationLineage()
        ll.record_evidence(source_id="ev-1", explanation_id="exp-1")
        ll.record_reasoning(source_id="rs-1", explanation_id="exp-1")
        ll.record_recommendation(source_id="rc-1", explanation_id="exp-2")
        entries = ll.get_lineage("exp-1")
        assert len(entries) == 2
        assert all(e["explanation_id"] == "exp-1" for e in entries)

    def test_get_lineage_empty(self) -> None:
        ll = ExplanationLineage()
        assert ll.get_lineage("nonexistent") == []

    def test_get_by_source(self) -> None:
        ll = ExplanationLineage()
        ll.record_evidence(source_id="ev-1", explanation_id="exp-1")
        ll.record_evidence(source_id="ev-1", explanation_id="exp-2")
        ll.record_reasoning(source_id="rs-1", explanation_id="exp-1")
        entries = ll.get_by_source("ev-1")
        assert len(entries) == 2
        assert all(e["source_id"] == "ev-1" for e in entries)

    def test_get_by_source_empty(self) -> None:
        ll = ExplanationLineage()
        assert ll.get_by_source("nonexistent") == []

    def test_get_all(self) -> None:
        ll = ExplanationLineage()
        assert len(ll.get_all()) == 0
        ll.record_evidence(source_id="ev-1", explanation_id="exp-1")
        assert len(ll.get_all()) == 1
        ll.record_reasoning(source_id="rs-1", explanation_id="exp-1")
        assert len(ll.get_all()) == 2

    def test_clear(self) -> None:
        ll = ExplanationLineage()
        ll.record_evidence(source_id="ev-1", explanation_id="exp-1")
        ll.clear()
        assert ll.count() == 0

    def test_count(self) -> None:
        ll = ExplanationLineage()
        assert ll.count() == 0
        ll.record_evidence(source_id="ev-1", explanation_id="exp-1")
        assert ll.count() == 1
        ll.record_reasoning(source_id="rs-1", explanation_id="exp-1")
        assert ll.count() == 2


# =============================================================================
# 7. ExplanationSnapshot
# =============================================================================


class TestExplanationSnapshot:
    def _make_timeline(self) -> Any:
        return ExplanationTimeline(events=[{"event": "e1"}, {"event": "e2"}])

    def test_create(self) -> None:
        ss = ExplanationSnapshot()
        package = ExplanationPackage(result_id=uuid.uuid4())
        timeline = self._make_timeline()
        snapshot = ss.create(
            package=package,
            narratives=[{"id": "n-1"}],
            citations=[{"id": "c-1"}, {"id": "c-2"}],
            trace=[{"stage": "INITIALIZED"}],
            timeline=timeline,
        )
        assert snapshot is not None
        assert snapshot["package_id"] == str(package.package_id)
        assert snapshot["narrative_count"] == 1
        assert snapshot["citation_count"] == 2
        assert snapshot["trace_count"] == 1
        assert "snapshot_id" in snapshot
        assert "created_at" in snapshot

    def test_create_with_empty_data(self) -> None:
        ss = ExplanationSnapshot()
        package = ExplanationPackage(result_id=uuid.uuid4())
        timeline = self._make_timeline()
        snapshot = ss.create(
            package=package,
            narratives=[],
            citations=[],
            trace=[],
            timeline=timeline,
        )
        assert snapshot["narrative_count"] == 0
        assert snapshot["citation_count"] == 0

    def test_get_found(self) -> None:
        ss = ExplanationSnapshot()
        package = ExplanationPackage(result_id=uuid.uuid4())
        timeline = self._make_timeline()
        created = ss.create(package=package, narratives=[], citations=[], trace=[], timeline=timeline)
        retrieved = ss.get(created["snapshot_id"])
        assert retrieved is not None
        assert retrieved["snapshot_id"] == created["snapshot_id"]

    def test_get_not_found(self) -> None:
        ss = ExplanationSnapshot()
        assert ss.get("nonexistent") is None

    def test_get_by_explanation(self) -> None:
        ss = ExplanationSnapshot()
        package = ExplanationPackage(result_id=uuid.uuid4())
        pid = str(package.package_id)
        timeline = self._make_timeline()
        ss.create(package=package, narratives=[], citations=[], trace=[], timeline=timeline)
        ss.create(package=package, narratives=[], citations=[], trace=[], timeline=timeline)
        snapshots = ss.get_by_explanation(pid)
        assert len(snapshots) == 2

    def test_get_by_explanation_nonexistent(self) -> None:
        ss = ExplanationSnapshot()
        assert ss.get_by_explanation("nonexistent") == []

    def test_clear(self) -> None:
        ss = ExplanationSnapshot()
        package = ExplanationPackage(result_id=uuid.uuid4())
        timeline = self._make_timeline()
        ss.create(package=package, narratives=[], citations=[], trace=[], timeline=timeline)
        ss.clear()
        assert ss.count() == 0

    def test_count(self) -> None:
        ss = ExplanationSnapshot()
        assert ss.count() == 0
        package = ExplanationPackage(result_id=uuid.uuid4())
        timeline = self._make_timeline()
        ss.create(package=package, narratives=[], citations=[], trace=[], timeline=timeline)
        assert ss.count() == 1
        ss.create(package=package, narratives=[], citations=[], trace=[], timeline=timeline)
        assert ss.count() == 2


# =============================================================================
# 8. 5-Dimension Confidence Calculator
# =============================================================================


class TestConfidenceCalculator5Dimension:
    """Test ExplanationConfidenceCalculator with Phase 3.5 evidence_coverage and consistency."""

    def _make_package(self) -> ExplanationPackage:
        return ExplanationPackage(result_id=uuid.uuid4())

    def test_calculate_uses_5_dimensions(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore(
            completeness=1.0,
            citation_coverage=1.0,
            trace_coverage=1.0,
            consistency=1.0,
        )
        c = cc.calculate(package, quality)
        # citation_coverage = 1.0 (20%)
        # trace_completeness = 1.0 (20%)
        # narrative_completeness = 1.0 (20%)
        # evidence_coverage = 1.0 * 0.9 = 0.9 (20%)
        # consistency = 1.0 (20%)
        # overall = 0.20 + 0.20 + 0.20 + 0.18 + 0.20 = 0.98
        assert c.overall_confidence == 0.98
        assert c.evidence_coverage == 0.9
        assert c.consistency == 1.0

    def test_calculate_evidence_coverage_formula(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore(
            completeness=0.5,
            citation_coverage=0.0,
            trace_coverage=0.0,
            consistency=0.0,
        )
        c = cc.calculate(package, quality)
        # evidence_coverage = 0.5 * 0.9 = 0.45
        assert c.evidence_coverage == 0.45

    def test_calculate_overall_weighted_average(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore(
            completeness=0.8,
            citation_coverage=0.6,
            trace_coverage=0.4,
            consistency=0.2,
        )
        c = cc.calculate(package, quality)
        # citation_coverage = 0.6 (20%)
        # trace_completeness = 0.4 (20%)
        # narrative_completeness = 0.8 (20%)
        # evidence_coverage = 0.8 * 0.9 = 0.72 (20%)
        # consistency = 0.2 (20%)
        # overall = 0.6*0.2 + 0.4*0.2 + 0.8*0.2 + 0.72*0.2 + 0.2*0.2
        #         = 0.12 + 0.08 + 0.16 + 0.144 + 0.04 = 0.544
        assert c.overall_confidence == 0.544

    def test_calculate_all_fields_populated(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore(
            completeness=1.0,
            citation_coverage=0.8,
            trace_coverage=0.7,
            consistency=0.9,
        )
        c = cc.calculate(package, quality)
        assert c.overall_confidence >= 0.0
        assert c.narrative_quality == 1.0
        assert c.citation_accuracy == 0.8
        assert c.completeness == 0.7
        assert c.audience_coverage is not None
        assert c.evidence_coverage == 0.9
        assert c.consistency == 0.9
        assert c.metadata is not None
        assert "evidence_coverage" in c.metadata
        assert "consistency" in c.metadata

    def test_calculate_zero_values(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore()
        c = cc.calculate(package, quality)
        assert c.overall_confidence == 0.0
        assert c.evidence_coverage == 0.0
        assert c.consistency == 0.0

    def test_calculate_with_correlation_id(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore(
            completeness=0.9,
            citation_coverage=0.7,
            trace_coverage=0.6,
            consistency=0.8,
        )
        c = cc.calculate(package, quality, correlation_id="test-cid")
        assert isinstance(c, ExplanationConfidence)

    def test_calculate_clamps_negative_values(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore.model_construct(
            completeness=-0.5,
            citation_coverage=-0.2,
            trace_coverage=-0.1,
            consistency=-0.3,
        )
        c = cc.calculate(package, quality)
        assert c.narrative_quality == 0.0
        assert c.citation_accuracy == 0.0

    def test_calculate_clamps_over_one(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore.model_construct(
            completeness=1.5,
            citation_coverage=1.3,
            trace_coverage=1.2,
            consistency=1.1,
        )
        c = cc.calculate(package, quality)
        assert c.narrative_quality == 1.0
        assert c.citation_accuracy == 1.0


# =============================================================================
# 9. Enhanced Integration Hooks
# =============================================================================


class TestIntegrationHooksPhase35:
    def test_register_decision_review_hook(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(decision: Any, **kwargs: Any) -> None:
            calls.append("decision_review")

        h.register_decision_review(hook)
        h.run_decision_review(decision="test_decision")
        assert calls == ["decision_review"]

    def test_register_action_manager_hook(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(action: Any, **kwargs: Any) -> None:
            calls.append("action_manager")

        h.register_action_manager(hook)
        h.run_action_manager(action="test_action")
        assert calls == ["action_manager"]

    def test_register_action_engine_hook(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(action: Any, **kwargs: Any) -> None:
            calls.append("action_engine")

        h.register_action_engine(hook)
        h.run_action_engine(action="test_action")
        assert calls == ["action_engine"]

    def test_run_decision_review_passes_decision(self) -> None:
        h = IntegrationHooks()
        received: dict[str, Any] = {}

        def hook(decision: Any, **kwargs: Any) -> None:
            received["decision"] = decision

        h.register_decision_review(hook)
        h.run_decision_review(decision={"id": "d-1"}, user="admin")
        assert received.get("decision") == {"id": "d-1"}

    def test_run_action_manager_passes_action(self) -> None:
        h = IntegrationHooks()
        received: dict[str, Any] = {}

        def hook(action: Any, **kwargs: Any) -> None:
            received["action"] = action

        h.register_action_manager(hook)
        h.run_action_manager(action="maintenance")
        assert received.get("action") == "maintenance"

    def test_run_action_engine_passes_action(self) -> None:
        h = IntegrationHooks()
        received: dict[str, Any] = {}

        def hook(action: Any, **kwargs: Any) -> None:
            received["action"] = action

        h.register_action_engine(hook)
        h.run_action_engine(action="repair")
        assert received.get("action") == "repair"

    def test_exception_isolation_decision_review(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def failing_hook(decision: Any, **kwargs: Any) -> None:
            raise ValueError("Decision review failed")

        def working_hook(decision: Any, **kwargs: Any) -> None:
            calls.append("working")

        h.register_decision_review(failing_hook)
        h.register_decision_review(working_hook)
        h.run_decision_review(decision="test")
        assert calls == ["working"]

    def test_exception_isolation_action_manager(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def failing_hook(action: Any, **kwargs: Any) -> None:
            raise RuntimeError("Action manager failed")

        def working_hook(action: Any, **kwargs: Any) -> None:
            calls.append("working")

        h.register_action_manager(failing_hook)
        h.register_action_manager(working_hook)
        h.run_action_manager(action="test")
        assert calls == ["working"]

    def test_exception_isolation_action_engine(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def failing_hook(action: Any, **kwargs: Any) -> None:
            raise ValueError("Action engine failed")

        def working_hook(action: Any, **kwargs: Any) -> None:
            calls.append("working")

        h.register_action_engine(failing_hook)
        h.register_action_engine(working_hook)
        h.run_action_engine(action="test")
        assert calls == ["working"]

    def test_multiple_decision_review_hooks_all_run(self) -> None:
        h = IntegrationHooks()
        calls: list[int] = []

        def h1(decision: Any, **kwargs: Any) -> None:
            calls.append(1)

        def h2(decision: Any, **kwargs: Any) -> None:
            calls.append(2)

        h.register_decision_review(h1)
        h.register_decision_review(h2)
        h.run_decision_review(decision="test")
        assert calls == [1, 2]


# =============================================================================
# 10. Enhanced ExplainabilityMetricsCollector
# =============================================================================


class TestMetricsCollectorPhase35:
    def test_increment_reviews(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._reviews_total == 0
        mc.increment_reviews()
        assert mc._reviews_total == 1
        mc.increment_reviews(5)
        assert mc._reviews_total == 6

    def test_increment_versions(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._versions_total == 0
        mc.increment_versions()
        assert mc._versions_total == 1
        mc.increment_versions(3)
        assert mc._versions_total == 4

    def test_increment_readiness(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_readiness("READY")
        assert mc._readiness_by_status["READY"] == 1
        mc.increment_readiness("READY")
        assert mc._readiness_by_status["READY"] == 2
        mc.increment_readiness("REVIEW_REQUIRED")
        assert mc._readiness_by_status["REVIEW_REQUIRED"] == 1

    def test_increment_lineage_entries(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._lineage_entries_total == 0
        mc.increment_lineage_entries()
        assert mc._lineage_entries_total == 1
        mc.increment_lineage_entries(3)
        assert mc._lineage_entries_total == 4

    def test_increment_snapshots(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._snapshots_total == 0
        mc.increment_snapshots()
        assert mc._snapshots_total == 1
        mc.increment_snapshots(2)
        assert mc._snapshots_total == 3

    def test_record_confidence(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._confidence_scores == []
        mc.record_confidence(0.85)
        mc.record_confidence(0.75)
        assert mc._confidence_scores == [0.85, 0.75]

    def test_record_confidence_clamps_values(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.record_confidence(1.5)
        mc.record_confidence(-0.5)
        assert mc._confidence_scores == [1.0, 0.0]

    def test_increment_reviews_ignores_negative(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_reviews(-5)
        assert mc._reviews_total == 0

    def test_increment_versions_ignores_negative(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_versions(-3)
        assert mc._versions_total == 0

    def test_increment_lineage_entries_ignores_negative(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_lineage_entries(-2)
        assert mc._lineage_entries_total == 0

    def test_increment_snapshots_ignores_negative(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_snapshots(-1)
        assert mc._snapshots_total == 0

    def test_snapshot_includes_new_fields(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_explanations(2)
        mc.increment_narratives(5)
        mc.increment_citations(10)
        mc.record_audience("ENGINEER")
        mc.record_template("executive")
        mc.record_quality(0.8)
        mc.record_quality(0.9)
        mc.increment_reviews(3)
        mc.increment_versions(2)
        mc.increment_readiness("READY")
        mc.increment_readiness("READY")
        mc.increment_readiness("REVIEW_REQUIRED")
        mc.increment_lineage_entries(4)
        mc.increment_snapshots(1)
        mc.record_confidence(0.85)

        snap = mc.snapshot()
        assert isinstance(snap, ExplainabilityMetrics)
        assert snap.explanations_total == 2
        assert snap.narratives_total == 5
        assert snap.citations_total == 10
        assert snap.audience_distribution == {"ENGINEER": 1}
        assert snap.template_usage == {"executive": 1}
        assert snap.average_quality == pytest.approx(0.85, rel=1e-3)
        assert snap.reviews_total == 3
        assert snap.versions_total == 2
        assert snap.readiness_by_status == {"READY": 2, "REVIEW_REQUIRED": 1}
        assert snap.lineage_entries_total == 4
        assert snap.snapshots_total == 1
        assert snap.average_confidence == 0.85

    def test_snapshot_empty(self) -> None:
        mc = ExplainabilityMetricsCollector()
        snap = mc.snapshot()
        assert snap.explanations_total == 0
        assert snap.reviews_total == 0
        assert snap.versions_total == 0
        assert snap.lineage_entries_total == 0
        assert snap.snapshots_total == 0
        assert snap.average_quality == 0.0
        assert snap.average_confidence == 0.0

    def test_reset(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_reviews(5)
        mc.increment_versions(3)
        mc.reset()
        snap = mc.snapshot()
        assert snap.reviews_total == 0
        assert snap.versions_total == 0


# =============================================================================
# 11. Enhanced Coordinator Pipeline
# =============================================================================


class TestCoordinatorPipelinePhase35:
    def test_explain_includes_review(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        assert len(result.decisions) == 1
        decision = result.decisions[0]
        # Decision metadata should include review_results
        assert "review_results" in decision.metadata

    def test_explain_includes_versioning(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        decision = result.decisions[0]
        # Decision metadata should include version_id
        assert "version_id" in decision.metadata
        assert decision.metadata["version_id"] != ""

    def test_explain_includes_readiness(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        decision = result.decisions[0]
        assert "readiness_status" in decision.metadata
        # Readiness should be one of the valid statuses
        assert decision.metadata["readiness_status"] in ("READY", "REVIEW_REQUIRED", "INCOMPLETE")

    def test_explain_includes_lineage(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER],
            reasoning_result_id=uuid.uuid4(),
            evidence_result_id=uuid.uuid4(),
            recommendation_result_id=uuid.uuid4(),
        )
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        decision = result.decisions[0]
        assert "lineage_count" in decision.metadata
        assert decision.metadata["lineage_count"] >= 3

    def test_explain_includes_snapshot(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        decision = result.decisions[0]
        assert "snapshot_id" in decision.metadata
        assert decision.metadata["snapshot_id"] != ""

    def test_decision_readiness_field_populated(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        decision = result.decisions[0]
        assert decision.readiness != ""
        assert decision.readiness in ("READY", "REVIEW_REQUIRED", "INCOMPLETE")

    def test_metadata_includes_lineage_version_snapshot(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER],
            reasoning_result_id=uuid.uuid4(),
        )
        result = coord.explain(request)
        decision = result.decisions[0]
        md = decision.metadata
        assert "version_id" in md
        assert "lineage_count" in md
        assert "snapshot_id" in md

    def test_explain_metrics_collected(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE])
        coord.explain(request)
        metrics = coord.metrics()
        assert metrics.explanations_total >= 1
        assert metrics.narratives_total >= 2

    def test_explain_health_enhanced_fields(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        health = coord.health()
        assert health.narrative_status == "HEALTHY"
        assert health.citation_status == "HEALTHY"
        assert health.trace_status == "HEALTHY"
        assert health.formatter_status == "HEALTHY"
        assert health.template_status == "HEALTHY"
        assert health.policy_status == "HEALTHY"

    def test_explain_metrics_enhanced_fields(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        coord.explain(request)
        metrics = coord.metrics()
        assert metrics.average_quality >= 0.0
        assert metrics.audiences_total >= 1

    def test_explain_handles_error_gracefully(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        # A request with missing fields should still complete
        request = ExplanationRequest()
        result = coord.explain(request)
        assert result.status in (ExplanationStatus.COMPLETED, ExplanationStatus.FAILED)

    def test_explain_with_review_version_readiness_stages(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        assert result.confidence is not None
        assert result.package is not None
        assert len(result.narratives) >= 1
        assert len(result.citations) >= 1

    def test_metrics_after_explain_includes_new_fields(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        for _ in range(2):
            coord.explain(ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER]))
        metrics = coord.metrics()
        assert metrics.explanations_total == 2
        assert metrics.narratives_total >= 2


# =============================================================================
# 12. Pipeline Integration
# =============================================================================


class TestPipelineIntegration:
    def test_full_pipeline_from_request_to_snapshot(self) -> None:
        """Verify the full pipeline creates version, assesses readiness,
        records lineage, and creates a snapshot."""
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE],
            reasoning_result_id=uuid.uuid4(),
            evidence_result_id=uuid.uuid4(),
        )
        result = coord.explain(request, correlation_id="integration-test")
        assert result.status == ExplanationStatus.COMPLETED
        assert result.confidence is not None
        assert result.confidence.overall_confidence > 0.0
        assert len(result.decisions) == 1

        decision = result.decisions[0]
        # Version was created
        assert decision.metadata["version_id"] != ""
        # Readiness was assessed
        assert decision.metadata["readiness_status"] in ("READY", "REVIEW_REQUIRED", "INCOMPLETE")
        # Lineage was recorded (at least for reasoning + evidence)
        assert decision.metadata["lineage_count"] >= 2
        # Snapshot was created
        assert decision.metadata["snapshot_id"] != ""
        # Decision readiness field populated
        assert decision.readiness != ""

    def test_pipeline_with_recommendation_only(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER],
            recommendation_result_id=uuid.uuid4(),
        )
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        decision = result.decisions[0]
        assert decision.metadata["lineage_count"] >= 1

    def test_pipeline_with_all_source_ids(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER],
            reasoning_result_id=uuid.uuid4(),
            evidence_result_id=uuid.uuid4(),
            recommendation_result_id=uuid.uuid4(),
        )
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        decision = result.decisions[0]
        # All 3 source types recorded in lineage
        assert decision.metadata["lineage_count"] == 3

    def test_pipeline_multiple_executions_with_metrics(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        for i in range(3):
            coord.explain(ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER]))
        metrics = coord.metrics()
        assert metrics.explanations_total == 3

    def test_pipeline_maintains_version_history(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        rid = uuid.uuid4()
        request_1 = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER],
            reasoning_result_id=rid,
        )
        result_1 = coord.explain(request_1)
        v1_id = result_1.decisions[0].metadata["version_id"]

        request_2 = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER],
            reasoning_result_id=rid,
        )
        result_2 = coord.explain(request_2)
        v2_id = result_2.decisions[0].metadata["version_id"]

        # Each explain call gets its own result with different IDs
        assert v1_id != v2_id
        assert result_1.status == ExplanationStatus.COMPLETED
        assert result_2.status == ExplanationStatus.COMPLETED

    def test_pipeline_creates_valid_readiness_status(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        decision = result.decisions[0]
        assert decision.readiness in ("READY", "REVIEW_REQUIRED", "INCOMPLETE")

    def test_pipeline_creates_snapshot_with_data(self) -> None:
        """Verify the snapshot created by the pipeline contains expected fields."""
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE],
        )
        result = coord.explain(request)
        decision = result.decisions[0]
        snapshot_id = decision.metadata["snapshot_id"]
        assert snapshot_id != ""
        # Snapshot ID is a UUID string
        assert len(snapshot_id.split("-")) == 5


# =============================================================================
# 13. ExplanationJustification
# =============================================================================


class TestExplanationJustification:
    """Test ExplanationJustification recording and retrieval."""

    def test_record_narrative_justification(self) -> None:
        ej = ExplanationJustification()
        record = ej.record_narrative_justification(narrative_id="n-1", why="Best fit narrative")
        assert record["category"] == "narrative"
        assert record["target_id"] == "n-1"
        assert record["why"] == "Best fit narrative"
        assert "id" in record
        assert ej.count() == 1

    def test_record_citation_justification(self) -> None:
        ej = ExplanationJustification()
        record = ej.record_citation_justification(citation_id="c-1", why="Supports evidence traceability")
        assert record["category"] == "citation"
        assert record["target_id"] == "c-1"
        assert record["why"] == "Supports evidence traceability"

    def test_record_template_justification(self) -> None:
        ej = ExplanationJustification()
        record = ej.record_template_justification(template_type="executive", why="Best fit for audience")
        assert record["category"] == "template"
        assert record["target_id"] == "executive"

    def test_record_audience_justification(self) -> None:
        ej = ExplanationJustification()
        record = ej.record_audience_justification(audience="ENGINEER", why="Target audience specified")
        assert record["category"] == "audience"
        assert record["target_id"] == "ENGINEER"

    def test_record_policy_justification(self) -> None:
        ej = ExplanationJustification()
        record = ej.record_policy_justification(policy_type="STANDARD", why="Governance rules apply")
        assert record["category"] == "policy"
        assert record["target_id"] == "STANDARD"

    def test_get_justifications(self) -> None:
        ej = ExplanationJustification()
        ej.record_narrative_justification(narrative_id="n-1")
        ej.record_citation_justification(citation_id="c-1")
        justs = ej.get_justifications("")
        assert len(justs) == 2

    def test_get_by_category(self) -> None:
        ej = ExplanationJustification()
        ej.record_narrative_justification(narrative_id="n-1")
        ej.record_citation_justification(citation_id="c-1")
        ej.record_narrative_justification(narrative_id="n-2")
        narratives = ej.get_by_category("", "narrative")
        assert len(narratives) == 2
        citations = ej.get_by_category("", "citation")
        assert len(citations) == 1

    def test_get_all(self) -> None:
        ej = ExplanationJustification()
        assert len(ej.get_all()) == 0
        ej.record_narrative_justification(narrative_id="n-1")
        assert len(ej.get_all()) == 1
        ej.record_citation_justification(citation_id="c-1")
        assert len(ej.get_all()) == 2

    def test_clear(self) -> None:
        ej = ExplanationJustification()
        ej.record_narrative_justification(narrative_id="n-1")
        ej.clear()
        assert ej.count() == 0

    def test_count(self) -> None:
        ej = ExplanationJustification()
        assert ej.count() == 0
        ej.record_narrative_justification(narrative_id="n-1")
        assert ej.count() == 1
        ej.record_citation_justification(citation_id="c-1")
        assert ej.count() == 2


# =============================================================================
# 14. ExplanationCompliance
# =============================================================================


class TestExplanationCompliance:
    """Test ExplanationCompliance validation and assessment."""

    def test_validate_regulatory_fields_all_present(self) -> None:
        ec = ExplanationCompliance()
        pkg = type("Package", (), {"result_id": "r1", "package_id": "p1"})()
        violations = ec.validate_regulatory_fields(
            explanation_id="exp-1", package=pkg,
            narratives=["n1"], citations=["c1"],
        )
        assert violations == {}

    def test_validate_regulatory_fields_missing(self) -> None:
        ec = ExplanationCompliance()
        violations = ec.validate_regulatory_fields(
            explanation_id="exp-1",
            package=None, narratives=None, citations=None,
        )
        assert "result_id" in violations
        assert "package_id" in violations
        assert "narratives" in violations
        assert "citations" in violations

    def test_validate_mandatory_citations_all_types(self) -> None:
        ec = ExplanationCompliance()
        citations = [
            type("Cit", (), {"citation_type": "EVIDENCE"})(),
            type("Cit", (), {"citation_type": "REASONING"})(),
            type("Cit", (), {"citation_type": "RECOMMENDATION"})(),
        ]
        violations = ec.validate_mandatory_citations(citations)
        assert violations == []

    def test_validate_mandatory_citations_missing_types(self) -> None:
        ec = ExplanationCompliance()
        citations = [type("Cit", (), {"citation_type": "EVIDENCE"})()]
        violations = ec.validate_mandatory_citations(citations)
        assert len(violations) == 2
        assert any("REASONING" in v for v in violations)
        assert any("RECOMMENDATION" in v for v in violations)

    def test_validate_governance_rules_valid(self) -> None:
        ec = ExplanationCompliance()
        pkg = type("Pkg", (), {
            "reasoning_summary": "reasoning",
            "recommendation_summary": "rec",
            "overall_confidence": 0.8,
        })()
        violations = ec.validate_governance_rules(package=pkg)
        assert violations == []

    def test_validate_governance_rules_violations(self) -> None:
        ec = ExplanationCompliance()
        pkg = type("Pkg", (), {
            "reasoning_summary": "",
            "recommendation_summary": "",
            "overall_confidence": 0.0,
        })()
        violations = ec.validate_governance_rules(package=pkg)
        assert len(violations) == 3

    def test_validate_audit_requirements_valid(self) -> None:
        ec = ExplanationCompliance()
        traces = [
            type("T", (), {"stage_name": "narrative"})(),
            type("T", (), {"stage_name": "citation"})(),
            type("T", (), {"stage_name": "formatting"})(),
            type("T", (), {"stage_name": "timeline"})(),
        ]
        violations = ec.validate_audit_requirements(traces)
        assert violations == []

    def test_validate_audit_requirements_missing_stages(self) -> None:
        ec = ExplanationCompliance()
        traces = [type("T", (), {"stage_name": "narrative"})()]
        violations = ec.validate_audit_requirements(traces)
        assert len(violations) == 3

    def test_assess_compliance_fully_compliant(self) -> None:
        ec = ExplanationCompliance()
        pkg = type("Pkg", (), {
            "result_id": "r1", "package_id": "p1",
            "reasoning_summary": "reasoning",
            "recommendation_summary": "rec",
            "overall_confidence": 0.8,
        })()
        citations = [
            type("Cit", (), {"citation_type": "EVIDENCE"})(),
            type("Cit", (), {"citation_type": "REASONING"})(),
            type("Cit", (), {"citation_type": "RECOMMENDATION"})(),
        ]
        traces = [
            type("T", (), {"stage_name": "narrative"})(),
            type("T", (), {"stage_name": "citation"})(),
            type("T", (), {"stage_name": "formatting"})(),
            type("T", (), {"stage_name": "timeline"})(),
        ]
        result = ec.assess_compliance(
            explanation_id="exp-1", package=pkg,
            narratives=["n1"], citations=citations,
            traces=traces,
        )
        assert result["compliant"] is True
        assert result["status"] == "COMPLIANT"

    def test_assess_compliance_non_compliant(self) -> None:
        ec = ExplanationCompliance()
        result = ec.assess_compliance(
            explanation_id="exp-1", package=None,
            narratives=None, citations=None, traces=None,
        )
        assert result["compliant"] is False
        assert result["status"] == "NON_COMPLIANT"


# =============================================================================
# 15. ExplanationAuditPackage
# =============================================================================


class TestExplanationAuditPackage:
    """Test ExplanationAuditPackage creation and retrieval."""

    def _make_pkg(self) -> Any:
        return type("Pkg", (), {
            "package_id": uuid.uuid4(),
            "result_id": uuid.uuid4(),
            "reasoning_summary": "reasoning",
            "recommendation_summary": "rec",
            "overall_confidence": 0.8,
        })()

    def test_create_audit_package(self) -> None:
        ap = ExplanationAuditPackage()
        pkg = self._make_pkg()
        result = ap.create(package=pkg)
        assert "audit_id" in result
        assert result["explanation_id"] == str(pkg.package_id)
        assert result["version"] == ""
        assert "created_at" in result

    def test_create_with_all_fields(self) -> None:
        ap = ExplanationAuditPackage()
        pkg = self._make_pkg()
        cit = type("Cit", (), {
            "citation_id": "c1", "citation_type": "EVIDENCE",
            "source_id": "s1", "excerpt": "excerpt text",
        })()
        meta = type("Meta", (), {
            "title": "Test", "category": "analysis",
            "source": "src", "version": "1",
        })()
        tl = type("Tl", (), {"timeline_id": "tl1", "events": [{"e": 1}]})()
        result = ap.create(
            package=pkg, narratives=["n1"], citations=[cit],
            trace=[{"stage": "test"}], metadata=meta,
            version="v2", timeline=tl,
        )
        assert result["version"] == "v2"
        assert len(result["citations"]) == 1
        assert result["citations"][0]["citation_id"] == "c1"

    def test_get_audit_package_by_id(self) -> None:
        ap = ExplanationAuditPackage()
        pkg = self._make_pkg()
        created = ap.create(package=pkg)
        retrieved = ap.get(created["audit_id"])
        assert retrieved is not None
        assert retrieved["audit_id"] == created["audit_id"]

    def test_get_audit_package_not_found(self) -> None:
        ap = ExplanationAuditPackage()
        assert ap.get("nonexistent") is None

    def test_get_by_explanation(self) -> None:
        ap = ExplanationAuditPackage()
        pkg = self._make_pkg()
        ap.create(package=pkg)
        ap.create(package=pkg)
        packages = ap.get_by_explanation(str(pkg.package_id))
        assert len(packages) == 2

    def test_get_by_explanation_empty(self) -> None:
        ap = ExplanationAuditPackage()
        assert ap.get_by_explanation("nonexistent") == []

    def test_verify_returns_true(self) -> None:
        ap = ExplanationAuditPackage()
        pkg = self._make_pkg()
        created = ap.create(package=pkg)
        assert ap.verify(created["audit_id"]) is True

    def test_get_all(self) -> None:
        ap = ExplanationAuditPackage()
        assert len(ap.get_all()) == 0
        pkg = self._make_pkg()
        ap.create(package=pkg)
        assert len(ap.get_all()) == 1
        ap.create(package=pkg)
        assert len(ap.get_all()) == 2

    def test_clear(self) -> None:
        ap = ExplanationAuditPackage()
        pkg = self._make_pkg()
        ap.create(package=pkg)
        ap.clear()
        assert ap.count() == 0

    def test_count(self) -> None:
        ap = ExplanationAuditPackage()
        assert ap.count() == 0
        pkg = self._make_pkg()
        ap.create(package=pkg)
        assert ap.count() == 1


# =============================================================================
# 16. ExplanationExportProfiles
# =============================================================================


class TestExplanationExportProfiles:
    """Test ExplanationExportProfiles profile management and export."""

    def test_get_profile_executive(self) -> None:
        ep = ExplanationExportProfiles()
        profile = ep.get_profile("executive")
        assert profile is not None
        assert profile["profile_id"] == "executive"
        assert profile["format"] == "markdown"

    def test_get_profile_technical(self) -> None:
        ep = ExplanationExportProfiles()
        profile = ep.get_profile("technical")
        assert profile is not None
        assert profile["format"] == "markdown"
        assert profile["include_citations"] is True

    def test_get_profile_audit(self) -> None:
        ep = ExplanationExportProfiles()
        profile = ep.get_profile("audit")
        assert profile is not None
        assert profile["format"] == "pdf"

    def test_get_profile_json(self) -> None:
        ep = ExplanationExportProfiles()
        profile = ep.get_profile("json")
        assert profile is not None
        assert profile["format"] == "json"

    def test_get_profile_dashboard(self) -> None:
        ep = ExplanationExportProfiles()
        profile = ep.get_profile("dashboard")
        assert profile is not None
        assert profile["format"] == "json"
        assert profile["include_citations"] is False

    def test_get_profile_not_found(self) -> None:
        ep = ExplanationExportProfiles()
        assert ep.get_profile("nonexistent") is None

    def test_list_profiles(self) -> None:
        ep = ExplanationExportProfiles()
        profiles = ep.list_profiles()
        assert len(profiles) == 5

    def test_export_with_profile(self) -> None:
        ep = ExplanationExportProfiles()
        pkg = type("Pkg", (), {
            "package_id": uuid.uuid4(),
            "reasoning_summary": "reasoning",
            "recommendation_summary": "rec",
            "overall_confidence": 0.8,
        })()
        result = ep.export(
            package=pkg, narratives=["n1"], citations=["c1"],
            profile_type="executive",
        )
        assert result["profile_type"] == "executive"
        assert result["citation_count"] == 0  # executive excludes citations
        assert result["narrative_count"] == 1

    def test_register_profile(self) -> None:
        ep = ExplanationExportProfiles()
        ep.register_profile("custom", {
            "profile_id": "custom", "name": "Custom",
            "format": "html", "include_sections": ["summary"],
        })
        profile = ep.get_profile("custom")
        assert profile is not None
        assert profile["profile_id"] == "custom"
        assert ep.count() == 6

    def test_remove_profile(self) -> None:
        ep = ExplanationExportProfiles()
        ep.register_profile("custom", {
            "profile_id": "custom", "name": "Custom",
            "format": "html", "include_sections": ["summary"],
        })
        ep.remove_profile("custom")
        assert ep.get_profile("custom") is None

    def test_clear(self) -> None:
        ep = ExplanationExportProfiles()
        ep.register_profile("custom", {
            "profile_id": "custom", "name": "Custom",
            "format": "html", "include_sections": ["summary"],
        })
        ep.clear()
        assert ep.count() == 5

    def test_count(self) -> None:
        ep = ExplanationExportProfiles()
        assert ep.count() == 5  # 5 default profiles


# =============================================================================
# 17. QualityManager Enhanced (audience_suitability + policy_compliance)
# =============================================================================


class TestQualityManagerEnhanced:
    """Test ExplanationQualityManager Phase 3.5 enhancements."""

    def test_evaluate_audience_suitability_all_matched(self) -> None:
        qm = ExplanationQualityManager()
        narratives = [
            type("N", (), {"audience": "ENGINEER"})(),
            type("N", (), {"audience": "EXECUTIVE"})(),
        ]
        score = qm.evaluate_audience_suitability(narratives, ["ENGINEER", "EXECUTIVE"])
        assert score == 1.0

    def test_evaluate_audience_suitability_partial(self) -> None:
        qm = ExplanationQualityManager()
        narratives = [type("N", (), {"audience": "ENGINEER"})()]
        score = qm.evaluate_audience_suitability(narratives, ["ENGINEER", "EXECUTIVE"])
        assert score == 0.5

    def test_evaluate_audience_suitability_none(self) -> None:
        qm = ExplanationQualityManager()
        narratives = [type("N", (), {"audience": "MANAGER"})()]
        score = qm.evaluate_audience_suitability(narratives, ["ENGINEER", "EXECUTIVE"])
        assert score == 0.0

    def test_evaluate_policy_compliance_no_violations(self) -> None:
        qm = ExplanationQualityManager()
        pkg = type("Pkg", (), {"primary_narrative": "n1"})()
        score = qm.evaluate_policy_compliance(pkg, [])
        assert score == 1.0

    def test_evaluate_policy_compliance_with_violations(self) -> None:
        qm = ExplanationQualityManager()
        pkg = type("Pkg", (), {"primary_narrative": "n1"})()
        score = qm.evaluate_policy_compliance(pkg, ["violation1"])
        assert score == 0.5

    def test_evaluate_includes_new_dimensions(self) -> None:
        qm = ExplanationQualityManager()
        package = ExplanationPackage(
            result_id=uuid.uuid4(),
            primary_narrative=ExplanationNarrative(
                package_id=uuid.uuid4(), title="T", content="C",
                audience=ExplanationLayer.ENGINEER,
            ),
        )
        citations = [
            ExplanationCitation(
                narrative_id=uuid.uuid4(), citation_type=CitationType.EVIDENCE,
                source_id="s1", source_type="ev", excerpt="ex",
            ),
            ExplanationCitation(
                narrative_id=uuid.uuid4(), citation_type=CitationType.REASONING,
                source_id="s2", source_type="rs", excerpt="ex",
            ),
            ExplanationCitation(
                narrative_id=uuid.uuid4(), citation_type=CitationType.RECOMMENDATION,
                source_id="s3", source_type="rc", excerpt="ex",
            ),
        ]
        traces = [
            TraceRecord(stage_name="INITIALIZED"),
            TraceRecord(stage_name="COMPLETED"),
            TraceRecord(stage_name="QUALITY"),
        ]
        score = qm.evaluate(package, citations, traces)
        assert score.metadata.get("audience_suitability") == 0.7
        assert score.metadata.get("policy_compliance") == 1.0


# =============================================================================
# 18. AudienceValidator Enhanced (consistency + multi-audience)
# =============================================================================


class TestAudienceValidatorEnhanced:
    """Test AudienceValidator Phase 3.5 enhancements."""

    def test_validate_audience_consistency_consistent(self) -> None:
        av = AudienceValidator()
        narratives = [
            type("N", (), {"audience": "ENGINEER", "detail_level": "high"})(),
            type("N", (), {"audience": "ENGINEER", "detail_level": "high"})(),
        ]
        violations = av.validate_audience_consistency(narratives)
        assert violations == []

    def test_validate_audience_consistency_inconsistent(self) -> None:
        av = AudienceValidator()
        narratives = [
            type("N", (), {"audience": "ENGINEER", "detail_level": "high"})(),
            type("N", (), {"audience": "ENGINEER", "detail_level": "low"})(),
        ]
        violations = av.validate_audience_consistency(narratives)
        assert len(violations) == 1
        assert "Inconsistent detail levels" in violations[0]

    def test_validate_multi_audience_runs_all(self) -> None:
        av = AudienceValidator()
        narratives = [type("N", (), {"audience": "ENGINEER", "detail_level": "high"})()]
        result = av.validate_multi_audience(narratives, ["ENGINEER", "EXECUTIVE"])
        assert len(result) == 2
        assert "ENGINEER" in result
        assert "EXECUTIVE" in result

    def test_validate_multi_audience_empty_targets(self) -> None:
        av = AudienceValidator()
        result = av.validate_multi_audience([], [])
        assert result == {}


# =============================================================================
# 19. Trace Enhanced (new stage methods)
# =============================================================================


class TestTraceEnhanced:
    """Test ExplainabilityTrace Phase 3.5 stage methods."""

    def test_record_package_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_package_stage(explanation_id="exp-1", duration_ms=10.0)
        assert record.stage_name == "PACKAGE"
        assert record.explanation_id == "exp-1"
        assert record.duration_ms == 10.0
        assert t.count() == 1

    def test_record_audience_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_audience_stage(explanation_id="exp-1", duration_ms=5.0)
        assert record.stage_name == "AUDIENCE"
        assert record.duration_ms == 5.0

    def test_record_review_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_review_stage(
            explanation_id="exp-1", success=True,
            warnings=["minor issue"],
        )
        assert record.stage_name == "REVIEW"
        assert record.success is True
        assert "minor issue" in record.warnings

    def test_record_compliance_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_compliance_stage(
            explanation_id="exp-1", success=False,
            errors=["missing citation"],
        )
        assert record.stage_name == "COMPLIANCE"
        assert record.success is False
        assert "missing citation" in record.errors

    def test_new_stages_in_get_by_stage(self) -> None:
        t = ExplainabilityTrace()
        t.record_package_stage(explanation_id="exp-1")
        t.record_audience_stage(explanation_id="exp-1")
        t.record_review_stage(explanation_id="exp-1")
        t.record_compliance_stage(explanation_id="exp-1")
        assert len(t.get_by_stage("PACKAGE")) == 1
        assert len(t.get_by_stage("AUDIENCE")) == 1
        assert len(t.get_by_stage("REVIEW")) == 1
        assert len(t.get_by_stage("COMPLIANCE")) == 1


# =============================================================================
# 20. MetricsCollector Enhanced (Phase 3.5 new counters)
# =============================================================================


class TestMetricsCollectorEnhanced:
    """Test ExplainabilityMetricsCollector Phase 3.5 counters."""

    def test_increment_compliance(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._compliance_total == 0
        mc.increment_compliance()
        assert mc._compliance_total == 1
        mc.increment_compliance(5)
        assert mc._compliance_total == 6

    def test_increment_readiness_ready(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_readiness_ready()
        assert mc._readiness_by_status["READY"] == 1
        mc.increment_readiness_ready(3)
        assert mc._readiness_by_status["READY"] == 4

    def test_increment_readiness_review(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_readiness_review()
        assert mc._readiness_by_status["REVIEW_REQUIRED"] == 1

    def test_increment_readiness_incomplete(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_readiness_incomplete()
        assert mc._readiness_by_status["INCOMPLETE"] == 1

    def test_increment_readiness_non_compliant(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_readiness_non_compliant()
        assert mc._readiness_by_status["NON_COMPLIANT"] == 1

    def test_increment_audits(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._audits_total == 0
        mc.increment_audits()
        assert mc._audits_total == 1
        mc.increment_audits(3)
        assert mc._audits_total == 4

    def test_increment_exports(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._exports_total == 0
        mc.increment_exports()
        assert mc._exports_total == 1
        mc.increment_exports(5)
        assert mc._exports_total == 6

    def test_increment_justifications(self) -> None:
        mc = ExplainabilityMetricsCollector()
        assert mc._justifications_total == 0
        mc.increment_justifications()
        assert mc._justifications_total == 1
        mc.increment_justifications(7)
        assert mc._justifications_total == 8

    def test_snapshot_includes_new_fields(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_compliance(5)
        mc.increment_readiness_ready(2)
        mc.increment_readiness_review(1)
        mc.increment_readiness_incomplete(3)
        mc.increment_readiness_non_compliant(1)
        mc.increment_audits(4)
        mc.increment_exports(6)
        mc.increment_justifications(7)
        snap = mc.snapshot()
        assert snap.compliance_total == 5
        assert snap.readiness_ready == 2
        assert snap.readiness_review == 1
        assert snap.readiness_incomplete == 3
        assert snap.readiness_non_compliant == 1
        assert snap.audits_total == 4
        assert snap.exports_total == 6
        assert snap.justifications_total == 7


# =============================================================================
# 21. ExplainabilityMetrics Enhanced (Phase 3.5 new fields)
# =============================================================================


class TestExplainabilityMetricsEnhanced:
    """Test ExplainabilityMetrics Phase 3.5 new fields."""

    def test_defaults_new_fields(self) -> None:
        m = ExplainabilityMetrics()
        assert m.compliance_total == 0
        assert m.readiness_ready == 0
        assert m.readiness_review == 0
        assert m.readiness_incomplete == 0
        assert m.readiness_non_compliant == 0
        assert m.audits_total == 0
        assert m.exports_total == 0
        assert m.justifications_total == 0

    def test_with_values(self) -> None:
        m = ExplainabilityMetrics(
            compliance_total=10,
            readiness_ready=5,
            readiness_review=3,
            readiness_incomplete=2,
            readiness_non_compliant=1,
            audits_total=8,
            exports_total=12,
            justifications_total=15,
        )
        assert m.compliance_total == 10
        assert m.readiness_ready == 5
        assert m.readiness_review == 3
        assert m.readiness_incomplete == 2
        assert m.readiness_non_compliant == 1
        assert m.audits_total == 8
        assert m.exports_total == 12
        assert m.justifications_total == 15

    def test_non_negative_constraints(self) -> None:
        schema = ExplainabilityMetrics.model_json_schema()
        properties = schema.get("properties", {})
        for field_name in (
            "compliance_total", "readiness_ready", "readiness_review",
            "readiness_incomplete", "readiness_non_compliant",
            "audits_total", "exports_total", "justifications_total",
        ):
            prop = properties.get(field_name, {})
            assert prop.get("minimum") == 0, f"{field_name} should have minimum=0"


# =============================================================================
# 22. Readiness Enhanced (compliance_status support)
# =============================================================================


class TestReadinessEnhanced:
    """Test ExplanationReadiness Phase 3.5 compliance_status support."""

    def test_assess_non_compliant(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.9, quality_score=0.9,
            compliance_status="NON_COMPLIANT",
        )
        assert status == "NON_COMPLIANT"

    def test_assess_still_ready(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.7, quality_score=0.7,
            compliance_status="COMPLIANT",
        )
        assert status == "READY"

    def test_assess_still_review_required(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.5, quality_score=0.5,
            compliance_status="COMPLIANT",
        )
        assert status == "REVIEW_REQUIRED"

    def test_assess_still_incomplete(self) -> None:
        er = ExplanationReadiness()
        status = er.assess(
            confidence_score=0.4, quality_score=0.4,
            compliance_status="COMPLIANT",
        )
        assert status == "INCOMPLETE"


# =============================================================================
# 23. Lineage Enhanced (record_review)
# =============================================================================


class TestLineageEnhanced:
    """Test ExplanationLineage Phase 3.5 record_review method."""

    def test_record_review(self) -> None:
        ll = ExplanationLineage()
        entry = ll.record_review(review_id="rv-1", explanation_id="exp-1")
        assert entry["source_type"] == "review"
        assert entry["source_id"] == "rv-1"
        assert entry["explanation_id"] == "exp-1"
        assert "entry_id" in entry


# =============================================================================
# 24. Snapshot Enhanced (confidence, quality, compliance, version args)
# =============================================================================


class TestSnapshotEnhanced:
    """Test ExplanationSnapshot Phase 3.5 new fields."""

    def _make_package(self) -> ExplanationPackage:
        return ExplanationPackage(result_id=uuid.uuid4())

    def _make_timeline(self) -> ExplanationTimeline:
        return ExplanationTimeline(events=[{"event": "e1"}])

    def test_create_with_confidence_quality_compliance_version(self) -> None:
        ss = ExplanationSnapshot()
        pkg = self._make_package()
        timeline = self._make_timeline()
        snapshot = ss.create(
            package=pkg, narratives=[], citations=[], trace=[], timeline=timeline,
            confidence=0.85, quality={"overall": 0.8},
            compliance={"status": "COMPLIANT"}, version="v2",
        )
        assert snapshot["confidence"] == 0.85
        assert snapshot["quality"] == {"overall": 0.8}
        assert snapshot["compliance"] == {"status": "COMPLIANT"}
        assert snapshot["version"] == "v2"

    def test_create_without_new_fields(self) -> None:
        ss = ExplanationSnapshot()
        pkg = self._make_package()
        timeline = self._make_timeline()
        snapshot = ss.create(
            package=pkg, narratives=[], citations=[], trace=[], timeline=timeline,
        )
        assert snapshot["confidence"] is None
        assert snapshot["quality"] is None
        assert snapshot["compliance"] is None
        assert snapshot["version"] == ""


# =============================================================================
# 25. Coordinator Pipeline New Stages (justification, compliance, audit, export)
# =============================================================================


class TestCoordinatorPipelineNewStages:
    """Test that the coordinator pipeline includes Phase 3.5 stages."""

    def test_explain_includes_justification(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        # Justification runs without error — coordinator has _justification

    def test_explain_includes_compliance(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        md = result.decisions[0].metadata
        assert "compliance_status" in md

    def test_explain_includes_audit(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        md = result.decisions[0].metadata
        assert "audit_id" in md
        assert md["audit_id"] != ""

    def test_explain_includes_export(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        md = result.decisions[0].metadata
        assert "export_count" in md

    def test_decision_has_compliance_status(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        md = result.decisions[0].metadata
        assert md["compliance_status"] in ("COMPLIANT", "NON_COMPLIANT")

    def test_decision_has_audit_id(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        md = result.decisions[0].metadata
        assert md["audit_id"] != ""
        assert isinstance(md["audit_id"], str)

    def test_decision_has_export_count(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER])
        result = coord.explain(request)
        md = result.decisions[0].metadata
        assert md["export_count"] >= 0
        assert isinstance(md["export_count"], int)

    def test_24_stage_pipeline(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE],
            reasoning_result_id=uuid.uuid4(),
            evidence_result_id=uuid.uuid4(),
            recommendation_result_id=uuid.uuid4(),
        )
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        md = result.decisions[0].metadata
        assert "compliance_status" in md
        assert "audit_id" in md
        assert "export_count" in md
        assert "version_id" in md
        assert "readiness_status" in md
        assert "lineage_count" in md
        assert "snapshot_id" in md
