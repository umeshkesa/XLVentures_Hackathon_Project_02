"""Phase 1 tests for the Explainability Engine (Architecture, Contracts & Models).

Tests all Phase 1 components: enums, models, DTOs, events, exceptions,
interfaces, and their relationships.
"""

from __future__ import annotations

import sys
import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

sys.path.insert(0, 'backend/src')

from adip.explainability import (
    AudienceFormatter,
    CitationBuilder,
    CitationException,
    CitationType,
    ExplainabilityCoordinator,
    ExplainabilityException,
    ExplainabilityManager,
    ExplainabilityService,
    ExplanationAudience,
    ExplanationCitation,
    ExplanationCompleted,
    ExplanationConfidence,
    ExplanationContext,
    ExplanationDecision,
    ExplanationDomain,
    ExplanationEvent,
    ExplanationGenerated,
    ExplanationHealth,
    ExplanationLayer,
    ExplanationLayerModel,
    ExplanationMetadata,
    ExplanationMetrics,
    ExplanationNarrative,
    ExplanationPackage,
    ExplanationPackageDTO,
    ExplanationPolicy,
    ExplanationRequest,
    ExplanationRequestDTO,
    ExplanationRequested,
    ExplanationResponseDTO,
    ExplanationResult,
    ExplanationSession,
    ExplanationStatus,
    ExplanationTrace,
    ExplanationValidated,
    ExplanationValidator,
    NarrativeBuilder,
    NarrativeException,
    NarrativeType,
    TraceBuilder,
    TraceException,
)

# ═══════════════════════════════════════════════════════════════════════
# 1. ExplanationDomain Enum
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationDomain:
    def test_values(self) -> None:
        assert ExplanationDomain.SYSTEM.value == "SYSTEM"
        assert ExplanationDomain.ENERGY.value == "ENERGY"
        assert ExplanationDomain.OPERATIONS.value == "OPERATIONS"
        assert ExplanationDomain.MAINTENANCE.value == "MAINTENANCE"
        assert ExplanationDomain.SAFETY.value == "SAFETY"
        assert ExplanationDomain.COMPLIANCE.value == "COMPLIANCE"
        assert ExplanationDomain.CUSTOMER.value == "CUSTOMER"
        assert ExplanationDomain.HEALTHCARE.value == "HEALTHCARE"
        assert ExplanationDomain.MANUFACTURING.value == "MANUFACTURING"

    def test_unique_values(self) -> None:
        values = [e.value for e in ExplanationDomain]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ExplanationDomain) == 9


# ═══════════════════════════════════════════════════════════════════════
# 2. ExplanationLayer Enum
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationLayerEnum:
    def test_values(self) -> None:
        assert ExplanationLayer.EXECUTIVE.value == "EXECUTIVE"
        assert ExplanationLayer.MANAGER.value == "MANAGER"
        assert ExplanationLayer.ENGINEER.value == "ENGINEER"
        assert ExplanationLayer.OPERATOR.value == "OPERATOR"
        assert ExplanationLayer.TECHNICIAN.value == "TECHNICIAN"
        assert ExplanationLayer.AUDITOR.value == "AUDITOR"
        assert ExplanationLayer.DEVELOPER.value == "DEVELOPER"

    def test_unique_values(self) -> None:
        values = [e.value for e in ExplanationLayer]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ExplanationLayer) == 7


# ═══════════════════════════════════════════════════════════════════════
# 3. ExplanationStatus Enum
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationStatus:
    def test_values(self) -> None:
        assert ExplanationStatus.INITIALIZED.value == "INITIALIZED"
        assert ExplanationStatus.COLLECTING.value == "COLLECTING"
        assert ExplanationStatus.BUILDING.value == "BUILDING"
        assert ExplanationStatus.VALIDATED.value == "VALIDATED"
        assert ExplanationStatus.COMPLETED.value == "COMPLETED"
        assert ExplanationStatus.FAILED.value == "FAILED"

    def test_unique_values(self) -> None:
        values = [e.value for e in ExplanationStatus]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ExplanationStatus) == 6


# ═══════════════════════════════════════════════════════════════════════
# 4. NarrativeType Enum
# ═══════════════════════════════════════════════════════════════════════


class TestNarrativeType:
    def test_values(self) -> None:
        assert NarrativeType.SUMMARY.value == "SUMMARY"
        assert NarrativeType.DETAILED.value == "DETAILED"
        assert NarrativeType.TECHNICAL.value == "TECHNICAL"
        assert NarrativeType.BUSINESS.value == "BUSINESS"
        assert NarrativeType.AUDIT.value == "AUDIT"

    def test_unique_values(self) -> None:
        values = [e.value for e in NarrativeType]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(NarrativeType) == 5


# ═══════════════════════════════════════════════════════════════════════
# 5. CitationType Enum
# ═══════════════════════════════════════════════════════════════════════


class TestCitationType:
    def test_values(self) -> None:
        assert CitationType.EVIDENCE.value == "EVIDENCE"
        assert CitationType.REASONING.value == "REASONING"
        assert CitationType.RECOMMENDATION.value == "RECOMMENDATION"
        assert CitationType.POLICY.value == "POLICY"
        assert CitationType.METRIC.value == "METRIC"

    def test_unique_values(self) -> None:
        values = [e.value for e in CitationType]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(CitationType) == 5


# ═══════════════════════════════════════════════════════════════════════
# 6. ExplanationRequest Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationRequest:
    def test_default_request(self) -> None:
        req = ExplanationRequest()
        assert req.request_id is not None
        assert req.reasoning_result_id is not None
        assert req.evidence_result_id is not None
        assert req.recommendation_result_id is not None
        assert req.target_audiences == []
        assert req.domain == ExplanationDomain.SYSTEM
        assert req.context == {}
        assert req.metadata == {}

    def test_request_with_values(self) -> None:
        rid = uuid.uuid4()
        audiences = [ExplanationLayer.EXECUTIVE, ExplanationLayer.ENGINEER]
        req = ExplanationRequest(
            reasoning_result_id=rid,
            domain=ExplanationDomain.ENERGY,
            target_audiences=audiences,
            context={"asset_id": "asset-1"},
            metadata={"source": "test"},
        )
        assert req.reasoning_result_id == rid
        assert req.domain == ExplanationDomain.ENERGY
        assert len(req.target_audiences) == 2
        assert req.context["asset_id"] == "asset-1"

    def test_request_unique_ids(self) -> None:
        r1 = ExplanationRequest()
        r2 = ExplanationRequest()
        assert r1.request_id != r2.request_id
        assert r1.reasoning_result_id != r2.reasoning_result_id


# ═══════════════════════════════════════════════════════════════════════
# 7. ExplanationResult Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationResult:
    def test_default_result(self) -> None:
        rid = uuid.uuid4()
        result = ExplanationResult(request_id=rid)
        assert result.request_id == rid
        assert result.package is None
        assert result.narratives == []
        assert result.citations == []
        assert result.decisions == []
        assert result.status == ExplanationStatus.INITIALIZED
        assert result.confidence is None

    def test_result_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationResult()

    def test_result_with_package(self) -> None:
        rid = uuid.uuid4()
        pkg = ExplanationPackage(result_id=rid)
        result = ExplanationResult(
            request_id=rid,
            package=pkg,
            status=ExplanationStatus.COMPLETED,
        )
        assert result.package is not None
        assert result.package.result_id == rid
        assert result.status == ExplanationStatus.COMPLETED

    def test_result_roundtrip(self) -> None:
        rid = uuid.uuid4()
        result = ExplanationResult(
            request_id=rid,
            status=ExplanationStatus.COMPLETED,
        )
        data = result.model_dump()
        restored = ExplanationResult.model_validate(data)
        assert restored.status == ExplanationStatus.COMPLETED
        assert restored.request_id == rid


# ═══════════════════════════════════════════════════════════════════════
# 8. ExplanationPackage Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationPackage:
    def test_default_package(self) -> None:
        rid = uuid.uuid4()
        pkg = ExplanationPackage(result_id=rid)
        assert pkg.result_id == rid
        assert pkg.primary_narrative is None
        assert pkg.supporting_narratives == []
        assert pkg.evidence_citations == []
        assert pkg.reasoning_summary == ""
        assert pkg.recommendation_summary == ""
        assert pkg.overall_confidence == 0.0

    def test_package_requires_result_id(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationPackage()

    def test_package_with_narrative(self) -> None:
        rid = uuid.uuid4()
        narrative = ExplanationNarrative(
            package_id=rid,
            title="Explanation Title",
            content="Detailed explanation content",
        )
        pkg = ExplanationPackage(
            result_id=rid,
            primary_narrative=narrative,
            overall_confidence=0.85,
        )
        assert pkg.primary_narrative is not None
        assert pkg.primary_narrative.title == "Explanation Title"
        assert pkg.overall_confidence == 0.85

    def test_package_with_citations(self) -> None:
        rid = uuid.uuid4()
        nid = uuid.uuid4()
        citation = ExplanationCitation(
            narrative_id=nid,
            citation_type=CitationType.EVIDENCE,
        )
        pkg = ExplanationPackage(
            result_id=rid,
            evidence_citations=[citation],
        )
        assert len(pkg.evidence_citations) == 1
        assert pkg.evidence_citations[0].citation_type == CitationType.EVIDENCE


# ═══════════════════════════════════════════════════════════════════════
# 9. ExplanationNarrative Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationNarrative:
    def test_default_narrative(self) -> None:
        pid = uuid.uuid4()
        n = ExplanationNarrative(package_id=pid)
        assert n.package_id == pid
        assert n.narrative_type == NarrativeType.SUMMARY
        assert n.audience == ExplanationLayer.ENGINEER
        assert n.title == ""
        assert n.content == ""
        assert n.summary == ""

    def test_narrative_with_values(self) -> None:
        pid = uuid.uuid4()
        n = ExplanationNarrative(
            package_id=pid,
            narrative_type=NarrativeType.DETAILED,
            audience=ExplanationLayer.EXECUTIVE,
            title="Executive Summary",
            content="Detailed content for executives",
            summary="Brief overview",
        )
        assert n.narrative_type == NarrativeType.DETAILED
        assert n.audience == ExplanationLayer.EXECUTIVE
        assert n.title == "Executive Summary"
        assert n.content == "Detailed content for executives"
        assert n.summary == "Brief overview"

    def test_narrative_type_enum(self) -> None:
        pid = uuid.uuid4()
        n = ExplanationNarrative(
            package_id=pid,
            narrative_type=NarrativeType.TECHNICAL,
        )
        assert n.narrative_type == NarrativeType.TECHNICAL


# ═══════════════════════════════════════════════════════════════════════
# 10. ExplanationContext Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationContext:
    def test_default_context(self) -> None:
        c = ExplanationContext()
        assert c.context_id is not None
        assert c.reasoning_context == {}
        assert c.evidence_context == {}
        assert c.recommendation_context == {}
        assert c.asset_id == ""
        assert c.machine_id == ""
        assert c.facility_id == ""
        assert c.workflow_id == ""

    def test_context_with_values(self) -> None:
        c = ExplanationContext(
            reasoning_context={"score": 0.85},
            evidence_context={"source": "sensor-1"},
            asset_id="asset-1",
            machine_id="machine-1",
            facility_id="facility-1",
            workflow_id="wf-1",
        )
        assert c.reasoning_context["score"] == 0.85
        assert c.evidence_context["source"] == "sensor-1"
        assert c.asset_id == "asset-1"
        assert c.machine_id == "machine-1"
        assert c.facility_id == "facility-1"
        assert c.workflow_id == "wf-1"

    def test_context_with_ids(self) -> None:
        c1 = ExplanationContext()
        c2 = ExplanationContext()
        assert c1.context_id != c2.context_id


# ═══════════════════════════════════════════════════════════════════════
# 11. ExplanationAudience Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationAudience:
    def test_default_audience(self) -> None:
        layer = ExplanationLayer.ENGINEER
        a = ExplanationAudience(layer=layer)
        assert a.layer == layer
        assert a.name == ""
        assert a.description == ""
        assert a.required_detail_level == ""
        assert a.technical_depth == 0.5

    def test_audience_with_values(self) -> None:
        a = ExplanationAudience(
            layer=ExplanationLayer.EXECUTIVE,
            name="C-Suite",
            description="Executive leadership team",
            required_detail_level="high",
            technical_depth=0.2,
        )
        assert a.layer == ExplanationLayer.EXECUTIVE
        assert a.name == "C-Suite"
        assert a.technical_depth == 0.2

    def test_audience_technical_depth_bounds(self) -> None:
        layer = ExplanationLayer.ENGINEER
        with pytest.raises(ValidationError):
            ExplanationAudience(layer=layer, technical_depth=-0.1)
        with pytest.raises(ValidationError):
            ExplanationAudience(layer=layer, technical_depth=1.1)


# ═══════════════════════════════════════════════════════════════════════
# 12. ExplanationPolicy Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationPolicy:
    def test_default_policy(self) -> None:
        p = ExplanationPolicy()
        assert p.policy_id is not None
        assert p.name == ""
        assert p.description == ""
        assert p.allowed_layers == []
        assert p.max_narratives == 10
        assert p.require_citations is True
        assert p.is_active is True

    def test_policy_with_values(self) -> None:
        layers = [ExplanationLayer.EXECUTIVE, ExplanationLayer.AUDITOR]
        p = ExplanationPolicy(
            name="Compliance Policy",
            description="Policy for compliance-related explanations",
            allowed_layers=layers,
            max_narratives=5,
            require_citations=True,
            is_active=True,
        )
        assert p.name == "Compliance Policy"
        assert len(p.allowed_layers) == 2
        assert p.max_narratives == 5
        assert p.require_citations is True

    def test_policy_max_narratives_positive(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationPolicy(max_narratives=0)
        with pytest.raises(ValidationError):
            ExplanationPolicy(max_narratives=-1)


# ═══════════════════════════════════════════════════════════════════════
# 13. ExplanationTrace Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationTrace:
    def test_default_trace(self) -> None:
        t = ExplanationTrace()
        assert t.trace_id is not None
        assert t.stage_name == ""
        assert t.operation == ""
        assert t.explanation_id == ""
        assert t.correlation_id == ""
        assert t.duration_ms == 0.0
        assert t.success is False
        assert t.warnings == []
        assert t.errors == []

    def test_trace_with_values(self) -> None:
        now = datetime.now(UTC)
        t = ExplanationTrace(
            stage_name="NARRATIVE_BUILD",
            operation="build_narrative",
            explanation_id="exp-1",
            correlation_id="corr-1",
            started_at=now,
            completed_at=now,
            duration_ms=42.5,
            success=True,
            warnings=["Missing optional context"],
            errors=[],
        )
        assert t.stage_name == "NARRATIVE_BUILD"
        assert t.duration_ms == 42.5
        assert t.success is True
        assert len(t.warnings) == 1

    def test_trace_duration_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationTrace(duration_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# 14. ExplanationCitation Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationCitation:
    def test_default_citation(self) -> None:
        nid = uuid.uuid4()
        c = ExplanationCitation(
            narrative_id=nid,
            citation_type=CitationType.EVIDENCE,
        )
        assert c.narrative_id == nid
        assert c.citation_type == CitationType.EVIDENCE
        assert c.source_id == ""
        assert c.source_type == ""
        assert c.excerpt == ""
        assert c.relevance_score == 0.0

    def test_citation_with_values(self) -> None:
        nid = uuid.uuid4()
        c = ExplanationCitation(
            narrative_id=nid,
            citation_type=CitationType.REASONING,
            source_id="src-1",
            source_type="reasoning",
            excerpt="Reasoning step 3 shows confidence of 0.85",
            relevance_score=0.92,
        )
        assert c.citation_type == CitationType.REASONING
        assert c.source_id == "src-1"
        assert c.excerpt == "Reasoning step 3 shows confidence of 0.85"
        assert c.relevance_score == 0.92

    def test_citation_relevance_bounds(self) -> None:
        nid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ExplanationCitation(
                narrative_id=nid,
                citation_type=CitationType.EVIDENCE,
                relevance_score=-0.1,
            )
        with pytest.raises(ValidationError):
            ExplanationCitation(
                narrative_id=nid,
                citation_type=CitationType.EVIDENCE,
                relevance_score=1.1,
            )


# ═══════════════════════════════════════════════════════════════════════
# 15. ExplanationLayer Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationLayerModel:
    def test_default_layer(self) -> None:
        layer_type = ExplanationLayer.ENGINEER
        layer = ExplanationLayerModel(layer_type=layer_type)
        assert layer.layer_type == layer_type
        assert layer.name == ""
        assert layer.description == ""
        assert layer.format_preferences == {}

    def test_layer_with_values(self) -> None:
        layer = ExplanationLayerModel(
            layer_type=ExplanationLayer.EXECUTIVE,
            name="Executive",
            description="For C-level executives",
            format_preferences={"verbosity": "high", "format": "dashboard"},
        )
        assert layer.layer_type == ExplanationLayer.EXECUTIVE
        assert layer.name == "Executive"
        assert layer.format_preferences["verbosity"] == "high"

    def test_layer_type_enum(self) -> None:
        layer = ExplanationLayerModel(layer_type=ExplanationLayer.AUDITOR)
        assert layer.layer_type == ExplanationLayer.AUDITOR


# ═══════════════════════════════════════════════════════════════════════
# 16. ExplanationConfidence Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationConfidence:
    def test_default_confidence(self) -> None:
        c = ExplanationConfidence()
        assert c.overall_confidence == 0.0
        assert c.narrative_quality == 0.0
        assert c.citation_accuracy == 0.0
        assert c.completeness == 0.0
        assert c.audience_coverage == 0.0

    def test_confidence_with_values(self) -> None:
        c = ExplanationConfidence(
            overall_confidence=0.85,
            narrative_quality=0.9,
            citation_accuracy=0.75,
            completeness=0.8,
            audience_coverage=0.7,
        )
        assert c.overall_confidence == 0.85
        assert c.narrative_quality == 0.9
        assert c.citation_accuracy == 0.75
        assert c.completeness == 0.8
        assert c.audience_coverage == 0.7

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationConfidence(overall_confidence=-0.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(overall_confidence=1.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(narrative_quality=-0.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(narrative_quality=1.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(citation_accuracy=-0.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(citation_accuracy=1.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(completeness=-0.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(completeness=1.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(audience_coverage=-0.1)
        with pytest.raises(ValidationError):
            ExplanationConfidence(audience_coverage=1.1)


# ═══════════════════════════════════════════════════════════════════════
# 17. ExplanationMetadata Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationMetadata:
    def test_default_metadata(self) -> None:
        m = ExplanationMetadata()
        assert m.title == ""
        assert m.description == ""
        assert m.tags == []
        assert m.category == ""
        assert m.source == ""
        assert m.version == ""

    def test_metadata_with_values(self) -> None:
        m = ExplanationMetadata(
            title="Safety Analysis Explanation",
            description="Explanation of safety analysis results",
            tags=["safety", "analysis", "compliance"],
            category="analysis",
            source="safety-engine",
            version="1.0.0",
        )
        assert m.title == "Safety Analysis Explanation"
        assert len(m.tags) == 3
        assert m.source == "safety-engine"
        assert m.version == "1.0.0"


# ═══════════════════════════════════════════════════════════════════════
# 18. ExplanationHealth Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationHealth:
    def test_default_health(self) -> None:
        h = ExplanationHealth()
        assert h.overall_status == ""
        assert h.coordinator_status == ""
        assert h.narrative_builder_status == ""
        assert h.citation_builder_status == ""
        assert h.audience_formatter_status == ""
        assert h.validator_status == ""
        assert h.explanation_count == 0
        assert h.error_count == 0
        assert h.average_latency_ms == 0.0

    def test_health_with_values(self) -> None:
        h = ExplanationHealth(
            overall_status="HEALTHY",
            coordinator_status="HEALTHY",
            narrative_builder_status="HEALTHY",
            citation_builder_status="DEGRADED",
            audience_formatter_status="HEALTHY",
            validator_status="HEALTHY",
            explanation_count=100,
            error_count=2,
            average_latency_ms=45.5,
        )
        assert h.overall_status == "HEALTHY"
        assert h.citation_builder_status == "DEGRADED"
        assert h.explanation_count == 100
        assert h.error_count == 2
        assert h.average_latency_ms == 45.5

    def test_health_counts_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationHealth(explanation_count=-1)
        with pytest.raises(ValidationError):
            ExplanationHealth(error_count=-1)
        with pytest.raises(ValidationError):
            ExplanationHealth(average_latency_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# 19. ExplanationMetrics Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationMetrics:
    def test_default_metrics(self) -> None:
        m = ExplanationMetrics()
        assert m.explanations_total == 0
        assert m.narratives_total == 0
        assert m.citations_total == 0
        assert m.packages_total == 0
        assert m.validated_total == 0
        assert m.failed_total == 0
        assert m.explanations_per_domain == {}
        assert m.explanations_per_layer == {}
        assert m.average_confidence == 0.0
        assert m.average_completeness == 0.0

    def test_metrics_with_values(self) -> None:
        m = ExplanationMetrics(
            explanations_total=50,
            narratives_total=120,
            citations_total=300,
            packages_total=45,
            validated_total=40,
            failed_total=3,
            explanations_per_domain={"ENERGY": 20, "SAFETY": 30},
            explanations_per_layer={"EXECUTIVE": 25, "ENGINEER": 25},
            average_confidence=0.82,
            average_completeness=0.78,
        )
        assert m.explanations_total == 50
        assert m.narratives_total == 120
        assert m.packages_total == 45
        assert m.explanations_per_domain["ENERGY"] == 20
        assert m.average_confidence == 0.82
        assert m.average_completeness == 0.78

    def test_metrics_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationMetrics(explanations_total=-1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(narratives_total=-1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(citations_total=-1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(packages_total=-1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(validated_total=-1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(failed_total=-1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(average_confidence=-0.1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(average_confidence=1.1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(average_completeness=-0.1)
        with pytest.raises(ValidationError):
            ExplanationMetrics(average_completeness=1.1)


# ═══════════════════════════════════════════════════════════════════════
# 20. ExplanationSession Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationSession:
    def test_default_session(self) -> None:
        rid = uuid.uuid4()
        s = ExplanationSession(request_id=rid)
        assert s.request_id == rid
        assert s.domain == ExplanationDomain.SYSTEM
        assert s.target_layers == []
        assert s.status == ExplanationStatus.INITIALIZED
        assert s.completed_at is None
        assert s.statistics == {}

    def test_session_with_values(self) -> None:
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        layers = [ExplanationLayer.EXECUTIVE, ExplanationLayer.ENGINEER]
        s = ExplanationSession(
            request_id=rid,
            domain=ExplanationDomain.ENERGY,
            target_layers=layers,
            status=ExplanationStatus.COMPLETED,
            completed_at=now,
            statistics={"duration_ms": 150, "narratives_count": 3},
        )
        assert s.domain == ExplanationDomain.ENERGY
        assert len(s.target_layers) == 2
        assert s.status == ExplanationStatus.COMPLETED
        assert s.completed_at == now
        assert s.statistics["duration_ms"] == 150

    def test_session_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationSession()


# ═══════════════════════════════════════════════════════════════════════
# 21. ExplanationDecision Model
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationDecision:
    def test_default_decision(self) -> None:
        rid = uuid.uuid4()
        d = ExplanationDecision(result_id=rid)
        assert d.result_id == rid
        assert d.conclusion == ""
        assert d.reasoning_summary == ""
        assert d.recommendation_summary == ""
        assert d.selected_narratives == []
        assert d.rejected_narratives == []
        assert d.confidence == 0.0
        assert d.audience == ExplanationLayer.ENGINEER

    def test_decision_with_values(self) -> None:
        rid = uuid.uuid4()
        d = ExplanationDecision(
            result_id=rid,
            conclusion="Proceed with maintenance",
            reasoning_summary="High confidence based on evidence",
            recommendation_summary="Schedule repair within 7 days",
            selected_narratives=["narrative-1"],
            rejected_narratives=["narrative-2"],
            confidence=0.85,
            audience=ExplanationLayer.EXECUTIVE,
        )
        assert d.conclusion == "Proceed with maintenance"
        assert d.confidence == 0.85
        assert len(d.selected_narratives) == 1
        assert len(d.rejected_narratives) == 1
        assert d.audience == ExplanationLayer.EXECUTIVE

    def test_decision_requires_result_id(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationDecision()

    def test_decision_confidence_bounds(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ExplanationDecision(result_id=rid, confidence=-0.1)
        with pytest.raises(ValidationError):
            ExplanationDecision(result_id=rid, confidence=1.1)


# ═══════════════════════════════════════════════════════════════════════
# 22. Events
# ═══════════════════════════════════════════════════════════════════════


class TestEvents:
    def test_base_event(self) -> None:
        e = ExplanationEvent(event_type="test.event")
        assert e.event_type == "test.event"
        assert e.explanation_id == ""
        assert e.correlation_id == ""

    def test_explanation_requested(self) -> None:
        e = ExplanationRequested(
            explanation_id="exp-1",
            correlation_id="corr-1",
            domain="ENERGY",
            target_audiences=["EXECUTIVE", "ENGINEER"],
        )
        assert e.event_type == "explanation.requested"
        assert e.domain == "ENERGY"
        assert len(e.target_audiences) == 2

    def test_explanation_generated(self) -> None:
        e = ExplanationGenerated(
            explanation_id="exp-1",
            result_id="res-1",
            narratives_count=3,
        )
        assert e.event_type == "explanation.generated"
        assert e.result_id == "res-1"
        assert e.narratives_count == 3

    def test_explanation_validated(self) -> None:
        e = ExplanationValidated(
            explanation_id="exp-1",
            result_id="res-1",
            passed=True,
            violations=[],
        )
        assert e.event_type == "explanation.validated"
        assert e.passed is True
        assert e.violations == []

    def test_explanation_completed(self) -> None:
        e = ExplanationCompleted(
            explanation_id="exp-1",
            result_id="res-1",
            status="COMPLETED",
            duration_ms=150.5,
        )
        assert e.event_type == "explanation.completed"
        assert e.status == "COMPLETED"
        assert e.duration_ms == 150.5

    def test_event_inheritance(self) -> None:
        e = ExplanationRequested(explanation_id="exp-1")
        assert isinstance(e, ExplanationEvent)
        assert e.timestamp is not None
        assert e.event_type == "explanation.requested"

    def test_generated_narratives_count_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationGenerated(narratives_count=-1)

    def test_completed_duration_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationCompleted(duration_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# 23. Exceptions
# ═══════════════════════════════════════════════════════════════════════


class TestExceptions:
    def test_base_exception(self) -> None:
        e = ExplainabilityException("base error")
        assert str(e) == "base error"
        assert isinstance(e, Exception)

    def test_narrative_exception(self) -> None:
        e = NarrativeException("narrative error", narrative_id="n-1")
        assert str(e) == "narrative error"
        assert e.narrative_id == "n-1"
        assert isinstance(e, ExplainabilityException)

    def test_citation_exception(self) -> None:
        e = CitationException("citation error", citation_id="c-1")
        assert str(e) == "citation error"
        assert e.citation_id == "c-1"
        assert isinstance(e, ExplainabilityException)

    def test_trace_exception(self) -> None:
        e = TraceException("trace error", trace_id="t-1")
        assert str(e) == "trace error"
        assert e.trace_id == "t-1"
        assert isinstance(e, ExplainabilityException)

    def test_default_messages(self) -> None:
        assert "explainability error" in str(ExplainabilityException())
        assert "narrative error" in str(NarrativeException())
        assert "citation error" in str(CitationException())
        assert "trace error" in str(TraceException())

    def test_exception_hierarchy(self) -> None:
        assert issubclass(NarrativeException, ExplainabilityException)
        assert issubclass(CitationException, ExplainabilityException)
        assert issubclass(TraceException, ExplainabilityException)


# ═══════════════════════════════════════════════════════════════════════
# 24. DTOs
# ═══════════════════════════════════════════════════════════════════════


class TestExplanationRequestDTO:
    def test_default_request_dto(self) -> None:
        rid = uuid.uuid4()
        dto = ExplanationRequestDTO(reasoning_result_id=str(rid))
        assert dto.reasoning_result_id == str(rid)
        assert dto.evidence_result_id == ""
        assert dto.recommendation_result_id == ""
        assert dto.domain == "GENERAL"
        assert dto.target_audiences == []

    def test_request_dto_with_values(self) -> None:
        rid = uuid.uuid4()
        dto = ExplanationRequestDTO(
            reasoning_result_id=str(rid),
            evidence_result_id="ev-1",
            recommendation_result_id="rec-1",
            target_audiences=["EXECUTIVE", "ENGINEER"],
            domain="ENERGY",
            context={"asset_id": "asset-1"},
        )
        assert dto.evidence_result_id == "ev-1"
        assert dto.domain == "ENERGY"
        assert len(dto.target_audiences) == 2
        assert dto.context["asset_id"] == "asset-1"

    def test_request_dto_requires_reasoning_result_id(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationRequestDTO()


class TestExplanationResponseDTO:
    def test_default_response_dto(self) -> None:
        rid = uuid.uuid4()
        req_id = uuid.uuid4()
        dto = ExplanationResponseDTO(result_id=rid, request_id=req_id)
        assert dto.result_id == rid
        assert dto.request_id == req_id
        assert dto.package_id == ""
        assert dto.narratives_count == 0
        assert dto.citations_count == 0
        assert dto.confidence == 0.0
        assert dto.status == ""

    def test_response_dto_with_values(self) -> None:
        rid = uuid.uuid4()
        req_id = uuid.uuid4()
        dto = ExplanationResponseDTO(
            result_id=rid,
            request_id=req_id,
            package_id="pkg-1",
            narratives_count=3,
            citations_count=10,
            confidence=0.85,
            status="COMPLETED",
        )
        assert dto.package_id == "pkg-1"
        assert dto.narratives_count == 3
        assert dto.citations_count == 10
        assert dto.confidence == 0.85
        assert dto.status == "COMPLETED"

    def test_response_dto_requires_ids(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationResponseDTO()
        with pytest.raises(ValidationError):
            ExplanationResponseDTO(result_id=uuid.uuid4())
        with pytest.raises(ValidationError):
            ExplanationResponseDTO(request_id=uuid.uuid4())


class TestExplanationPackageDTO:
    def test_default_package_dto(self) -> None:
        dto = ExplanationPackageDTO()
        assert dto.package_id == ""
        assert dto.result_id == ""
        assert dto.primary_narrative == {}
        assert dto.supporting_narratives == []
        assert dto.evidence_citations == []
        assert dto.reasoning_summary == ""
        assert dto.recommendation_summary == ""
        assert dto.overall_confidence == 0.0

    def test_package_dto_with_values(self) -> None:
        dto = ExplanationPackageDTO(
            package_id="pkg-1",
            result_id="res-1",
            primary_narrative={"title": "Summary", "content": "..."},
            supporting_narratives=[{"title": "Detail"}],
            evidence_citations=[{"source": "ev-1"}],
            reasoning_summary="High confidence",
            recommendation_summary="Schedule repair",
            overall_confidence=0.85,
        )
        assert dto.package_id == "pkg-1"
        assert dto.primary_narrative["title"] == "Summary"
        assert len(dto.supporting_narratives) == 1
        assert dto.overall_confidence == 0.85
        assert dto.reasoning_summary == "High confidence"
        assert dto.recommendation_summary == "Schedule repair"


# ═══════════════════════════════════════════════════════════════════════
# 25. Interfaces
# ═══════════════════════════════════════════════════════════════════════


class TestInterfaces:
    def test_explainability_service_abstract(self) -> None:
        with pytest.raises(TypeError):
            ExplainabilityService()

    def test_explainability_manager_abstract(self) -> None:
        with pytest.raises(TypeError):
            ExplainabilityManager()

    def test_explainability_coordinator_abstract(self) -> None:
        with pytest.raises(TypeError):
            ExplainabilityCoordinator()

    def test_narrative_builder_abstract(self) -> None:
        with pytest.raises(TypeError):
            NarrativeBuilder()

    def test_citation_builder_abstract(self) -> None:
        with pytest.raises(TypeError):
            CitationBuilder()

    def test_trace_builder_abstract(self) -> None:
        with pytest.raises(TypeError):
            TraceBuilder()

    def test_audience_formatter_abstract(self) -> None:
        with pytest.raises(TypeError):
            AudienceFormatter()

    def test_explanation_validator_abstract(self) -> None:
        with pytest.raises(TypeError):
            ExplanationValidator()

    def test_all_interfaces_are_abc(self) -> None:
        import abc
        assert issubclass(ExplainabilityService, abc.ABC)
        assert issubclass(ExplainabilityManager, abc.ABC)
        assert issubclass(ExplainabilityCoordinator, abc.ABC)
        assert issubclass(NarrativeBuilder, abc.ABC)
        assert issubclass(CitationBuilder, abc.ABC)
        assert issubclass(TraceBuilder, abc.ABC)
        assert issubclass(AudienceFormatter, abc.ABC)
        assert issubclass(ExplanationValidator, abc.ABC)


# ═══════════════════════════════════════════════════════════════════════
# 26. Model Relationships
# ═══════════════════════════════════════════════════════════════════════


class TestModelRelationships:
    def test_narrative_in_package(self) -> None:
        rid = uuid.uuid4()
        narrative = ExplanationNarrative(
            package_id=rid,
            title="Primary Analysis",
            content="Content body",
        )
        pkg = ExplanationPackage(
            result_id=rid,
            primary_narrative=narrative,
        )
        assert pkg.primary_narrative is not None
        assert pkg.primary_narrative.title == "Primary Analysis"
        assert pkg.primary_narrative.content == "Content body"

    def test_citation_in_narrative(self) -> None:
        nid = uuid.uuid4()
        citation = ExplanationCitation(
            narrative_id=nid,
            citation_type=CitationType.EVIDENCE,
            source_id="ev-1",
            relevance_score=0.9,
        )
        assert citation.narrative_id == nid
        assert citation.citation_type == CitationType.EVIDENCE
        assert citation.source_id == "ev-1"

    def test_citations_in_package(self) -> None:
        rid = uuid.uuid4()
        nid = uuid.uuid4()
        citation = ExplanationCitation(
            narrative_id=nid,
            citation_type=CitationType.REASONING,
            excerpt="Critical reasoning step",
        )
        pkg = ExplanationPackage(
            result_id=rid,
            evidence_citations=[citation],
            reasoning_summary="Based on evidence",
        )
        assert len(pkg.evidence_citations) == 1
        assert pkg.evidence_citations[0].citation_type == CitationType.REASONING
        assert pkg.reasoning_summary == "Based on evidence"

    def test_decision_in_result(self) -> None:
        rid = uuid.uuid4()
        decision = ExplanationDecision(
            result_id=rid,
            conclusion="Approve maintenance",
            reasoning_summary="Evidence supports action",
        )
        result = ExplanationResult(
            request_id=rid,
            decisions=[decision],
            status=ExplanationStatus.COMPLETED,
        )
        assert len(result.decisions) == 1
        assert result.decisions[0].conclusion == "Approve maintenance"
        assert result.decisions[0].reasoning_summary == "Evidence supports action"

    def test_package_in_result(self) -> None:
        rid = uuid.uuid4()
        narrative = ExplanationNarrative(
            package_id=rid,
            title="Explanation",
        )
        pkg = ExplanationPackage(
            result_id=rid,
            primary_narrative=narrative,
        )
        result = ExplanationResult(
            request_id=rid,
            package=pkg,
        )
        assert result.package is not None
        assert result.package.primary_narrative is not None
        assert result.package.primary_narrative.title == "Explanation"

    def test_dto_to_model_flow(self) -> None:
        rid = uuid.uuid4()
        dto = ExplanationRequestDTO(
            reasoning_result_id=str(rid),
            domain="ENERGY",
            target_audiences=["EXECUTIVE", "ENGINEER"],
        )
        audiences = [
            ExplanationLayer(a)
            for a in dto.target_audiences
        ]
        req = ExplanationRequest(
            reasoning_result_id=uuid.UUID(dto.reasoning_result_id),
            domain=ExplanationDomain(dto.domain),
            target_audiences=audiences,
        )
        assert req.reasoning_result_id == rid
        assert req.domain == ExplanationDomain.ENERGY
        assert len(req.target_audiences) == 2

    def test_confidence_in_result(self) -> None:
        rid = uuid.uuid4()
        confidence = ExplanationConfidence(
            overall_confidence=0.85,
            narrative_quality=0.9,
        )
        result = ExplanationResult(
            request_id=rid,
            confidence=confidence,
        )
        assert result.confidence is not None
        assert result.confidence.overall_confidence == 0.85
        assert result.confidence.narrative_quality == 0.9

    def test_supporting_narratives_in_package(self) -> None:
        rid = uuid.uuid4()
        n1 = ExplanationNarrative(
            package_id=rid,
            title="Technical Detail",
            narrative_type=NarrativeType.TECHNICAL,
        )
        n2 = ExplanationNarrative(
            package_id=rid,
            title="Business Impact",
            narrative_type=NarrativeType.BUSINESS,
        )
        pkg = ExplanationPackage(
            result_id=rid,
            supporting_narratives=[n1, n2],
        )
        assert len(pkg.supporting_narratives) == 2
        assert pkg.supporting_narratives[0].narrative_type == NarrativeType.TECHNICAL
        assert pkg.supporting_narratives[1].title == "Business Impact"


# ═══════════════════════════════════════════════════════════════════════
# 27. Pydantic Validation
# ═══════════════════════════════════════════════════════════════════════


class TestPydanticValidation:
    def test_invalid_enum_value(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationRequest(domain="INVALID_DOMAIN")

    def test_invalid_confidence_type(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationConfidence(overall_confidence="high")

    def test_negative_score(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ExplanationPackage(result_id=rid, overall_confidence=-0.1)

    def test_excessive_score(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ExplanationPackage(result_id=rid, overall_confidence=1.5)

    def test_invalid_domain(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationRequest(domain="FINANCE")

    def test_invalid_layer(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationNarrative(
                package_id=uuid.uuid4(),
                audience="INTERN",
            )

    def test_invalid_citation_type(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type="UNKNOWN_TYPE",
            )

    def test_invalid_narrative_type(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationNarrative(
                package_id=uuid.uuid4(),
                narrative_type="VERBOSE",
            )

    def test_invalid_status_value(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationResult(
                request_id=uuid.uuid4(),
                status="IN_PROGRESS",
            )

    def test_negative_relevance_score(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type=CitationType.EVIDENCE,
                relevance_score=-0.5,
            )

    def test_excessive_relevance_score(self) -> None:
        with pytest.raises(ValidationError):
            ExplanationCitation(
                narrative_id=uuid.uuid4(),
                citation_type=CitationType.EVIDENCE,
                relevance_score=1.5,
            )
