"""Comprehensive tests for the Explainability Engine Phase 2 (Execution Pipeline).

Tests all 13 deterministic-placeholder execution components:
  1. Execution Models (models.py)
  2. NarrativeBuilder (narrative_builder.py)
  3. AudienceFormatter (audience_formatter.py)
  4. CitationManager (citation_manager.py)
  5. ExplanationBuilder (builder.py)
  6. TraceAggregator (trace_aggregator.py)
  7. ExplanationSections (sections.py)
  8. ExplanationQualityManager (quality_manager.py)
  9. TimelineBuilder (timeline_builder.py)
 10. TemplateManager (template_manager.py)
 11. PolicyEngine (policy_engine.py)
 12. ExplainabilityTrace (trace.py)
 13. ExplainabilityMetricsCollector (metrics.py)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from adip.explainability.contracts.models import (
    ExplanationCitation,
    ExplanationNarrative,
    ExplanationPackage,
    ExplanationRequest,
)
from adip.explainability.enums import (
    CitationType,
    ExplanationLayer,
    NarrativeType,
)
from adip.explainability.execution.audience_formatter import AudienceFormatter
from adip.explainability.execution.builder import ExplanationBuilder
from adip.explainability.execution.citation_manager import CitationManager
from adip.explainability.execution.metrics import ExplainabilityMetricsCollector
from adip.explainability.execution.models import (
    AudienceFormat,
    ExplainabilityMetrics,
    ExplanationSection,
    ExplanationTimeline,
    NarrativeTemplate,
    PolicyRule,
    QualityScore,
    SectionContent,
    TimelineEvent,
    TraceRecord,
)
from adip.explainability.execution.narrative_builder import NarrativeBuilder
from adip.explainability.execution.policy_engine import PolicyEngine
from adip.explainability.execution.quality_manager import ExplanationQualityManager
from adip.explainability.execution.sections import ExplanationSections
from adip.explainability.execution.template_manager import TemplateManager
from adip.explainability.execution.timeline_builder import TimelineBuilder
from adip.explainability.execution.trace import ExplainabilityTrace
from adip.explainability.execution.trace_aggregator import TraceAggregator

# =============================================================================
# 1. Execution Models
# =============================================================================


class TestExplanationSection:
    def test_default_section(self) -> None:
        s = ExplanationSection()
        assert s.section_id is not None
        assert s.section_type == ""
        assert s.title == ""
        assert s.content == ""
        assert s.order == 0
        assert s.audience == ""
        assert s.citations == []
        assert s.metadata == {}

    def test_custom_values(self) -> None:
        s = ExplanationSection(
            section_type="summary",
            title="Executive Summary",
            content="Key findings and recommendations.",
            order=1,
            audience="EXECUTIVE",
            citations=["cit-1", "cit-2"],
            metadata={"source": "test"},
        )
        assert s.section_type == "summary"
        assert s.title == "Executive Summary"
        assert s.content == "Key findings and recommendations."
        assert s.order == 1
        assert s.audience == "EXECUTIVE"
        assert s.citations == ["cit-1", "cit-2"]
        assert s.metadata["source"] == "test"

    def test_order_non_negative(self) -> None:
        with pytest.raises(Exception):
            ExplanationSection(order=-1)

    def test_unique_ids(self) -> None:
        s1 = ExplanationSection()
        s2 = ExplanationSection()
        assert s1.section_id != s2.section_id


class TestTimelineEvent:
    def test_default_event(self) -> None:
        e = TimelineEvent()
        assert e.event_id is not None
        assert e.event_type == ""
        assert e.description == ""
        assert isinstance(e.timestamp, datetime)
        assert e.metadata == {}

    def test_custom_values(self) -> None:
        now = datetime.now(UTC)
        e = TimelineEvent(
            event_type="narrative_created",
            description="Narrative 1 created",
            timestamp=now,
            metadata={"narrative_id": "n-1"},
        )
        assert e.event_type == "narrative_created"
        assert e.description == "Narrative 1 created"
        assert e.timestamp == now
        assert e.metadata["narrative_id"] == "n-1"

    def test_unique_ids(self) -> None:
        e1 = TimelineEvent()
        e2 = TimelineEvent()
        assert e1.event_id != e2.event_id


class TestExplanationTimeline:
    def test_default_timeline(self) -> None:
        t = ExplanationTimeline()
        assert t.timeline_id is not None
        assert t.explanation_id == ""
        assert t.events == []
        assert isinstance(t.start_time, datetime)
        assert isinstance(t.end_time, datetime)
        assert t.total_duration_ms == 0.0

    def test_events_storage(self) -> None:
        now = datetime.now(UTC)
        events = [
            {"event_type": "request_created", "description": "Request created", "timestamp": now.isoformat()},
            {"event_type": "narrative_created", "description": "Narrative built", "timestamp": now.isoformat()},
        ]
        t = ExplanationTimeline(
            explanation_id="exp-1",
            events=events,
            start_time=now,
            end_time=now,
            total_duration_ms=150.5,
        )
        assert t.explanation_id == "exp-1"
        assert len(t.events) == 2
        assert t.events[0]["event_type"] == "request_created"
        assert t.total_duration_ms == 150.5

    def test_duration_non_negative(self) -> None:
        with pytest.raises(Exception):
            ExplanationTimeline(total_duration_ms=-1.0)

    def test_unique_ids(self) -> None:
        t1 = ExplanationTimeline()
        t2 = ExplanationTimeline()
        assert t1.timeline_id != t2.timeline_id


class TestSectionContent:
    def test_default_content(self) -> None:
        c = SectionContent()
        assert c.content_id is not None
        assert c.section_type == ""
        assert c.summary == ""
        assert c.details == ""
        assert c.key_points == []
        assert c.audience == ""

    def test_with_key_points(self) -> None:
        c = SectionContent(
            section_type="evidence",
            summary="Evidence summary",
            details="Detailed evidence",
            key_points=["Point 1", "Point 2", "Point 3"],
            audience="ENGINEER",
        )
        assert c.section_type == "evidence"
        assert c.summary == "Evidence summary"
        assert c.key_points == ["Point 1", "Point 2", "Point 3"]
        assert len(c.key_points) == 3
        assert c.audience == "ENGINEER"


class TestAudienceFormat:
    def test_default_format(self) -> None:
        f = AudienceFormat()
        assert f.format_id is not None
        assert f.audience == ""
        assert f.template_name == ""
        assert f.detail_level == ""
        assert f.technical_depth == 0.5
        assert f.format_preferences == {}

    def test_technical_depth_range(self) -> None:
        with pytest.raises(Exception):
            AudienceFormat(technical_depth=-0.1)
        with pytest.raises(Exception):
            AudienceFormat(technical_depth=1.1)

    def test_custom_values(self) -> None:
        f = AudienceFormat(
            audience="EXECUTIVE",
            template_name="executive_briefing",
            detail_level="high",
            technical_depth=0.1,
            format_preferences={"verbosity": "concise"},
        )
        assert f.audience == "EXECUTIVE"
        assert f.template_name == "executive_briefing"
        assert f.technical_depth == 0.1


class TestNarrativeTemplate:
    def test_default_template(self) -> None:
        t = NarrativeTemplate()
        assert t.template_id is not None
        assert t.template_type == ""
        assert t.name == ""
        assert t.sections == []
        assert t.audience == ""

    def test_summary_template(self) -> None:
        t = NarrativeTemplate(
            template_type="executive",
            name="Executive Briefing",
            sections=["summary", "key_findings", "recommendations"],
            audience="EXECUTIVE",
        )
        assert t.template_type == "executive"
        assert t.name == "Executive Briefing"
        assert len(t.sections) == 3
        assert t.audience == "EXECUTIVE"

    def test_technical_template(self) -> None:
        t = NarrativeTemplate(
            template_type="technical",
            name="Technical Deep Dive",
            sections=["summary", "technical_analysis", "evidence"],
            audience="ENGINEER",
        )
        assert t.template_type == "technical"
        assert t.name == "Technical Deep Dive"
        assert t.audience == "ENGINEER"

    def test_audit_template(self) -> None:
        t = NarrativeTemplate(
            template_type="audit",
            name="Audit Report",
            sections=["summary", "compliance_check", "evidence"],
            audience="AUDITOR",
        )
        assert t.template_type == "audit"
        assert t.name == "Audit Report"

    def test_incident_template(self) -> None:
        t = NarrativeTemplate(
            template_type="incident",
            name="Incident Report",
            sections=["summary", "timeline", "impact_analysis"],
            audience="OPERATOR",
        )
        assert t.template_type == "incident"
        assert t.name == "Incident Report"

    def test_compliance_template(self) -> None:
        t = NarrativeTemplate(
            template_type="compliance",
            name="Compliance Summary",
            sections=["summary", "regulatory_findings"],
            audience="MANAGER",
        )
        assert t.template_type == "compliance"
        assert t.name == "Compliance Summary"


class TestPolicyRule:
    def test_default_policy(self) -> None:
        p = PolicyRule()
        assert p.rule_id is not None
        assert p.policy_type == ""
        assert p.name == ""
        assert p.allowed_audiences == []
        assert p.max_narratives == 10
        assert p.require_citations is False
        assert p.require_trace is False

    def test_summary_policy(self) -> None:
        p = PolicyRule(
            policy_type="SUMMARY",
            name="Summary Policy",
            allowed_audiences=["EXECUTIVE", "MANAGER"],
            max_narratives=1,
            require_citations=False,
            require_trace=False,
        )
        assert p.policy_type == "SUMMARY"
        assert p.max_narratives == 1
        assert p.require_citations is False

    def test_full_policy(self) -> None:
        p = PolicyRule(
            policy_type="FULL",
            name="Full Policy",
            allowed_audiences=["ENGINEER", "TECHNICIAN"],
            max_narratives=10,
            require_citations=True,
            require_trace=True,
        )
        assert p.policy_type == "FULL"
        assert p.require_citations is True
        assert p.require_trace is True

    def test_confidential_policy(self) -> None:
        p = PolicyRule(
            policy_type="CONFIDENTIAL",
            name="Confidential Policy",
            allowed_audiences=["EXECUTIVE", "AUDITOR"],
            max_narratives=3,
            require_citations=True,
        )
        assert p.policy_type == "CONFIDENTIAL"
        assert p.max_narratives == 3

    def test_max_narratives_positive(self) -> None:
        with pytest.raises(Exception):
            PolicyRule(max_narratives=0)
        with pytest.raises(Exception):
            PolicyRule(max_narratives=-1)


class TestQualityScore:
    def test_default_score(self) -> None:
        q = QualityScore()
        assert q.score_id is not None
        assert q.completeness == 0.0
        assert q.citation_coverage == 0.0
        assert q.trace_coverage == 0.0
        assert q.readability == 0.0
        assert q.consistency == 0.0
        assert q.overall == 0.0

    def test_custom_values(self) -> None:
        q = QualityScore(
            completeness=0.85,
            citation_coverage=0.75,
            trace_coverage=0.6,
            readability=0.9,
            consistency=0.8,
            overall=0.78,
        )
        assert q.completeness == 0.85
        assert q.citation_coverage == 0.75
        assert q.trace_coverage == 0.6
        assert q.readability == 0.9
        assert q.consistency == 0.8
        assert q.overall == 0.78

    def test_bounds(self) -> None:
        with pytest.raises(Exception):
            QualityScore(completeness=-0.1)
        with pytest.raises(Exception):
            QualityScore(completeness=1.1)
        with pytest.raises(Exception):
            QualityScore(citation_coverage=-0.1)
        with pytest.raises(Exception):
            QualityScore(citation_coverage=1.1)
        with pytest.raises(Exception):
            QualityScore(trace_coverage=-0.1)
        with pytest.raises(Exception):
            QualityScore(trace_coverage=1.1)
        with pytest.raises(Exception):
            QualityScore(readability=-0.1)
        with pytest.raises(Exception):
            QualityScore(readability=1.1)
        with pytest.raises(Exception):
            QualityScore(consistency=-0.1)
        with pytest.raises(Exception):
            QualityScore(consistency=1.1)
        with pytest.raises(Exception):
            QualityScore(overall=-0.1)
        with pytest.raises(Exception):
            QualityScore(overall=1.1)


class TestTraceRecord:
    def test_default_record(self) -> None:
        t = TraceRecord()
        assert t.trace_id is not None
        assert t.stage_name == ""
        assert t.operation == ""
        assert t.explanation_id == ""
        assert t.correlation_id == ""
        assert t.duration_ms is None
        assert t.success is True
        assert t.warnings == []
        assert t.errors == []

    def test_with_values(self) -> None:
        now = datetime.now(UTC)
        t = TraceRecord(
            stage_name="NARRATIVE",
            operation="build",
            explanation_id="exp-1",
            correlation_id="corr-1",
            started_at=now,
            completed_at=now,
            duration_ms=42.5,
            success=True,
            warnings=["Missing optional context"],
            errors=[],
            metadata={"source": "test"},
        )
        assert t.stage_name == "NARRATIVE"
        assert t.operation == "build"
        assert t.duration_ms == 42.5
        assert t.success is True
        assert t.warnings == ["Missing optional context"]
        assert t.errors == []

    def test_with_warnings_and_errors(self) -> None:
        t = TraceRecord(
            warnings=["Warning 1", "Warning 2"],
            errors=["Error 1"],
        )
        assert len(t.warnings) == 2
        assert len(t.errors) == 1

    def test_duration_non_negative(self) -> None:
        with pytest.raises(Exception):
            TraceRecord(duration_ms=-1.0)


class TestExplainabilityMetrics:
    def test_default_metrics(self) -> None:
        m = ExplainabilityMetrics()
        assert m.metrics_id is not None
        assert m.explanations_total == 0
        assert m.narratives_total == 0
        assert m.citations_total == 0
        assert m.audience_distribution == {}
        assert m.template_usage == {}
        assert m.average_quality == 0.0
        assert m.average_completeness == 0.0

    def test_with_values(self) -> None:
        now = datetime.now(UTC)
        m = ExplainabilityMetrics(
            explanations_total=50,
            narratives_total=120,
            citations_total=300,
            audience_distribution={"EXECUTIVE": 25, "ENGINEER": 25},
            template_usage={"executive": 10, "technical": 5},
            average_quality=0.82,
            average_completeness=0.78,
            collected_at=now,
        )
        assert m.explanations_total == 50
        assert m.narratives_total == 120
        assert m.citations_total == 300
        assert m.audience_distribution["EXECUTIVE"] == 25
        assert m.template_usage["executive"] == 10
        assert m.average_quality == 0.82
        assert m.average_completeness == 0.78

    def test_non_negative_constraints(self) -> None:
        with pytest.raises(Exception):
            ExplainabilityMetrics(explanations_total=-1)
        with pytest.raises(Exception):
            ExplainabilityMetrics(narratives_total=-1)
        with pytest.raises(Exception):
            ExplainabilityMetrics(citations_total=-1)
        with pytest.raises(Exception):
            ExplainabilityMetrics(average_quality=-0.1)
        with pytest.raises(Exception):
            ExplainabilityMetrics(average_quality=1.1)
        with pytest.raises(Exception):
            ExplainabilityMetrics(average_completeness=-0.1)
        with pytest.raises(Exception):
            ExplainabilityMetrics(average_completeness=1.1)


# =============================================================================
# 2. NarrativeBuilder
# =============================================================================


class TestNarrativeBuilder:
    def test_build_narrative_default(self) -> None:
        nb = NarrativeBuilder()
        narrative = nb.build_narrative(narrative_type="SUMMARY", audience="EXECUTIVE")
        assert isinstance(narrative, ExplanationNarrative)
        assert narrative.narrative_type == NarrativeType.SUMMARY
        assert narrative.audience == ExplanationLayer.EXECUTIVE
        assert narrative.title == "Executive Summary"
        assert "explanation content for executive" in narrative.content
        assert "summary" in narrative.summary.lower()

    def test_build_narrative_technical_engineer(self) -> None:
        nb = NarrativeBuilder()
        narrative = nb.build_narrative(
            narrative_type="TECHNICAL",
            audience="ENGINEER",
            context={"asset": "turbine-1"},
            correlation_id="corr-1",
        )
        assert narrative.narrative_type == NarrativeType.TECHNICAL
        assert narrative.audience == ExplanationLayer.ENGINEER
        assert narrative.title == "Technical Analysis"
        assert "engineer" in narrative.content
        assert narrative.metadata.get("correlation_id") == "corr-1"

    def test_build_narrative_detailed_operator(self) -> None:
        nb = NarrativeBuilder()
        narrative = nb.build_narrative(narrative_type="DETAILED", audience="OPERATOR")
        assert narrative.narrative_type == NarrativeType.DETAILED
        assert narrative.audience == ExplanationLayer.OPERATOR
        assert narrative.title == "Detailed Explanation"

    def test_build_narrative_business_manager(self) -> None:
        nb = NarrativeBuilder()
        narrative = nb.build_narrative(narrative_type="BUSINESS", audience="MANAGER")
        assert narrative.narrative_type == NarrativeType.BUSINESS
        assert narrative.audience == ExplanationLayer.MANAGER
        assert narrative.title == "Business Overview"

    def test_build_narrative_audit_auditor(self) -> None:
        nb = NarrativeBuilder()
        narrative = nb.build_narrative(narrative_type="AUDIT", audience="AUDITOR")
        assert narrative.narrative_type == NarrativeType.AUDIT
        assert narrative.audience == ExplanationLayer.AUDITOR
        assert narrative.title == "Audit Report"

    def test_build_narratives_multiple_audiences(self) -> None:
        nb = NarrativeBuilder()
        audiences = [ExplanationLayer.EXECUTIVE, ExplanationLayer.ENGINEER, ExplanationLayer.OPERATOR]
        narratives = nb.build_narratives(audiences=audiences, correlation_id="corr-1")
        assert len(narratives) == 3
        assert narratives[0].audience == ExplanationLayer.EXECUTIVE
        assert narratives[1].audience == ExplanationLayer.ENGINEER
        assert narratives[2].audience == ExplanationLayer.OPERATOR
        assert narratives[0].narrative_type == NarrativeType.SUMMARY
        assert narratives[1].narrative_type == NarrativeType.DETAILED

    def test_build_narratives_all_audiences(self) -> None:
        nb = NarrativeBuilder()
        all_audiences = list(ExplanationLayer)
        narratives = nb.build_narratives(audiences=all_audiences)
        assert len(narratives) == len(all_audiences)

    def test_get_narrative(self) -> None:
        nb = NarrativeBuilder()
        narrative = nb.build_narrative(narrative_type="SUMMARY", audience="EXECUTIVE")
        found = nb.get_narrative(str(narrative.narrative_id))
        assert found is not None
        assert str(found.narrative_id) == str(narrative.narrative_id)

    def test_get_narrative_not_found(self) -> None:
        nb = NarrativeBuilder()
        assert nb.get_narrative("nonexistent") is None

    def test_get_all(self) -> None:
        nb = NarrativeBuilder()
        nb.build_narrative(narrative_type="SUMMARY", audience="EXECUTIVE")
        nb.build_narrative(narrative_type="DETAILED", audience="ENGINEER")
        all_narratives = nb.get_all()
        assert len(all_narratives) == 2

    def test_clear(self) -> None:
        nb = NarrativeBuilder()
        nb.build_narrative(narrative_type="SUMMARY", audience="EXECUTIVE")
        assert nb.count() == 1
        nb.clear()
        assert nb.count() == 0

    def test_count(self) -> None:
        nb = NarrativeBuilder()
        assert nb.count() == 0
        nb.build_narrative(narrative_type="SUMMARY", audience="EXECUTIVE")
        assert nb.count() == 1
        nb.build_narrative(narrative_type="DETAILED", audience="ENGINEER")
        assert nb.count() == 2


# =============================================================================
# 3. AudienceFormatter
# =============================================================================


class TestAudienceFormatter:
    def _make_narrative(self) -> ExplanationNarrative:
        pid = uuid.uuid4()
        return ExplanationNarrative(
            package_id=pid,
            title="Test",
            content="Original content",
            summary="Original summary",
            audience=ExplanationLayer.ENGINEER,
        )

    def test_format_executive(self) -> None:
        af = AudienceFormatter()
        narrative = self._make_narrative()
        formatted = af.format(narrative, ExplanationLayer.EXECUTIVE)
        assert formatted.content.startswith("Executive summary format:")
        assert formatted.summary.startswith("Executive summary format:")

    def test_format_engineer(self) -> None:
        af = AudienceFormatter()
        narrative = self._make_narrative()
        formatted = af.format(narrative, ExplanationLayer.ENGINEER)
        assert formatted.content.startswith("Technical detail format:")
        assert formatted.summary.startswith("Technical detail format:")

    def test_format_manager(self) -> None:
        af = AudienceFormatter()
        narrative = self._make_narrative()
        formatted = af.format(narrative, ExplanationLayer.MANAGER)
        assert formatted.content.startswith("Manager overview format:")
        assert formatted.summary.startswith("Manager overview format:")

    def test_format_operator(self) -> None:
        af = AudienceFormatter()
        narrative = self._make_narrative()
        formatted = af.format(narrative, ExplanationLayer.OPERATOR, correlation_id="corr-1")
        assert formatted.content.startswith("Operator actionable format:")
        assert formatted.summary.startswith("Operator actionable format:")

    def test_format_preserves_original(self) -> None:
        af = AudienceFormatter()
        narrative = self._make_narrative()
        original_content = narrative.content
        original_summary = narrative.summary
        af.format(narrative, ExplanationLayer.EXECUTIVE)
        assert narrative.content == original_content
        assert narrative.summary == original_summary

    def test_format_batch(self) -> None:
        af = AudienceFormatter()
        narratives = [self._make_narrative(), self._make_narrative()]
        formatted = af.format_batch(narratives, ExplanationLayer.EXECUTIVE)
        assert len(formatted) == 2
        for f in formatted:
            assert f.content.startswith("Executive summary format:")

    def test_get_format_executive(self) -> None:
        af = AudienceFormatter()
        fmt = af.get_format("EXECUTIVE")
        assert isinstance(fmt, AudienceFormat)
        assert fmt.audience == "EXECUTIVE"
        assert fmt.technical_depth == 0.1
        assert fmt.detail_level == "high"

    def test_get_format_engineer(self) -> None:
        af = AudienceFormatter()
        fmt = af.get_format("ENGINEER")
        assert fmt.audience == "ENGINEER"
        assert fmt.technical_depth == 0.9
        assert fmt.detail_level == "full"

    def test_get_format_unknown(self) -> None:
        af = AudienceFormatter()
        fmt = af.get_format("UNKNOWN")
        assert fmt.audience == "UNKNOWN"
        assert fmt.technical_depth == 0.5

    def test_get_audience_profiles(self) -> None:
        af = AudienceFormatter()
        profiles = af.get_audience_profiles()
        assert "EXECUTIVE" in profiles
        assert "ENGINEER" in profiles
        assert "MANAGER" in profiles
        assert "OPERATOR" in profiles
        assert len(profiles) == 7


# =============================================================================
# 4. CitationManager
# =============================================================================


class TestCitationManager:
    def _make_nid(self) -> str:
        return str(uuid.uuid4())

    def test_build_citations_with_all_sources(self) -> None:
        cm = CitationManager()
        nid = self._make_nid()
        citations = cm.build_citations(
            narrative_id=nid,
            evidence_ids=["ev-1", "ev-2"],
            reasoning_ids=["rs-1"],
            recommendation_ids=["rec-1"],
        )
        assert len(citations) == 4
        types = [c.citation_type for c in citations]
        assert types.count(CitationType.EVIDENCE) == 2
        assert types.count(CitationType.REASONING) == 1
        assert types.count(CitationType.RECOMMENDATION) == 1

    def test_build_citations_empty_ids(self) -> None:
        cm = CitationManager()
        citations = cm.build_citations(narrative_id=self._make_nid())
        assert citations == []

    def test_build_citations_with_correlation_id(self) -> None:
        cm = CitationManager()
        citations = cm.build_citations(
            narrative_id=self._make_nid(),
            evidence_ids=["ev-1"],
            correlation_id="corr-1",
        )
        assert len(citations) == 1

    def test_build_evidence_citation(self) -> None:
        cm = CitationManager()
        nid = self._make_nid()
        citation = cm.build_evidence_citation(narrative_id=nid, source_id="ev-1")
        assert citation.citation_type == CitationType.EVIDENCE
        assert citation.source_id == "ev-1"
        assert citation.source_type == "evidence"
        assert citation.relevance_score == 0.85
        assert "Placeholder evidence excerpt" in citation.excerpt

    def test_build_reasoning_citation(self) -> None:
        cm = CitationManager()
        nid = self._make_nid()
        citation = cm.build_reasoning_citation(narrative_id=nid, source_id="rs-1")
        assert citation.citation_type == CitationType.REASONING
        assert citation.source_id == "rs-1"
        assert citation.source_type == "reasoning"
        assert citation.relevance_score == 0.90

    def test_build_recommendation_citation(self) -> None:
        cm = CitationManager()
        nid = self._make_nid()
        citation = cm.build_recommendation_citation(narrative_id=nid, source_id="rec-1")
        assert citation.citation_type == CitationType.RECOMMENDATION
        assert citation.source_id == "rec-1"
        assert citation.source_type == "recommendation"
        assert citation.relevance_score == 0.80

    def test_get_by_narrative(self) -> None:
        cm = CitationManager()
        nid1 = self._make_nid()
        cm.build_citations(
            narrative_id=nid1,
            evidence_ids=["ev-1"],
            reasoning_ids=["rs-1"],
        )
        nid2 = self._make_nid()
        cm.build_citations(
            narrative_id=nid2,
            evidence_ids=["ev-2"],
        )
        n1_citations = cm.get_by_narrative(str(cm.get_all()[0].narrative_id))
        assert len(n1_citations) >= 2

    def test_get_by_type(self) -> None:
        cm = CitationManager()
        nid = self._make_nid()
        cm.build_citations(
            narrative_id=nid,
            evidence_ids=["ev-1", "ev-2"],
            reasoning_ids=["rs-1"],
        )
        evidence_citations = cm.get_by_type(CitationType.EVIDENCE)
        reasoning_citations = cm.get_by_type(CitationType.REASONING)
        assert len(evidence_citations) == 2
        assert len(reasoning_citations) == 1

    def test_get_all(self) -> None:
        cm = CitationManager()
        assert cm.get_all() == []
        cm.build_citations(narrative_id=self._make_nid(), evidence_ids=["ev-1"])
        assert len(cm.get_all()) == 1

    def test_clear(self) -> None:
        cm = CitationManager()
        cm.build_citations(narrative_id=self._make_nid(), evidence_ids=["ev-1"])
        assert cm.count() == 1
        cm.clear()
        assert cm.count() == 0

    def test_count(self) -> None:
        cm = CitationManager()
        assert cm.count() == 0
        cm.build_citations(narrative_id=self._make_nid(), evidence_ids=["ev-1"])
        assert cm.count() == 1


# =============================================================================
# 5. ExplanationBuilder
# =============================================================================


class TestExplanationBuilder:
    def _make_request(self) -> ExplanationRequest:
        return ExplanationRequest(
            context={"asset_id": "asset-1"},
            metadata={"version": "1.0"},
        )

    def _make_narrative(self, request: ExplanationRequest) -> ExplanationNarrative:
        return ExplanationNarrative(
            package_id=request.request_id,
            title="Primary Explanation",
            content="Content body",
            summary="Brief summary",
            audience=ExplanationLayer.EXECUTIVE,
            narrative_type=NarrativeType.SUMMARY,
        )

    def _make_citation(self, narrative_id: uuid.UUID) -> ExplanationCitation:
        return ExplanationCitation(
            narrative_id=narrative_id,
            citation_type=CitationType.EVIDENCE,
            source_id="ev-1",
            relevance_score=0.85,
        )

    def test_build_creates_package(self) -> None:
        builder = ExplanationBuilder()
        request = self._make_request()
        narrative = self._make_narrative(request)
        citation = self._make_citation(narrative.narrative_id)
        package = builder.build(
            request=request,
            narratives=[narrative],
            citations=[citation],
        )
        assert isinstance(package, ExplanationPackage)
        assert package.result_id == request.request_id
        assert package.primary_narrative is not None
        assert package.primary_narrative.title == "Primary Explanation"
        assert len(package.evidence_citations) == 1

    def test_build_with_multiple_narratives(self) -> None:
        builder = ExplanationBuilder()
        request = self._make_request()
        n1 = self._make_narrative(request)
        n2 = ExplanationNarrative(
            package_id=request.request_id,
            title="Supporting Detail",
            content="Supporting content",
            audience=ExplanationLayer.ENGINEER,
            narrative_type=NarrativeType.DETAILED,
        )
        package = builder.build(
            request=request,
            narratives=[n1, n2],
            citations=[],
        )
        assert package.primary_narrative is not None
        assert package.primary_narrative.title == "Primary Explanation"
        assert len(package.supporting_narratives) == 1
        assert package.supporting_narratives[0].title == "Supporting Detail"

    def test_build_empty_narratives(self) -> None:
        builder = ExplanationBuilder()
        request = self._make_request()
        package = builder.build(request=request, narratives=[], citations=[])
        assert package.primary_narrative is None
        assert package.overall_confidence == 0.0

    def test_build_confidence_average(self) -> None:
        builder = ExplanationBuilder()
        request = self._make_request()
        n1 = self._make_narrative(request)
        n2 = ExplanationNarrative(
            package_id=request.request_id,
            title="Narrative 2",
            content="Content",
            audience=ExplanationLayer.ENGINEER,
        )
        package = builder.build(
            request=request,
            narratives=[n1, n2],
            citations=[],
        )
        assert package.overall_confidence == 0.85

    def test_build_reasoning_and_recommendation_summaries(self) -> None:
        builder = ExplanationBuilder()
        request = self._make_request()
        narrative = self._make_narrative(request)
        package = builder.build(
            request=request,
            narratives=[narrative],
            citations=[],
            correlation_id="corr-1",
        )
        assert package.reasoning_summary == "Placeholder reasoning summary for explanation package."
        assert package.recommendation_summary == "Placeholder recommendation summary for explanation package."

    def test_build_sections(self) -> None:
        builder = ExplanationBuilder()
        request = self._make_request()
        narrative = self._make_narrative(request)
        citation = self._make_citation(narrative.narrative_id)
        sections = builder.build_sections(
            narratives=[narrative],
            citations=[citation],
            correlation_id="corr-1",
        )
        assert len(sections) == 1
        assert isinstance(sections[0], ExplanationSection)
        assert sections[0].section_type == "summary"
        assert sections[0].title == "Primary Explanation"
        assert sections[0].order == 0
        assert len(sections[0].citations) == 1

    def test_build_sections_multiple(self) -> None:
        builder = ExplanationBuilder()
        request = self._make_request()
        n1 = self._make_narrative(request)
        n2 = ExplanationNarrative(
            package_id=request.request_id,
            title="Technical Analysis",
            content="Technical content",
            audience=ExplanationLayer.ENGINEER,
            narrative_type=NarrativeType.TECHNICAL,
        )
        sections = builder.build_sections(
            narratives=[n1, n2],
            citations=[],
        )
        assert len(sections) == 2
        assert sections[0].order == 0
        assert sections[0].section_type == "summary"
        assert sections[1].order == 1
        assert sections[1].section_type == "technical"
        assert sections[1].title == "Technical Analysis"


# =============================================================================
# 6. TraceAggregator
# =============================================================================


class TestTraceAggregator:
    def test_aggregate_empty(self) -> None:
        ta = TraceAggregator()
        records = ta.aggregate()
        assert records == []

    def test_aggregate_evidence_trace(self) -> None:
        ta = TraceAggregator()
        records = ta.aggregate(
            evidence_trace=[
                {"stage_name": "COLLECT", "operation": "collect", "explanation_id": "exp-1", "success": True},
            ],
            correlation_id="corr-1",
        )
        assert len(records) == 1
        assert records[0].stage_name == "COLLECT"
        assert records[0].metadata.get("source") == "evidence"

    def test_aggregate_reasoning_trace(self) -> None:
        ta = TraceAggregator()
        records = ta.aggregate(
            reasoning_trace=[
                {"stage_name": "INFER", "operation": "infer", "explanation_id": "exp-1", "success": True},
            ],
        )
        assert len(records) == 1
        assert records[0].stage_name == "INFER"
        assert records[0].metadata.get("source") == "reasoning"

    def test_aggregate_recommendation_trace(self) -> None:
        ta = TraceAggregator()
        records = ta.aggregate(
            recommendation_trace=[
                {"stage_name": "RANK", "operation": "rank", "explanation_id": "exp-1", "success": True},
            ],
        )
        assert len(records) == 1
        assert records[0].stage_name == "RANK"
        assert records[0].metadata.get("source") == "recommendation"

    def test_aggregate_all_sources(self) -> None:
        ta = TraceAggregator()
        records = ta.aggregate(
            evidence_trace=[{"stage_name": "COLLECT", "operation": "collect"}],
            reasoning_trace=[{"stage_name": "INFER", "operation": "infer"}],
            recommendation_trace=[{"stage_name": "RANK", "operation": "rank"}],
        )
        assert len(records) == 3

    def test_merge_traces(self) -> None:
        ta = TraceAggregator()
        records = ta.merge_traces([
            {"stage_name": "STAGE_1", "operation": "op1", "source": "evidence", "success": True},
            {"stage_name": "STAGE_2", "operation": "op2", "source": "reasoning", "success": False, "errors": ["err"]},
        ])
        assert len(records) == 2
        assert records[0].stage_name == "STAGE_1"
        assert not records[1].success
        assert records[1].errors == ["err"]

    def test_get_by_stage(self) -> None:
        ta = TraceAggregator()
        ta.aggregate(evidence_trace=[{"stage_name": "COLLECT", "operation": "collect"}])
        ta.aggregate(reasoning_trace=[{"stage_name": "INFER", "operation": "infer"}])
        ta.aggregate(reasoning_trace=[{"stage_name": "INFER", "operation": "infer2"}])
        records = ta.get_by_stage("INFER")
        assert len(records) == 2

    def test_get_by_source(self) -> None:
        ta = TraceAggregator()
        ta.aggregate(evidence_trace=[{"stage_name": "COLLECT", "operation": "collect"}])
        ta.aggregate(reasoning_trace=[{"stage_name": "INFER", "operation": "infer"}])
        evidence_records = ta.get_by_source("evidence")
        reasoning_records = ta.get_by_source("reasoning")
        assert len(evidence_records) == 1
        assert len(reasoning_records) == 1

    def test_get_all(self) -> None:
        ta = TraceAggregator()
        assert ta.get_all() == []
        ta.aggregate(evidence_trace=[{"stage_name": "COLLECT", "operation": "collect"}])
        assert len(ta.get_all()) == 1

    def test_clear(self) -> None:
        ta = TraceAggregator()
        ta.aggregate(evidence_trace=[{"stage_name": "COLLECT", "operation": "collect"}])
        assert ta.count() == 1
        ta.clear()
        assert ta.count() == 0

    def test_count(self) -> None:
        ta = TraceAggregator()
        assert ta.count() == 0
        ta.aggregate(evidence_trace=[{"stage_name": "COLLECT", "operation": "collect"}])
        assert ta.count() == 1
        ta.aggregate(reasoning_trace=[{"stage_name": "INFER", "operation": "infer"}])
        assert ta.count() == 2


# =============================================================================
# 7. ExplanationSections
# =============================================================================


class TestExplanationSections:
    def _make_package(self) -> ExplanationPackage:
        rid = uuid.uuid4()
        narrative = ExplanationNarrative(
            package_id=rid,
            title="Primary Narrative",
            content="Primary content body",
            summary="Primary summary",
            audience=ExplanationLayer.EXECUTIVE,
        )
        return ExplanationPackage(
            result_id=rid,
            primary_narrative=narrative,
        )

    def test_build_eight_sections(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert len(sections) == 8

    def test_section_ordering(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        expected_types = ["summary", "evidence", "reasoning", "recommendation",
                          "alternatives", "risks", "confidence", "references"]
        for i, section in enumerate(sections):
            assert section.section_type == expected_types[i]
            assert section.order == i

    def test_summary_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[0].title == "Summary"
        assert sections[0].content == "Primary content body"

    def test_evidence_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[1].title == "Evidence"
        assert "evidence citations" in sections[1].content

    def test_reasoning_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[2].title == "Reasoning"

    def test_recommendation_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[3].title == "Recommendation"

    def test_alternatives_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[4].title == "Alternatives"

    def test_risks_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[5].title == "Risks"

    def test_confidence_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[6].title == "Confidence"
        assert "0.00" in sections[6].content

    def test_references_section(self) -> None:
        es = ExplanationSections()
        package = self._make_package()
        sections = es.build(package)
        assert sections[7].title == "References"

    def test_build_with_citations(self) -> None:
        rid = uuid.uuid4()
        nid = uuid.uuid4()
        narrative = ExplanationNarrative(
            package_id=rid,
            title="Narrative",
            content="Content",
            audience=ExplanationLayer.EXECUTIVE,
        )
        citation = ExplanationCitation(
            narrative_id=nid,
            citation_type=CitationType.EVIDENCE,
            source_id="ev-1",
        )
        package = ExplanationPackage(
            result_id=rid,
            primary_narrative=narrative,
            evidence_citations=[citation],
        )
        es = ExplanationSections()
        sections = es.build(package)
        assert len(sections[1].citations) == 1
        assert sections[7].content != "No references available."


# =============================================================================
# 8. ExplanationQualityManager
# =============================================================================


class TestExplanationQualityManager:
    def test_evaluate_with_package_and_citations(self) -> None:
        eqm = ExplanationQualityManager()
        rid = uuid.uuid4()
        narrative = ExplanationNarrative(
            package_id=rid,
            title="Test",
            content="Content",
            audience=ExplanationLayer.EXECUTIVE,
        )
        package = ExplanationPackage(
            result_id=rid,
            primary_narrative=narrative,
        )
        citations = [
            ExplanationCitation(narrative_id=uuid.uuid4(), citation_type=CitationType.EVIDENCE)
            for _ in range(3)
        ]
        traces = [
            TraceRecord(stage_name="NARRATIVE", operation="build"),
            TraceRecord(stage_name="CITATION", operation="build"),
        ]
        score = eqm.evaluate(package=package, citations=citations, traces=traces)
        assert isinstance(score, QualityScore)
        assert score.completeness == 0.8
        assert score.citation_coverage == 0.6  # min(1.0, 3/5)
        assert score.trace_coverage == round(2.0 / 3.0, 4)
        assert score.readability == 0.7
        assert score.consistency == 0.8

    def test_evaluate_empty_citations(self) -> None:
        eqm = ExplanationQualityManager()
        rid = uuid.uuid4()
        package = ExplanationPackage(result_id=rid)
        score = eqm.evaluate(package=package, citations=[], traces=[])
        assert score.citation_coverage == 0.0
        assert score.trace_coverage == 0.0
        assert score.consistency == 0.0

    def test_evaluate_no_package(self) -> None:
        eqm = ExplanationQualityManager()
        score = eqm.evaluate(package=None, citations=[], traces=[])
        assert score.completeness == 0.0
        assert score.consistency == 0.0

    def test_evaluate_with_correlation_id(self) -> None:
        eqm = ExplanationQualityManager()
        score = eqm.evaluate(package=None, citations=[], traces=[], correlation_id="corr-1")
        assert score.metadata.get("correlation_id") == "corr-1"

    def test_overall_score_formula(self) -> None:
        eqm = ExplanationQualityManager()
        rid = uuid.uuid4()
        narrative = ExplanationNarrative(
            package_id=rid,
            title="Test",
            content="Content",
            audience=ExplanationLayer.EXECUTIVE,
        )
        package = ExplanationPackage(
            result_id=rid,
            primary_narrative=narrative,
        )
        citations = [
            ExplanationCitation(narrative_id=uuid.uuid4(), citation_type=CitationType.EVIDENCE)
            for _ in range(5)
        ]
        traces = [
            TraceRecord(stage_name="NARRATIVE", operation="build")
            for _ in range(3)
        ]
        score = eqm.evaluate(package=package, citations=citations, traces=traces)
        expected = round(
            0.20 * 0.8 + 0.15 * 1.0 + 0.10 * 1.0 + 0.15 * 0.7 + 0.15 * 0.8 + 0.15 * 0.7 + 0.10 * 1.0, 4
        )
        assert score.overall == expected


# =============================================================================
# 9. TimelineBuilder
# =============================================================================


class TestTimelineBuilder:
    def test_build_creates_timeline(self) -> None:
        tb = TimelineBuilder()
        request = ExplanationRequest()
        narratives = [
            ExplanationNarrative(
                package_id=request.request_id,
                title="Narrative 1",
                content="Content",
                audience=ExplanationLayer.EXECUTIVE,
            ),
        ]
        citations = [
            ExplanationCitation(
                narrative_id=narratives[0].narrative_id,
                citation_type=CitationType.EVIDENCE,
            ),
        ]
        timeline = tb.build(
            request=request,
            narratives=narratives,
            citations=citations,
            correlation_id="corr-1",
        )
        assert isinstance(timeline, ExplanationTimeline)
        assert timeline.explanation_id == str(request.request_id)
        assert len(timeline.events) == 1 + len(narratives) + len(citations)
        assert timeline.events[0]["event_type"] == "request_created"
        assert timeline.events[1]["event_type"] == "narrative_created"
        assert timeline.events[2]["event_type"] == "citation_created"

    def test_timeline_has_start_end_times(self) -> None:
        tb = TimelineBuilder()
        request = ExplanationRequest()
        timeline = tb.build(
            request=request,
            narratives=[],
            citations=[],
        )
        assert isinstance(timeline.start_time, datetime)
        assert isinstance(timeline.end_time, datetime)
        assert timeline.total_duration_ms >= 0.0

    def test_timeline_with_multiple_events(self) -> None:
        tb = TimelineBuilder()
        request = ExplanationRequest()
        narratives = [
            ExplanationNarrative(package_id=request.request_id, title=f"N {i}", content="C", audience=ExplanationLayer.ENGINEER)
            for i in range(3)
        ]
        citations = [
            ExplanationCitation(narrative_id=narratives[0].narrative_id, citation_type=CitationType.EVIDENCE)
            for _ in range(2)
        ]
        timeline = tb.build(request=request, narratives=narratives, citations=citations)
        assert len(timeline.events) == 1 + 3 + 2

    def test_timeline_metadata(self) -> None:
        tb = TimelineBuilder()
        request = ExplanationRequest()
        timeline = tb.build(
            request=request,
            narratives=[],
            citations=[],
            correlation_id="corr-1",
        )
        assert timeline.metadata.get("correlation_id") == "corr-1"


# =============================================================================
# 10. TemplateManager
# =============================================================================


class TestTemplateManager:
    def test_get_template_executive(self) -> None:
        tm = TemplateManager()
        template = tm.get_template("executive")
        assert template is not None
        assert template.template_type == "executive"
        assert template.name == "Executive Briefing"
        assert template.audience == "EXECUTIVE"
        assert "summary" in template.sections

    def test_get_template_technical(self) -> None:
        tm = TemplateManager()
        template = tm.get_template("technical")
        assert template is not None
        assert template.template_type == "technical"
        assert template.name == "Technical Deep Dive"
        assert template.audience == "ENGINEER"

    def test_get_template_audit(self) -> None:
        tm = TemplateManager()
        template = tm.get_template("audit")
        assert template is not None
        assert template.template_type == "audit"
        assert template.name == "Audit Report"
        assert template.audience == "AUDITOR"

    def test_get_template_incident(self) -> None:
        tm = TemplateManager()
        template = tm.get_template("incident")
        assert template is not None
        assert template.template_type == "incident"
        assert template.name == "Incident Report"
        assert template.audience == "OPERATOR"

    def test_get_template_compliance(self) -> None:
        tm = TemplateManager()
        template = tm.get_template("compliance")
        assert template is not None
        assert template.template_type == "compliance"
        assert template.name == "Compliance Summary"
        assert template.audience == "MANAGER"

    def test_get_template_unknown(self) -> None:
        tm = TemplateManager()
        template = tm.get_template("unknown_type")
        assert template is None

    def test_list_templates(self) -> None:
        tm = TemplateManager()
        templates = tm.list_templates()
        assert len(templates) == 5
        types = {t.template_type for t in templates}
        assert types == {"executive", "technical", "audit", "incident", "compliance"}

    def test_register_template(self) -> None:
        tm = TemplateManager()
        assert tm.count() == 5
        new_template = NarrativeTemplate(
            template_type="custom",
            name="Custom Report",
            sections=["summary"],
            audience="EXECUTIVE",
        )
        tm.register_template(new_template)
        assert tm.count() == 6
        retrieved = tm.get_template("custom")
        assert retrieved is not None
        assert retrieved.name == "Custom Report"

    def test_remove_template(self) -> None:
        tm = TemplateManager()
        assert tm.count() == 5
        template = tm.get_template("executive")
        assert template is not None
        tm.remove_template(template.template_id)
        assert tm.count() == 4
        assert tm.get_template("executive") is None

    def test_clear(self) -> None:
        tm = TemplateManager()
        assert tm.count() > 0
        tm.clear()
        assert tm.count() == 0

    def test_count(self) -> None:
        tm = TemplateManager()
        assert tm.count() == 5


# =============================================================================
# 11. PolicyEngine
# =============================================================================


class TestPolicyEngine:
    def test_check_policy_summary_allowed(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="SUMMARY",
            audience="EXECUTIVE",
            narrative_count=1,
            has_citations=False,
            has_trace=False,
        )
        assert violations == []

    def test_check_policy_summary_exceeds_narratives(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="SUMMARY",
            audience="EXECUTIVE",
            narrative_count=2,
            has_citations=False,
            has_trace=False,
        )
        assert len(violations) == 1
        assert "exceeds" in violations[0]

    def test_check_policy_summary_wrong_audience(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="SUMMARY",
            audience="ENGINEER",
            narrative_count=1,
            has_citations=False,
            has_trace=False,
        )
        assert len(violations) == 1
        assert "not allowed" in violations[0]

    def test_check_policy_standard_allowed(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="STANDARD",
            audience="ENGINEER",
            narrative_count=3,
            has_citations=False,
            has_trace=False,
        )
        assert violations == []

    def test_check_policy_full_requires_citations_and_trace(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="FULL",
            audience="ENGINEER",
            narrative_count=5,
            has_citations=False,
            has_trace=False,
        )
        assert len(violations) == 2
        assert any("citations" in v for v in violations)
        assert any("trace" in v for v in violations)

    def test_check_policy_full_passes_with_citations_and_trace(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="FULL",
            audience="ENGINEER",
            narrative_count=5,
            has_citations=True,
            has_trace=True,
        )
        assert violations == []

    def test_check_policy_audit_requires_citations_and_trace(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="AUDIT",
            audience="AUDITOR",
            narrative_count=5,
            has_citations=False,
            has_trace=False,
        )
        assert len(violations) == 2

    def test_check_policy_audit_passes(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="AUDIT",
            audience="AUDITOR",
            narrative_count=5,
            has_citations=True,
            has_trace=True,
        )
        assert violations == []

    def test_check_policy_confidential(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="CONFIDENTIAL",
            audience="EXECUTIVE",
            narrative_count=2,
            has_citations=True,
            has_trace=False,
        )
        assert violations == []

    def test_check_policy_confidential_exceeds_max(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="CONFIDENTIAL",
            audience="EXECUTIVE",
            narrative_count=5,
            has_citations=True,
            has_trace=False,
        )
        assert len(violations) == 1
        assert "exceeds" in violations[0]

    def test_check_policy_unknown_type(self) -> None:
        pe = PolicyEngine()
        violations = pe.check_policy(
            policy_type="UNKNOWN",
            audience="EXECUTIVE",
            narrative_count=1,
            has_citations=False,
            has_trace=False,
        )
        assert len(violations) == 1
        assert "No policy found" in violations[0]

    def test_get_policy(self) -> None:
        pe = PolicyEngine()
        policy = pe.get_policy("SUMMARY")
        assert policy is not None
        assert policy.policy_type == "SUMMARY"
        assert policy.name == "Summary Policy"

    def test_get_policy_not_found(self) -> None:
        pe = PolicyEngine()
        assert pe.get_policy("UNKNOWN") is None

    def test_list_policies(self) -> None:
        pe = PolicyEngine()
        policies = pe.list_policies()
        assert len(policies) == 5
        types = {p.policy_type for p in policies}
        assert types == {"SUMMARY", "STANDARD", "FULL", "AUDIT", "CONFIDENTIAL"}


# =============================================================================
# 12. ExplainabilityTrace
# =============================================================================


class TestExplainabilityTrace:
    def test_record_event(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_event(stage_name="TEST", operation="test_op")
        assert isinstance(record, TraceRecord)
        assert record.stage_name == "TEST"
        assert record.operation == "test_op"
        assert record.success is True

    def test_record_event_with_warnings_and_errors(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_event(
            stage_name="TEST",
            operation="test_op",
            success=False,
            warnings=["Warning 1"],
            errors=["Error 1"],
            duration_ms=50.0,
        )
        assert record.success is False
        assert record.warnings == ["Warning 1"]
        assert record.errors == ["Error 1"]
        assert record.duration_ms == 50.0

    def test_record_narrative_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_narrative_stage(explanation_id="exp-1", correlation_id="corr-1", duration_ms=30.0)
        assert record.stage_name == "NARRATIVE"
        assert record.operation == "build"
        assert record.explanation_id == "exp-1"
        assert record.correlation_id == "corr-1"
        assert record.duration_ms == 30.0

    def test_record_citation_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_citation_stage(explanation_id="exp-1", duration_ms=20.0)
        assert record.stage_name == "CITATION"
        assert record.operation == "build"
        assert record.duration_ms == 20.0

    def test_record_formatting_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_formatting_stage(explanation_id="exp-1")
        assert record.stage_name == "FORMATTING"
        assert record.operation == "format"

    def test_record_timeline_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_timeline_stage(explanation_id="exp-1")
        assert record.stage_name == "TIMELINE"
        assert record.operation == "build"

    def test_record_template_stage(self) -> None:
        t = ExplainabilityTrace()
        record = t.record_template_stage(explanation_id="exp-1")
        assert record.stage_name == "TEMPLATE"
        assert record.operation == "select"

    def test_get_by_explanation_id(self) -> None:
        t = ExplainabilityTrace()
        t.record_narrative_stage(explanation_id="exp-1")
        t.record_citation_stage(explanation_id="exp-1")
        t.record_formatting_stage(explanation_id="exp-2")
        records = t.get_by_explanation_id("exp-1")
        assert len(records) == 2

    def test_get_by_stage(self) -> None:
        t = ExplainabilityTrace()
        t.record_narrative_stage(explanation_id="exp-1")
        t.record_narrative_stage(explanation_id="exp-2")
        t.record_citation_stage(explanation_id="exp-1")
        records = t.get_by_stage("NARRATIVE")
        assert len(records) == 2

    def test_get_recent(self) -> None:
        t = ExplainabilityTrace()
        for i in range(15):
            t.record_event(stage_name=f"stage-{i}", operation="test")
        recent = t.get_recent(5)
        assert len(recent) == 5

    def test_get_recent_empty(self) -> None:
        t = ExplainabilityTrace()
        assert t.get_recent(5) == []

    def test_clear(self) -> None:
        t = ExplainabilityTrace()
        t.record_narrative_stage(explanation_id="exp-1")
        assert t.count() == 1
        t.clear()
        assert t.count() == 0

    def test_count(self) -> None:
        t = ExplainabilityTrace()
        assert t.count() == 0
        t.record_narrative_stage(explanation_id="exp-1")
        assert t.count() == 1
        t.record_citation_stage(explanation_id="exp-1")
        assert t.count() == 2


# =============================================================================
# 13. ExplainabilityMetricsCollector
# =============================================================================


class TestExplainabilityMetricsCollector:
    def test_initial_state(self) -> None:
        mc = ExplainabilityMetricsCollector()
        snap = mc.snapshot()
        assert snap.explanations_total == 0
        assert snap.narratives_total == 0
        assert snap.citations_total == 0
        assert snap.audience_distribution == {}
        assert snap.template_usage == {}
        assert snap.average_quality == 0.0
        assert snap.average_completeness == 0.0

    def test_increment_explanations(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_explanations(5)
        assert mc.snapshot().explanations_total == 5

    def test_increment_narratives(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_narratives(10)
        assert mc.snapshot().narratives_total == 10

    def test_increment_citations(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_citations(20)
        assert mc.snapshot().citations_total == 20

    def test_increment_multiple_times(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_explanations(3)
        mc.increment_explanations(4)
        assert mc.snapshot().explanations_total == 7
        mc.increment_narratives(5)
        mc.increment_narratives(5)
        assert mc.snapshot().narratives_total == 10

    def test_record_audience(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.record_audience("EXECUTIVE")
        mc.record_audience("EXECUTIVE")
        mc.record_audience("ENGINEER")
        snap = mc.snapshot()
        assert snap.audience_distribution["EXECUTIVE"] == 2
        assert snap.audience_distribution["ENGINEER"] == 1

    def test_record_template(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.record_template("executive")
        mc.record_template("technical")
        mc.record_template("executive")
        snap = mc.snapshot()
        assert snap.template_usage["executive"] == 2
        assert snap.template_usage["technical"] == 1

    def test_record_quality(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.record_quality(0.85)
        mc.record_quality(0.75)
        snap = mc.snapshot()
        assert snap.average_quality == 0.8
        assert snap.average_completeness == 0.8

    def test_record_quality_single(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.record_quality(0.9)
        snap = mc.snapshot()
        assert snap.average_quality == 0.9

    def test_record_quality_clamped(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.record_quality(1.5)
        assert mc.snapshot().average_quality == 1.0
        mc.reset()
        mc.record_quality(-0.5)
        assert mc.snapshot().average_quality == 0.0

    def test_increment_negative_clamped(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_explanations(-5)
        assert mc.snapshot().explanations_total == 0
        mc.increment_narratives(-3)
        assert mc.snapshot().narratives_total == 0

    def test_snapshot_type(self) -> None:
        mc = ExplainabilityMetricsCollector()
        snap = mc.snapshot()
        assert isinstance(snap, ExplainabilityMetrics)

    def test_snapshot_includes_all_fields(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_explanations(5)
        mc.increment_narratives(10)
        mc.increment_citations(20)
        mc.record_audience("EXECUTIVE")
        mc.record_template("executive")
        mc.record_quality(0.85)
        snap = mc.snapshot()
        assert snap.explanations_total == 5
        assert snap.narratives_total == 10
        assert snap.citations_total == 20
        assert snap.audience_distribution.get("EXECUTIVE") == 1
        assert snap.template_usage.get("executive") == 1
        assert snap.average_quality == 0.85
        assert snap.metrics_id is not None

    def test_reset(self) -> None:
        mc = ExplainabilityMetricsCollector()
        mc.increment_explanations(10)
        mc.increment_narratives(20)
        mc.record_audience("EXECUTIVE")
        mc.record_template("executive")
        mc.record_quality(0.9)
        mc.reset()
        snap = mc.snapshot()
        assert snap.explanations_total == 0
        assert snap.narratives_total == 0
        assert snap.citations_total == 0
        assert snap.audience_distribution == {}
        assert snap.template_usage == {}
        assert snap.average_quality == 0.0
