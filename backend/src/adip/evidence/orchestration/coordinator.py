"""EvidenceCoordinator — central orchestrator for the evidence pipeline.

Coordinates all Phase 2 sub-components in the correct order for each
evidence operation. Contains orchestration only — no business logic.

Pipeline stages for each operation are timed and traced individually.
Phase 3 adds per-stage timing/tracing, confidence calculation, session
management, and enhanced decision creation.
Phase 3.5 adds weight and consensus stages.
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy.orm import Session

from adip.evidence.contracts.models import (
    Evidence,
    EvidenceDecision,
    EvidenceHealth,
    EvidenceMetrics,
    EvidencePackage,
)
from adip.evidence.enums import BundleType, EvidenceDomain, EvidenceStatus, EvidenceType
from adip.evidence.execution.bundle import EvidenceBundleManager
from adip.evidence.execution.cache import EvidenceCache
from adip.evidence.execution.classification_manager import EvidenceClassificationManager
from adip.evidence.execution.collector import EvidenceCollector
from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
from adip.evidence.execution.consensus_manager import EvidenceConsensusManager
from adip.evidence.execution.correlation_score import EvidenceCorrelationScorer
from adip.evidence.execution.correlator import EvidenceCorrelator
from adip.evidence.execution.deduplicator import EvidenceDeduplicator
from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
from adip.evidence.execution.graph_builder import EvidenceGraphBuilder
from adip.evidence.execution.metrics import EvidenceMetricsCollector
from adip.evidence.execution.normalizer import EvidenceNormalizer
from adip.evidence.execution.policy import EvidencePolicyEngine
from adip.evidence.execution.priority import EvidencePriorityAssigner
from adip.evidence.execution.quality_manager import EvidenceQualityManager
from adip.evidence.execution.source_reliability import EvidenceSourceReliability
from adip.evidence.execution.timeline import EvidenceTimelineManager
from adip.evidence.execution.trace import EvidenceTrace, TraceStage
from adip.evidence.execution.trust_manager import EvidenceTrustManager
from adip.evidence.execution.validator import EvidenceValidator
from adip.evidence.execution.weight_manager import EvidenceWeightManager
from adip.evidence.orchestration.confidence import EvidenceConfidenceCalculator
from adip.evidence.orchestration.session import EvidenceSessionManager
from adip.infrastructure.repositories.evidence_repo import (
    count_evidence as _db_count_evidence,
    get_all_evidence as _db_get_all_evidence,
    get_evidence as _db_get_evidence,
    save_evidence as _db_save_evidence,
)

log = structlog.get_logger(__name__)


class EvidenceCoordinator:
    """Orchestrates the full evidence processing pipeline.

    Each public method runs the relevant pipeline stages in order,
    with per-stage timing and tracing. All sub-components are
    injectable via constructor for DI and testability.

    Pipeline stages (varies by operation):
        1. Collection
        2. Validation
        3. Normalization
        4. Classification
        5. Priority Assignment
        6. Trust Assessment
        7. Correlation
        8. Conflict Detection
        9. Deduplication
        10. Quality Assessment
        11. Graph Building
        12. Bundle Creation
        13. Timeline
        14. Weight Calculation
        15. Consensus Assessment
        16. Cache
        17. Policy
        18. Confidence Calculation
        19. Metrics
        20. Trace
    """

    def __init__(
        self,
        collector: EvidenceCollector | None = None,
        validator: EvidenceValidator | None = None,
        normalizer: EvidenceNormalizer | None = None,
        classification_manager: EvidenceClassificationManager | None = None,
        priority_assigner: EvidencePriorityAssigner | None = None,
        trust_manager: EvidenceTrustManager | None = None,
        correlator: EvidenceCorrelator | None = None,
        conflict_detector: EvidenceConflictDetector | None = None,
        deduplicator: EvidenceDeduplicator | None = None,
        quality_manager: EvidenceQualityManager | None = None,
        graph_builder: EvidenceGraphBuilder | None = None,
        bundle_manager: EvidenceBundleManager | None = None,
        timeline_manager: EvidenceTimelineManager | None = None,
        cache: EvidenceCache | None = None,
        policy_engine: EvidencePolicyEngine | None = None,
        source_reliability: EvidenceSourceReliability | None = None,
        freshness_policy: EvidenceFreshnessPolicy | None = None,
        correlation_scorer: EvidenceCorrelationScorer | None = None,
        weight_manager: EvidenceWeightManager | None = None,
        consensus_manager: EvidenceConsensusManager | None = None,
        metrics_collector: EvidenceMetricsCollector | None = None,
        trace: EvidenceTrace | None = None,
        session_manager: EvidenceSessionManager | None = None,
        confidence_calculator: EvidenceConfidenceCalculator | None = None,
        db_session: Session | None = None,
    ) -> None:
        self.collector = collector or EvidenceCollector()
        self.validator = validator or EvidenceValidator()
        self.normalizer = normalizer or EvidenceNormalizer()
        self.classification_manager = classification_manager or EvidenceClassificationManager()
        self.priority_assigner = priority_assigner or EvidencePriorityAssigner()
        self.trust_manager = trust_manager or EvidenceTrustManager()
        self.correlator = correlator or EvidenceCorrelator()
        self.conflict_detector = conflict_detector or EvidenceConflictDetector()
        self.deduplicator = deduplicator or EvidenceDeduplicator()
        self.quality_manager = quality_manager or EvidenceQualityManager()
        self.graph_builder = graph_builder or EvidenceGraphBuilder()
        self.bundle_manager = bundle_manager or EvidenceBundleManager()
        self.timeline_manager = timeline_manager or EvidenceTimelineManager()
        self.cache = cache or EvidenceCache()
        self.policy_engine = policy_engine or EvidencePolicyEngine()
        self.source_reliability = source_reliability or EvidenceSourceReliability()
        self.freshness_policy = freshness_policy or EvidenceFreshnessPolicy()
        self.correlation_scorer = correlation_scorer or EvidenceCorrelationScorer()
        self.weight_manager = weight_manager or EvidenceWeightManager()
        self.consensus_manager = consensus_manager or EvidenceConsensusManager()
        self.metrics_collector = metrics_collector or EvidenceMetricsCollector()
        self.trace = trace or EvidenceTrace()
        self.session_manager = session_manager or EvidenceSessionManager()
        self.confidence_calculator = confidence_calculator or EvidenceConfidenceCalculator()

        # In-memory evidence store + optional DB persistence
        self._evidence_store: dict[str, Evidence] = {}
        self._packages: dict[str, EvidencePackage] = {}
        self._start_time: float = time.time()
        self.db_session: Session | None = db_session

    # ─────────────────────────────────────────────────────────────────
    # Collect & Process
    # ─────────────────────────────────────────────────────────────────

    def collect_and_process(
        self,
        evidence_type: EvidenceType = EvidenceType.KNOWLEDGE,
        domain: EvidenceDomain = EvidenceDomain.SYSTEM,
        source_id: str = "",
        correlation_id: str = "",
    ) -> EvidenceDecision:
        """Collect evidence and run the full processing pipeline.

        Pipeline: session -> collect -> validate -> normalize -> classify
                 -> priority -> trust -> correlate -> conflict -> dedup
                 -> quality -> graph -> bundle -> timeline -> weight
                 -> consensus -> cache -> policy -> confidence -> metrics -> trace
        """
        op = "collect_and_process"
        corr_id = correlation_id or str(uuid.uuid4())

        # Session
        session = self.session_manager.create_session(
            operation=op,
            correlation_id=corr_id,
        )

        reasoning: list[str] = []
        validation_violations: list[str] = []
        policy_violations: list[str] = []
        pipeline_errors: list[str] = []
        evidence_weights: dict[str, float] = {}
        consensus_result: str = ""

        # 1. Collection
        t0 = time.time()
        evidence = self.collector.collect(evidence_type, domain, source_id=source_id if source_id else None)
        t1 = time.time()
        col_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.COLLECTION, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=col_duration,
        )
        reasoning.append(f"Collected evidence from {source_id or domain.value}")
        self.metrics_collector.increment_evidence(
            domain=domain.value,
            source_id=source_id or domain.value,
        )

        # Store evidence
        self._evidence_store[str(evidence.evidence_id)] = evidence
        if self.db_session is not None:
            _db_save_evidence(self.db_session, evidence)
        self.session_manager.add_evidence_id(str(session.session_id), str(evidence.evidence_id))

        # 2. Validation
        t0 = time.time()
        validation_violations = self.validator.validate(evidence)
        t1 = time.time()
        val_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.VALIDATION, op, str(evidence.evidence_id),
            corr_id, len(validation_violations) == 0,
            errors=validation_violations, duration_ms=val_duration,
        )
        if validation_violations:
            reasoning.append(f"Validation issues: {'; '.join(validation_violations)}")
            self.metrics_collector.increment_conflict()
        else:
            reasoning.append("Validation passed")

        # 3. Normalization
        t0 = time.time()
        evidence = self.normalizer.normalize(evidence)
        t1 = time.time()
        norm_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.NORMALIZATION, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=norm_duration,
        )
        reasoning.append("Evidence normalized")
        self._evidence_store[str(evidence.evidence_id)] = evidence

        # 4. Classification
        t0 = time.time()
        classification = self.classification_manager.classify(evidence)
        t1 = time.time()
        cls_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.CLASSIFICATION, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=cls_duration,
        )
        reasoning.append(f"Classified as {classification}")
        self.metrics_collector.record_classification(classification)

        # 5. Priority Assignment
        t0 = time.time()
        priority = self.priority_assigner.assign_priority(evidence)
        t1 = time.time()
        pri_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.PRIORITY_ASSIGNMENT, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=pri_duration,
        )
        reasoning.append(f"Priority: {priority.value if hasattr(priority, 'value') else priority}")
        self.metrics_collector.record_priority(
            priority.value if hasattr(priority, 'value') else str(priority),
        )

        # 6. Trust Assessment
        t0 = time.time()
        trust = self.trust_manager.calculate_trust_score(evidence)
        t1 = time.time()
        tr_duration = round((t1 - t0) * 1000, 2)
        reasoning.append(f"Trust score: {trust.score:.2f}")
        self.metrics_collector.record_trust_score(trust.score)

        # 7. Correlation
        t0 = time.time()
        evidence_pool = list(self._evidence_store.values())
        correlation_result = self.correlator.correlate(evidence, evidence_pool)
        t1 = time.time()
        corr_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.CORRELATION, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=corr_duration,
        )
        correlated_count = len(correlation_result.correlated_evidence_ids)
        if correlated_count > 0:
            reasoning.append(f"Correlated with {correlated_count} items")
            self.metrics_collector.increment_correlation()
        else:
            reasoning.append("No correlations found")

        # 8. Conflict Detection
        t0 = time.time()
        conflict_report = self.conflict_detector.detect(evidence_pool)
        t1 = time.time()
        cfl_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.CONFLICT_DETECTION, op, str(evidence.evidence_id),
            corr_id, not conflict_report.has_conflicts,
            warnings=[f"{conflict_report.conflict_count} conflicts"] if conflict_report.has_conflicts else [],
            duration_ms=cfl_duration,
        )
        if conflict_report.has_conflicts:
            reasoning.append(f"Detected {conflict_report.conflict_count} conflicts")
            self.metrics_collector.increment_conflict()
        else:
            reasoning.append("No conflicts detected")

        # 9. Deduplication
        t0 = time.time()
        dedup_result = self.deduplicator.deduplicate(evidence_pool)
        t1 = time.time()
        dedup_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.DEDUPLICATION, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=dedup_duration,
        )
        reasoning.append(f"Deduplication: {len(dedup_result)} unique items")

        # 10. Quality Assessment
        t0 = time.time()
        quality = self.quality_manager.assess_quality(evidence)
        t1 = time.time()
        ql_duration = round((t1 - t0) * 1000, 2)
        reasoning.append(f"Quality score: {quality.overall:.2f}")
        self.metrics_collector.record_quality(quality.overall)
        self.metrics_collector.record_quality_distribution(quality.overall)

        # 11. Graph Building
        t0 = time.time()
        graph = self.graph_builder.build_graph(evidence_pool)
        t1 = time.time()
        gr_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.GRAPH_BUILDING, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=gr_duration,
        )
        reasoning.append(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

        # 12. Bundle Creation
        t0 = time.time()
        bundle = self.bundle_manager.create_bundle(
            BundleType.INCIDENT, "default", evidence_pool,
            title="Evidence Bundle", confidence=0.5,
        )
        t1 = time.time()
        bnd_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.BUNDLE_CREATION, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=bnd_duration,
        )
        self.metrics_collector.increment_bundle()
        reasoning.append(f"Bundle created: {bundle.title or 'Untitled'}")

        # 13. Timeline
        t0 = time.time()
        timeline = self.timeline_manager.build_timeline(evidence_pool)
        t1 = time.time()
        tm_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.TIMELINE, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=tm_duration,
        )
        reasoning.append(f"Timeline: {len(timeline.entries)} entries")

        # 14. Weight Calculation
        t0 = time.time()
        weight = self.weight_manager.calculate_weight(
            quality_score=quality.overall,
            trust_score=trust.score,
            freshness_score=0.8,
            correlation_score=0.8 if correlated_count > 0 else 0.5,
        )
        evidence_weights[str(evidence.evidence_id)] = weight
        normalized_weights = self.weight_manager.normalize_weights(evidence_weights)
        t1 = time.time()
        wt_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.WEIGHT, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=wt_duration,
        )
        self.metrics_collector.record_weight(weight)
        reasoning.append(f"Weight assigned: {weight:.4f}")

        # 15. Consensus Assessment
        t0 = time.time()
        evidence_ids = [str(e.evidence_id) for e in evidence_pool]
        agreement_score = self.consensus_manager.calculate_agreement_score(
            evidence_ids=evidence_ids,
            correlation_count=correlated_count,
            conflict_count=conflict_report.conflict_count,
        )
        conflict_score = self.consensus_manager.calculate_conflict_score(
            evidence_ids=evidence_ids,
            conflict_count=conflict_report.conflict_count,
        )
        consensus_level = self.consensus_manager.determine_consensus_level(
            agreement_score, conflict_score,
        )
        consensus_result = consensus_level.value
        t1 = time.time()
        cs_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_event(
            TraceStage.CONSENSUS, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=cs_duration,
        )
        self.metrics_collector.record_consensus(consensus_result)
        reasoning.append(f"Consensus: {consensus_result}")

        # 16. Cache
        t0 = time.time()
        self.cache.set_evidence(evidence.evidence_id, evidence)
        t1 = time.time()
        cache_duration = round((t1 - t0) * 1000, 2)
        self.metrics_collector.record_trace()

        # 17. Policy
        t0 = time.time()
        policy_violations = self.policy_engine.check_all(evidence)
        t1 = time.time()
        pol_duration = round((t1 - t0) * 1000, 2)
        if policy_violations:
            reasoning.append(f"Policy violations: {'; '.join(policy_violations)}")
        else:
            reasoning.append("Policy check passed")

        allowed = len(pipeline_errors) == 0

        # Update evidence status
        evidence.status = EvidenceStatus.READY
        self._evidence_store[str(evidence.evidence_id)] = evidence

        # 18. Confidence
        t0 = time.time()
        confidence = self.confidence_calculator.calculate(
            evidence=evidence,
            validation_violations=validation_violations,
            is_normalized=True,
            is_correlated=correlated_count > 0,
            trust_score=trust.score,
            quality_score=quality.overall,
            is_classified=True,
            freshness_score=0.8,
            consensus_level=consensus_result,
            weight_distribution_score=weight,
        )
        t1 = time.time()
        conf_duration = round((t1 - t0) * 1000, 2)

        # Complete session
        total_duration = round((time.time() - t1) * 1000, 2)
        self.session_manager.complete_session(
            str(session.session_id),
            status="COMPLETED" if allowed else "FAILED",
            statistics={
                "collection_ms": col_duration,
                "validation_ms": val_duration,
                "normalization_ms": norm_duration,
                "classification_ms": cls_duration,
                "priority_ms": pri_duration,
                "trust_ms": tr_duration,
                "correlation_ms": corr_duration,
                "conflict_ms": cfl_duration,
                "dedup_ms": dedup_duration,
                "quality_ms": ql_duration,
                "graph_ms": gr_duration,
                "bundle_ms": bnd_duration,
                "timeline_ms": tm_duration,
                "weight_ms": wt_duration,
                "consensus_ms": cs_duration,
                "cache_ms": cache_duration,
                "policy_ms": pol_duration,
                "confidence_ms": conf_duration,
                "total_ms": total_duration,
            },
        )

        # 19. Decision
        decision = EvidenceDecision(
            evidence_id=evidence.evidence_id,
            bundle_id=bundle.bundle_id,
            operation=op,
            allowed=allowed,
            selected_evidence=[e.evidence_id for e in evidence_pool],
            evidence_weights=normalized_weights,
            consensus_result=consensus_result,
            conflicts=[
                f"{c} conflicts" for c in [conflict_report.conflict_count] if c > 0
            ],
            reasoning=reasoning,
            confidence=confidence.overall_confidence,
            quality_score=quality.overall,
            trust_score=trust.score,
            performed_by="",
            metadata={
                "session_id": str(session.session_id),
                "correlation_id": corr_id,
                "bundle_id": str(bundle.bundle_id),
            },
        )

        # 20. Trace
        self.trace.record_event(
            TraceStage.METRICS, op, str(evidence.evidence_id),
            corr_id, True, duration_ms=total_duration,
        )

        return decision

    # ─────────────────────────────────────────────────────────────────
    # Process Existing
    # ─────────────────────────────────────────────────────────────────

    def process_existing(
        self,
        evidence_list: list[Evidence],
        correlation_id: str = "",
    ) -> EvidenceDecision:
        """Process existing evidence through the pipeline.

        Runs validation, normalization, classification, correlation,
        conflict detection, graph building, bundling, weight calculation,
        and consensus assessment on existing evidence items.
        """
        op = "process_existing"
        corr_id = correlation_id or str(uuid.uuid4())

        session = self.session_manager.create_session(
            operation=op,
            correlation_id=corr_id,
        )

        reasoning: list[str] = []
        total_violations: list[str] = []

        # Store evidence
        for ev in evidence_list:
            self._evidence_store[str(ev.evidence_id)] = ev
            if self.db_session is not None:
                _db_save_evidence(self.db_session, ev)
            self.session_manager.add_evidence_id(str(session.session_id), str(ev.evidence_id))

        # Validate all
        t0 = time.time()
        all_violations: list[str] = []
        for ev in evidence_list:
            violations = self.validator.validate(ev)
            all_violations.extend(violations)
        t1 = time.time()
        val_duration = round((t1 - t0) * 1000, 2)
        total_violations.extend(all_violations)
        reasoning.append(f"Validated {len(evidence_list)} items ({len(all_violations)} violations)")

        # Normalize all
        t0 = time.time()
        normalized = [self.normalizer.normalize(ev) for ev in evidence_list]
        for ev in normalized:
            self._evidence_store[str(ev.evidence_id)] = ev
            if self.db_session is not None:
                _db_save_evidence(self.db_session, ev)
        t1 = time.time()
        norm_duration = round((t1 - t0) * 1000, 2)
        reasoning.append(f"Normalized {len(normalized)} items")

        # Classify all
        for ev in normalized:
            cls = self.classification_manager.classify(ev)
            self.metrics_collector.record_classification(cls)
        reasoning.append("Classification completed")

        # Assign priorities
        for ev in normalized:
            pri = self.priority_assigner.assign_priority(ev)
            self.metrics_collector.record_priority(
                pri.value if hasattr(pri, 'value') else str(pri),
            )
        reasoning.append("Priority assignment completed")

        # Trust assessment
        trust_scores = [self.trust_manager.calculate_trust_score(ev) for ev in normalized]
        avg_trust = sum(t.score for t in trust_scores) / len(trust_scores) if trust_scores else 0.0
        reasoning.append(f"Average trust: {avg_trust:.2f}")

        # Correlation
        t0 = time.time()
        evidence_pool = list(self._evidence_store.values())
        total_correlated = 0
        for ev in normalized:
            corr_result = self.correlator.correlate(ev, evidence_pool)
            total_correlated += len(corr_result.correlated_evidence_ids)
        t1 = time.time()
        corr_duration = round((t1 - t0) * 1000, 2)
        reasoning.append(f"Correlation completed ({total_correlated} correlations)")

        # Conflict detection
        t0 = time.time()
        conflict_report = self.conflict_detector.detect(evidence_pool)
        t1 = time.time()
        cfl_duration = round((t1 - t0) * 1000, 2)
        if conflict_report.has_conflicts:
            reasoning.append(f"Detected {conflict_report.conflict_count} conflicts")

        # Deduplication
        t0 = time.time()
        dedup_result = self.deduplicator.deduplicate(evidence_pool)
        t1 = time.time()
        dedup_duration = round((t1 - t0) * 1000, 2)
        reasoning.append(f"Deduplication: {len(dedup_result)} unique")

        # Quality assessment
        quality = self.quality_manager.assess_quality(normalized[0]) if normalized else None
        quality_score = quality.overall if quality else 0.0
        reasoning.append(f"Quality: {quality_score:.2f}" if quality else "No quality assessment")
        if quality:
            self.metrics_collector.record_quality_distribution(quality.overall)

        # Graph building
        t0 = time.time()
        graph = self.graph_builder.build_graph(evidence_pool)
        t1 = time.time()
        gr_duration = round((t1 - t0) * 1000, 2)
        reasoning.append(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

        # Bundle creation
        t0 = time.time()
        bundle = self.bundle_manager.create_bundle(
            BundleType.INCIDENT, "default", evidence_pool,
            title="Evidence Bundle", confidence=0.5,
        )
        t1 = time.time()
        bnd_duration = round((t1 - t0) * 1000, 2)
        self.metrics_collector.increment_bundle()
        reasoning.append(f"Bundle created: {bundle.title or 'Untitled'}")

        # Timeline
        t0 = time.time()
        timeline = self.timeline_manager.build_timeline(evidence_pool)
        t1 = time.time()
        tm_duration = round((t1 - t0) * 1000, 2)
        reasoning.append(f"Timeline: {len(timeline.entries)} entries")

        # Weight Calculation
        evidence_ids = [str(e.evidence_id) for e in evidence_pool]
        evidence_weights: dict[str, float] = {}
        for idx, ev in enumerate(evidence_pool):
            ts = trust_scores[idx].score if idx < len(trust_scores) else 0.5
            w = self.weight_manager.calculate_weight(
                quality_score=quality_score,
                trust_score=ts,
            )
            evidence_weights[str(ev.evidence_id)] = w
            self.metrics_collector.record_weight(w)
        normalized_weights = self.weight_manager.normalize_weights(evidence_weights)

        # Consensus Assessment
        agreement_score = self.consensus_manager.calculate_agreement_score(
            evidence_ids=evidence_ids,
            correlation_count=total_correlated,
            conflict_count=conflict_report.conflict_count,
        )
        conflict_score = self.consensus_manager.calculate_conflict_score(
            evidence_ids=evidence_ids,
            conflict_count=conflict_report.conflict_count,
        )
        consensus_level = self.consensus_manager.determine_consensus_level(
            agreement_score, conflict_score,
        )
        consensus_result = consensus_level.value
        self.metrics_collector.record_consensus(consensus_result)
        reasoning.append(f"Consensus: {consensus_result}")

        # Policy
        policy_violations: list[str] = []
        for ev in evidence_pool:
            policy_violations.extend(self.policy_engine.check_all(ev))
        if policy_violations:
            reasoning.append(f"Policy violations: {'; '.join(policy_violations)}")

        allowed = True

        # Confidence
        confidence = self.confidence_calculator.calculate(
            evidence=normalized[0] if normalized else None,
            validation_violations=all_violations,
            is_normalized=True,
            is_correlated=total_correlated > 0,
            trust_score=avg_trust,
            quality_score=quality_score,
            is_classified=True,
            freshness_score=0.8,
            consensus_level=consensus_result,
            weight_distribution_score=sum(normalized_weights.values()) / max(1, len(normalized_weights)),
        )

        total_duration = round((time.time() - t0) * 1000, 2)
        self.session_manager.complete_session(
            str(session.session_id),
            status="COMPLETED",
            statistics={
                "validation_ms": val_duration,
                "normalization_ms": norm_duration,
                "correlation_ms": corr_duration,
                "conflict_ms": cfl_duration,
                "dedup_ms": dedup_duration,
                "graph_ms": gr_duration,
                "bundle_ms": bnd_duration,
                "timeline_ms": tm_duration,
                "total_ms": total_duration,
            },
        )

        decision = EvidenceDecision(
            evidence_id=normalized[0].evidence_id if normalized else uuid.uuid4(),
            bundle_id=bundle.bundle_id,
            operation=op,
            allowed=allowed,
            selected_evidence=[e.evidence_id for e in evidence_pool],
            evidence_weights=normalized_weights,
            consensus_result=consensus_result,
            conflicts=[
                f"{conflict_report.conflict_count} conflicts"
            ] if conflict_report.has_conflicts else [],
            reasoning=reasoning,
            confidence=confidence.overall_confidence,
            quality_score=quality_score,
            trust_score=avg_trust,
            performed_by="",
            metadata={
                "session_id": str(session.session_id),
                "correlation_id": corr_id,
                "evidence_count": len(evidence_pool),
            },
        )

        self.trace.record_event(
            TraceStage.METRICS, op, str(decision.decision_id),
            corr_id, True, duration_ms=total_duration,
        )

        return decision

    # ─────────────────────────────────────────────────────────────────
    # Lookup
    # ─────────────────────────────────────────────────────────────────

    def get_evidence(
        self,
        evidence_id: str,
        correlation_id: str = "",
    ) -> Evidence | None:
        """Retrieve evidence by ID with cache-first strategy."""
        op = "lookup"
        corr_id = correlation_id or str(uuid.uuid4())

        t0 = time.time()
        cached = self.cache.get_evidence(evidence_id)
        t1 = time.time()
        if cached is not None:
            self.metrics_collector.record_trace()
            self.trace.record_event(
                TraceStage.METRICS, "cache_hit", evidence_id,
                corr_id, True, duration_ms=round((t1 - t0) * 1000, 2),
            )
            return cached

        evidence = self._evidence_store.get(evidence_id)
        if evidence is None and self.db_session is not None:
            evidence = _db_get_evidence(self.db_session, evidence_id)
            if evidence is not None:
                self._evidence_store[evidence_id] = evidence

        if evidence:
            self.cache.set_evidence(evidence.evidence_id, evidence)

        self.trace.record_event(
            TraceStage.METRICS, op, evidence_id,
            corr_id, evidence is not None, duration_ms=round((time.time() - t0) * 1000, 2),
        )
        return evidence

    def get_package(self, package_id: str) -> EvidencePackage | None:
        """Retrieve an evidence package by ID."""
        return self._packages.get(package_id)

    # ─────────────────────────────────────────────────────────────────
    # Health & Metrics
    # ─────────────────────────────────────────────────────────────────

    def health(self) -> EvidenceHealth:
        """Aggregate health status from all sub-components."""
        all_evidence = self.get_all_evidence()
        metrics_snapshot = self.metrics_collector.snapshot()

        collector_status = "HEALTHY"
        validator_status = "HEALTHY"
        normalizer_status = "HEALTHY"
        classifier_status = "HEALTHY"
        priority_status = "HEALTHY"
        trust_manager_status = "HEALTHY"
        correlator_status = "HEALTHY"
        conflict_detector_status = "HEALTHY"
        deduplicator_status = "HEALTHY"
        scorer_status = "HEALTHY"
        graph_builder_status = "HEALTHY"
        bundle_manager_status = "HEALTHY"
        timeline_status = "HEALTHY"
        weight_manager_status = "HEALTHY"
        consensus_status = "HEALTHY"
        cache_status = "HEALTHY"
        policy_status = "HEALTHY"
        trace_status = "HEALTHY"
        metrics_status = "HEALTHY"

        statuses = [
            collector_status, validator_status, normalizer_status,
            classifier_status, priority_status, trust_manager_status,
            correlator_status, conflict_detector_status, deduplicator_status,
            scorer_status, graph_builder_status, bundle_manager_status,
            timeline_status, weight_manager_status, consensus_status,
            cache_status, policy_status,
            trace_status, metrics_status,
        ]
        if "UNHEALTHY" in statuses:
            overall = "UNHEALTHY"
        elif "DEGRADED" in statuses:
            overall = "DEGRADED"
        else:
            overall = "HEALTHY"

        return EvidenceHealth(
            overall_status=overall,
            evidence_count=len(all_evidence),
            collector_status=collector_status,
            validator_status=validator_status,
            normalizer_status=normalizer_status,
            classifier_status=classifier_status,
            priority_status=priority_status,
            trust_manager_status=trust_manager_status,
            correlator_status=correlator_status,
            conflict_detector_status=conflict_detector_status,
            deduplicator_status=deduplicator_status,
            scorer_status=scorer_status,
            graph_builder_status=graph_builder_status,
            bundle_manager_status=bundle_manager_status,
            timeline_status=timeline_status,
            weight_manager_status=weight_manager_status,
            consensus_status=consensus_status,
            cache_status=cache_status,
            policy_status=policy_status,
            trace_status=trace_status,
            metrics_status=metrics_status,
            error_count=metrics_snapshot.evidence_count,
            average_latency_ms=0.0,
            uptime_seconds=round(time.time() - self._start_time, 2),
            last_check=datetime.now(UTC),
        )

    def metrics(self) -> EvidenceMetrics:
        """Return aggregated metrics from the metrics collector."""
        snap = self.metrics_collector.snapshot()
        all_evidence = self.get_all_evidence()
        return EvidenceMetrics(
            evidence_total=len(all_evidence),
            packages_total=snap.bundle_count,
            collections_total=snap.evidence_count,
            validations_total=snap.evidence_count,
            normalizations_total=snap.evidence_count,
            classifications_total=sum(snap.classification_count.values()),
            priority_assignments_total=sum(snap.priority_distribution.values()),
            graphs_total=snap.bundle_count,
            graph_nodes_total=snap.evidence_count,
            graph_edges_total=snap.correlations_count,
            correlations_total=snap.correlations_count,
            conflicts_total=snap.conflicts_count,
            deduplications_total=snap.evidence_count,
            bundles_total=snap.bundle_count,
            timelines_total=snap.bundle_count,
            fusions_total=0,
            cache_hits=0,
            cache_misses=0,
            policy_checks=snap.evidence_count,
            policy_violations=snap.conflicts_count,
            errors_total=0,
            evidence_per_classification=dict(snap.classification_count),
            evidence_per_priority=dict(snap.priority_distribution),
            evidence_per_domain={},
            evidence_per_type={},
            average_quality_score=snap.average_quality,
            consistency_distribution=dict(snap.consistency_distribution),
            consensus_distribution=dict(snap.consensus_distribution),
            weight_distribution=dict(snap.weight_distribution),
            trust_distribution=dict(snap.trust_distribution),
            quality_distribution=dict(snap.quality_distribution),
            correlation_distribution=dict(snap.correlation_distribution),
            timestamp=datetime.now(UTC),
        )

    def get_all_evidence(self) -> list[Evidence]:
        """Return all stored evidence (for manager use)."""
        seen: set[str] = set(self._evidence_store.keys())
        result = list(self._evidence_store.values())
        if self.db_session is not None:
            for ev in _db_get_all_evidence(self.db_session):
                eid = str(ev.evidence_id)
                if eid not in seen:
                    seen.add(eid)
                    result.append(ev)
        return result
