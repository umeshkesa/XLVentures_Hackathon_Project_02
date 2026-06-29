"""ExplainabilityCoordinatorImpl — orchestrates the explanation pipeline.

Coordinates the full explanation pipeline by delegating to
Phase 2 execution components and Phase 3 orchestration components.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.explainability.contracts.models import (
    ExplanationContext,
    ExplanationDecision,
    ExplanationHealth,
    ExplanationMetrics,
    ExplanationRequest,
    ExplanationResult,
)
from adip.explainability.enums import (
    ExplanationLayer,
    ExplanationStatus,
)
from adip.explainability.execution.audience_formatter import AudienceFormatter
from adip.explainability.execution.builder import ExplanationBuilder
from adip.explainability.execution.citation_manager import CitationManager
from adip.explainability.execution.metrics import ExplainabilityMetricsCollector
from adip.explainability.execution.models import TraceRecord
from adip.explainability.execution.narrative_builder import NarrativeBuilder
from adip.explainability.execution.policy_engine import PolicyEngine
from adip.explainability.execution.quality_manager import ExplanationQualityManager
from adip.explainability.execution.sections import ExplanationSections
from adip.explainability.execution.template_manager import TemplateManager
from adip.explainability.execution.timeline_builder import TimelineBuilder
from adip.explainability.execution.trace import ExplainabilityTrace
from adip.explainability.orchestration.audit_package import ExplanationAuditPackage
from adip.explainability.orchestration.compliance import ExplanationCompliance
from adip.explainability.orchestration.confidence import ExplanationConfidenceCalculator
from adip.explainability.orchestration.export_profiles import ExplanationExportProfiles
from adip.explainability.orchestration.justification import ExplanationJustification
from adip.explainability.orchestration.lineage import ExplanationLineage
from adip.explainability.orchestration.readiness import ExplanationReadiness
from adip.explainability.orchestration.review import ExplanationReview
from adip.explainability.orchestration.session import ExplanationSessionManager
from adip.explainability.orchestration.snapshot import ExplanationSnapshot
from adip.explainability.orchestration.version_manager import ExplanationVersionManager

log = structlog.get_logger(__name__)


class TraceAggregator:
    """Aggregates trace records for an explanation operation.

    Wraps ExplainabilityTrace to provide trace record aggregation
    by explanation identifier.
    """

    def __init__(self, trace: ExplainabilityTrace) -> None:
        self._trace = trace

    def get_traces(self, explanation_id: str) -> list[TraceRecord]:
        """Get all trace records for an explanation ID.

        Args:
            explanation_id: The explanation identifier.

        Returns:
            List of matching TraceRecord instances.
        """
        return self._trace.get_by_explanation_id(explanation_id)

    def count(self, explanation_id: str) -> int:
        """Get the number of trace records for an explanation ID.

        Args:
            explanation_id: The explanation identifier.

        Returns:
            The number of trace records.
        """
        return len(self._trace.get_by_explanation_id(explanation_id))


class ExplainabilityCoordinatorImpl:
    """Orchestrates the full explanation pipeline.

    Coordinates session, validation, timeline, narrative, formatting,
    citation, package, section, quality, confidence, policy, and
    trace stages for explanation operations.
    """

    def __init__(
        self,
        narrative_builder: NarrativeBuilder | None = None,
        audience_formatter: AudienceFormatter | None = None,
        citation_manager: CitationManager | None = None,
        explanation_builder: ExplanationBuilder | None = None,
        trace_aggregator: TraceAggregator | None = None,
        sections: ExplanationSections | None = None,
        quality_manager: ExplanationQualityManager | None = None,
        timeline_builder: TimelineBuilder | None = None,
        template_manager: TemplateManager | None = None,
        policy_engine: PolicyEngine | None = None,
        trace: ExplainabilityTrace | None = None,
        metrics_collector: ExplainabilityMetricsCollector | None = None,
        session_manager: ExplanationSessionManager | None = None,
        confidence_calculator: ExplanationConfidenceCalculator | None = None,
        review: ExplanationReview | None = None,
        version_manager: ExplanationVersionManager | None = None,
        readiness: ExplanationReadiness | None = None,
        lineage: ExplanationLineage | None = None,
        snapshot: ExplanationSnapshot | None = None,
        justification: ExplanationJustification | None = None,
        compliance: ExplanationCompliance | None = None,
        audit_package: ExplanationAuditPackage | None = None,
        export_profiles: ExplanationExportProfiles | None = None,
    ) -> None:
        self.narrative_builder = narrative_builder or NarrativeBuilder()
        self.audience_formatter = audience_formatter or AudienceFormatter()
        self.citation_manager = citation_manager or CitationManager()
        self.explanation_builder = explanation_builder or ExplanationBuilder()
        self.trace = trace or ExplainabilityTrace()
        self.trace_aggregator = trace_aggregator or TraceAggregator(self.trace)
        self.sections = sections or ExplanationSections()
        self.quality_manager = quality_manager or ExplanationQualityManager()
        self.timeline_builder = timeline_builder or TimelineBuilder()
        self.template_manager = template_manager or TemplateManager()
        self.policy_engine = policy_engine or PolicyEngine()
        self.metrics_collector = metrics_collector or ExplainabilityMetricsCollector()
        self.session_manager = session_manager or ExplanationSessionManager()
        self.confidence_calculator = confidence_calculator or ExplanationConfidenceCalculator()
        self.review = review or ExplanationReview()
        self.version_manager = version_manager or ExplanationVersionManager()
        self.readiness = readiness or ExplanationReadiness()
        self.lineage = lineage or ExplanationLineage()
        self.snapshot = snapshot or ExplanationSnapshot()
        self._justification = justification or ExplanationJustification()
        self._compliance = compliance or ExplanationCompliance()
        self._audit_package = audit_package or ExplanationAuditPackage()
        self._export_profiles = export_profiles or ExplanationExportProfiles()

    def explain(
        self,
        request: ExplanationRequest,
        correlation_id: str = "",
    ) -> ExplanationResult:
        """Execute a full explanation pipeline.

        24-stage pipeline:
        1. Create session (INITIALIZED)
        2. Validate request via policy_engine
        3. Update session to COLLECTING
        4. Build timelines
        5. Build narratives
        6. Format narratives for audiences
        7. Build citations
        8. Update session to BUILDING
        9. Build explanation package
        10. Build sections
        11. Calculate quality
        12. Calculate confidence
        13. Review (narratives, citations, policies)
        14. Versioning (create version)
        15. Readiness (assess)
        16. Lineage (record evidence, reasoning, recommendation)
        17. Snapshot (create snapshot)
        18. Justification (record narrative, citation, template, audience, policy justifications)
        19. Compliance (assess compliance)
        20. Audit (create audit package)
        21. Export (generate export profiles)
        22. Check for policy violations against result
        23. Build decision
        24. Update session to COMPLETED

        Args:
            request: The explanation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The explanation result with package, confidence, quality, and session.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("coordinator.explain.start", request_id=str(request.request_id), cid=cid)

        result = ExplanationResult(
            request_id=request.request_id,
            status=ExplanationStatus.INITIALIZED,
        )

        context = ExplanationContext(
            reasoning_context=request.context or {},
            evidence_context={},
            recommendation_context={},
            metadata={"request_id": str(request.request_id), "correlation_id": cid},
        )

        session = self.session_manager.create_session(context, correlation_id=cid)

        try:
            rid = str(request.request_id)

            # Stage 1: Tracing — INITIALIZED
            self.trace.record_event(
                stage_name="INITIALIZED",
                operation="create_session",
                explanation_id=rid,
                correlation_id=cid,
            )

            # Stage 2: Validate request via policy_engine
            self.trace.record_event(
                stage_name="VALIDATION",
                operation="validate",
                explanation_id=rid,
                correlation_id=cid,
            )
            policy_type = request.metadata.get("policy_type", "STANDARD")
            default_audience = request.target_audiences[0].value if request.target_audiences else "ENGINEER"
            violations = self.policy_engine.check_policy(
                policy_type=policy_type,
                audience=default_audience,
                narrative_count=0,
                has_citations=False,
                has_trace=False,
            )
            log.info("coordinator.validation", policy_type=policy_type, violations=len(violations))

            # Stage 3: Update session to COLLECTING
            self.trace.record_event(
                stage_name="COLLECTING",
                operation="update_status",
                explanation_id=rid,
                correlation_id=cid,
            )
            self.session_manager.update_status(str(session.session_id), ExplanationStatus.COLLECTING)

            # Stage 4: Build timelines
            self.trace.record_timeline_stage(explanation_id=rid, correlation_id=cid)
            audiences = request.target_audiences or [ExplanationLayer.ENGINEER]

            # Build narratives first to pass to timeline
            narratives = self.narrative_builder.build_narratives(
                audiences=audiences,
                correlation_id=cid,
            )
            self.metrics_collector.increment_narratives(len(narratives))
            for n in narratives:
                self.session_manager.add_narrative(str(session.session_id), str(n.narrative_id))
                self.metrics_collector.record_audience(n.audience.value)

            timeline = self.timeline_builder.build(
                request=request,
                narratives=narratives,
                citations=[],
                correlation_id=cid,
            )
            log.info("coordinator.timeline", events=len(timeline.events))

            # Stage 5: Build narratives (already done above for timeline input)
            self.trace.record_narrative_stage(explanation_id=rid, correlation_id=cid)
            log.info("coordinator.narratives", count=len(narratives))

            # Stage 6: Format narratives for audiences
            self.trace.record_formatting_stage(explanation_id=rid, correlation_id=cid)
            formatted_narratives: list[Any] = []
            for narrative in narratives:
                formatted = self.audience_formatter.format(
                    narrative=narrative,
                    audience=narrative.audience,
                    correlation_id=cid,
                )
                formatted_narratives.append(formatted)
            log.info("coordinator.formatting", count=len(formatted_narratives))

            # Stage 7: Build citations
            self.trace.record_citation_stage(explanation_id=rid, correlation_id=cid)
            all_citations: list[Any] = []
            for narrative in formatted_narratives:
                citations = self.citation_manager.build_citations(
                    narrative_id=str(narrative.narrative_id),
                    evidence_ids=[str(request.evidence_result_id)] if request.evidence_result_id else None,
                    reasoning_ids=[str(request.reasoning_result_id)] if request.reasoning_result_id else None,
                    recommendation_ids=[str(request.recommendation_result_id)] if request.recommendation_result_id else None,
                    correlation_id=cid,
                )
                for c in citations:
                    self.session_manager.add_citation(str(session.session_id), str(c.citation_id))
                all_citations.extend(citations)
            self.metrics_collector.increment_citations(len(all_citations))
            log.info("coordinator.citations", count=len(all_citations))

            # Stage 8: Update session to BUILDING
            self.trace.record_event(
                stage_name="BUILDING",
                operation="update_status",
                explanation_id=rid,
                correlation_id=cid,
            )
            self.session_manager.update_status(str(session.session_id), ExplanationStatus.BUILDING)

            # Stage 9: Build explanation package
            self.trace.record_event(
                stage_name="PACKAGE",
                operation="build",
                explanation_id=rid,
                correlation_id=cid,
            )
            package = self.explanation_builder.build(
                request=request,
                narratives=formatted_narratives,
                citations=all_citations,
                correlation_id=cid,
            )
            self.metrics_collector.increment_explanations()
            log.info("coordinator.package", package_id=str(package.package_id))

            # Stage 10: Build sections
            self.trace.record_event(
                stage_name="SECTIONS",
                operation="build",
                explanation_id=rid,
                correlation_id=cid,
            )
            built_sections = self.explanation_builder.build_sections(
                narratives=formatted_narratives,
                citations=all_citations,
                correlation_id=cid,
            )
            log.info("coordinator.sections", count=len(built_sections))

            # Stage 11: Calculate quality
            self.trace.record_event(
                stage_name="QUALITY",
                operation="evaluate",
                explanation_id=rid,
                correlation_id=cid,
            )
            expl_traces = self.trace_aggregator.get_traces(rid)
            quality = self.quality_manager.evaluate(
                package=package,
                citations=all_citations,
                traces=expl_traces,
                correlation_id=cid,
            )
            self.metrics_collector.record_quality(quality.overall)
            log.info("coordinator.quality", overall=quality.overall)

            # Stage 12: Calculate confidence
            self.trace.record_event(
                stage_name="CONFIDENCE",
                operation="calculate",
                explanation_id=rid,
                correlation_id=cid,
            )
            confidence = self.confidence_calculator.calculate(
                package=package,
                quality=quality,
                correlation_id=cid,
            )
            self.metrics_collector.record_confidence(confidence.overall_confidence)
            log.info("coordinator.confidence", overall=confidence.overall_confidence)

            # Stage 13: Review — run ExplanationReview.review()
            self.trace.record_event(
                stage_name="REVIEW",
                operation="review",
                explanation_id=rid,
                correlation_id=cid,
            )
            review_results = self.review.review(
                package=package,
                narratives=formatted_narratives,
                citations=all_citations,
                policies=[self.policy_engine._policies.get(policy_type, {})] if hasattr(self.policy_engine, '_policies') else [],
                correlation_id=cid,
            )
            self.metrics_collector.increment_reviews()
            total_review_warnings = sum(len(v) for v in review_results.values())
            log.info("coordinator.review", total_warnings=total_review_warnings)

            # Stage 14: Versioning — create version
            self.trace.record_event(
                stage_name="VERSIONING",
                operation="create_version",
                explanation_id=rid,
                correlation_id=cid,
            )
            version = self.version_manager.create_version(
                explanation_id=rid,
                narratives=formatted_narratives,
                citations=all_citations,
                trace=expl_traces,
                correlation_id=cid,
            )
            self.metrics_collector.increment_versions()
            log.info("coordinator.version", version_number=version["version_number"])

            # Stage 15: Readiness — assess
            self.trace.record_event(
                stage_name="READINESS",
                operation="assess",
                explanation_id=rid,
                correlation_id=cid,
            )
            readiness_status = self.readiness.assess(
                confidence_score=confidence.overall_confidence,
                quality_score=quality.overall,
                review_results=review_results,
                correlation_id=cid,
            )
            self.metrics_collector.increment_readiness(readiness_status)
            log.info("coordinator.readiness", status=readiness_status)

            # Stage 16: Lineage — record entries
            self.trace.record_event(
                stage_name="LINEAGE",
                operation="record",
                explanation_id=rid,
                correlation_id=cid,
            )
            lineage_entries: list[dict[str, Any]] = []
            if request.reasoning_result_id:
                entry = self.lineage.record_reasoning(
                    source_id=str(request.reasoning_result_id),
                    explanation_id=rid,
                    correlation_id=cid,
                )
                lineage_entries.append(entry)
            if request.evidence_result_id:
                entry = self.lineage.record_evidence(
                    source_id=str(request.evidence_result_id),
                    explanation_id=rid,
                    correlation_id=cid,
                )
                lineage_entries.append(entry)
            if request.recommendation_result_id:
                entry = self.lineage.record_recommendation(
                    source_id=str(request.recommendation_result_id),
                    explanation_id=rid,
                    correlation_id=cid,
                )
                lineage_entries.append(entry)
            self.metrics_collector.increment_lineage_entries(len(lineage_entries))
            log.info("coordinator.lineage", count=len(lineage_entries))

            # Stage 17: Snapshot — create snapshot
            self.trace.record_event(
                stage_name="SNAPSHOT",
                operation="create",
                explanation_id=rid,
                correlation_id=cid,
            )
            snapshot_record = self.snapshot.create(
                package=package,
                narratives=formatted_narratives,
                citations=all_citations,
                trace=expl_traces,
                timeline=timeline,
                correlation_id=cid,
            )
            self.metrics_collector.increment_snapshots()
            log.info("coordinator.snapshot", snapshot_id=snapshot_record["snapshot_id"])

            # Stage 18: Justification — record narrative/citation/template/audience/policy justifications
            self.trace.record_event(
                stage_name="JUSTIFICATION",
                operation="justify",
                explanation_id=rid,
                correlation_id=cid,
            )
            for narrative in formatted_narratives:
                self._justification.record_narrative_justification(
                    narrative_id=str(narrative.narrative_id),
                    why="Narrative selected as best fit for target audience and domain",
                    correlation_id=cid,
                )
            for citation in all_citations:
                self._justification.record_citation_justification(
                    citation_id=str(citation.citation_id),
                    why="Citation included to support narrative content and evidence traceability",
                    correlation_id=cid,
                )
            self._justification.record_template_justification(
                template_type=policy_type,
                why=f"Template '{policy_type}' selected based on request policy type",
                correlation_id=cid,
            )
            for audience in audiences:
                self._justification.record_audience_justification(
                    audience=audience.value if hasattr(audience, 'value') else str(audience),
                    why="Audience targeted based on request target_audiences specification",
                    correlation_id=cid,
                )
            self._justification.record_policy_justification(
                policy_type=policy_type,
                why=f"Policy '{policy_type}' applied to enforce explanation governance rules",
                correlation_id=cid,
            )
            self.metrics_collector.increment_justifications(
                len(formatted_narratives) + len(all_citations) + 1 + len(audiences) + 1
            )
            log.info("coordinator.justification", narrative_count=len(formatted_narratives), citation_count=len(all_citations), audience_count=len(audiences))

            # Stage 19: Compliance — assess compliance
            self.trace.record_event(
                stage_name="COMPLIANCE",
                operation="assess",
                explanation_id=rid,
                correlation_id=cid,
            )
            compliance_result = self._compliance.assess_compliance(
                explanation_id=rid,
                package=package,
                narratives=formatted_narratives,
                citations=all_citations,
                traces=expl_traces,
                correlation_id=cid,
            )
            self.metrics_collector.increment_compliance(1)
            log.info("coordinator.compliance", compliant=compliance_result["compliant"], status=compliance_result["status"])

            # Stage 20: Audit — create audit package
            self.trace.record_event(
                stage_name="AUDIT",
                operation="create",
                explanation_id=rid,
                correlation_id=cid,
            )
            audit_result = self._audit_package.create(
                package=package,
                narratives=formatted_narratives,
                citations=all_citations,
                trace=expl_traces,
                metadata=request.metadata,
                version=str(version["version_number"]) if isinstance(version, dict) else "",
                timeline=timeline,
                correlation_id=cid,
            )
            self.metrics_collector.increment_audits(1)
            log.info("coordinator.audit", audit_id=audit_result["audit_id"])

            # Stage 21: Export — generate export profiles for audiences
            self.trace.record_event(
                stage_name="EXPORT",
                operation="export",
                explanation_id=rid,
                correlation_id=cid,
            )
            export_count = 0
            for audience in audiences:
                audience_value = audience.value if hasattr(audience, 'value') else str(audience)
                profile = self._export_profiles.get_profile(audience_value.lower())
                if profile:
                    export_data = self._export_profiles.export(
                        package=package,
                        narratives=formatted_narratives,
                        citations=all_citations,
                        profile_type=audience_value.lower(),
                        correlation_id=cid,
                    )
                    export_count += 1
            self.metrics_collector.increment_exports(export_count)
            log.info("coordinator.export", export_count=export_count)

            # Stage 22: Check for policy violations against result
            self.trace.record_event(
                stage_name="POLICY_CHECK",
                operation="check",
                explanation_id=rid,
                correlation_id=cid,
            )
            final_audience = default_audience
            final_violations = self.policy_engine.check_policy(
                policy_type=policy_type,
                audience=final_audience,
                narrative_count=len(narratives),
                has_citations=len(all_citations) > 0,
                has_trace=len(expl_traces) > 0,
            )
            if final_violations:
                log.warning("coordinator.policy_violations", violations=final_violations)

            # Stage 23: Build decision
            primary_narrative = package.primary_narrative
            decision = ExplanationDecision(
                result_id=result.result_id,
                conclusion=primary_narrative.content if primary_narrative else "Explanation completed.",
                reasoning_summary=package.reasoning_summary,
                recommendation_summary=package.recommendation_summary,
                selected_narratives=[str(n.narrative_id) for n in formatted_narratives],
                rejected_narratives=[],
                confidence=confidence.overall_confidence,
                audience=final_audience if hasattr(final_audience, 'value') else ExplanationLayer.ENGINEER,
                readiness=readiness_status,
                metadata={
                    "correlation_id": cid,
                    "policy_type": policy_type,
                    "violations": final_violations,
                    "review_results": review_results,
                    "version_id": version["version_id"],
                    "readiness_status": readiness_status,
                    "lineage_count": len(lineage_entries),
                    "snapshot_id": snapshot_record["snapshot_id"],
                    "compliance_status": compliance_result["status"],
                    "audit_id": audit_result["audit_id"],
                    "export_count": export_count,
                },
            )

            # Stage 24: Update session to COMPLETED
            self.trace.record_event(
                stage_name="COMPLETED",
                operation="complete",
                explanation_id=rid,
                correlation_id=cid,
                success=True,
            )
            self.session_manager.update_status(str(session.session_id), ExplanationStatus.COMPLETED)

            result.package = package
            result.narratives = formatted_narratives
            result.citations = all_citations
            result.decisions = [decision]
            result.status = ExplanationStatus.COMPLETED
            result.confidence = confidence

            self.session_manager.update_status(
                str(session.session_id),
                ExplanationStatus.COMPLETED,
            )

            log.info(
                "coordinator.explain.complete",
                status=result.status.value,
                confidence=confidence.overall_confidence,
                narratives=len(formatted_narratives),
                citations=len(all_citations),
                readiness=readiness_status,
                warnings=total_review_warnings,
            )

        except Exception as e:
            log.error("coordinator.explain.error", error=str(e))
            result.status = ExplanationStatus.FAILED
            self.session_manager.update_status(str(session.session_id), ExplanationStatus.FAILED)
            self.trace.record_event(
                stage_name="COMPLETED",
                operation="fail",
                explanation_id=str(request.request_id),
                correlation_id=cid,
                success=False,
                errors=[str(e)],
            )

        return result

    def get_result(self, result_id: str) -> ExplanationResult | None:
        """Retrieve an explanation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ExplanationResult if found, None otherwise.
        """
        return None

    def health(self) -> ExplanationHealth:
        """Get the health status of all sub-components.

        Returns:
            ExplanationHealth with component statuses.
        """
        return ExplanationHealth(
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
            explanation_count=0,
            error_count=0,
            average_latency_ms=0.0,
        )

    def metrics(self) -> ExplanationMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            ExplanationMetrics with current values.
        """
        snap = self.metrics_collector.snapshot()
        return ExplanationMetrics(
            explanations_total=snap.explanations_total,
            narratives_total=snap.narratives_total,
            citations_total=snap.citations_total,
            packages_total=snap.explanations_total,
            validated_total=snap.reviews_total,
            failed_total=0,
            explanations_per_domain={},
            explanations_per_layer=dict(snap.audience_distribution),
            average_confidence=snap.average_confidence,
            average_completeness=snap.average_completeness,
            average_quality=snap.average_quality,
            sessions_total=0,
            audiences_total=len(snap.audience_distribution),
            templates_total=len(snap.template_usage),
            citation_coverage=snap.average_quality,
        )
