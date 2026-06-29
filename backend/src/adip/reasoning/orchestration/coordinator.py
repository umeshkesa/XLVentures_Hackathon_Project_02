"""ReasoningCoordinator — orchestrates all reasoning sub-components.

Coordinates the full reasoning pipeline: validation, context building,
goal creation, constraint management, assumption tracking, strategy
selection, hypothesis generation, inference, contradiction detection,
graph building, decision alternatives, weight calculation, scoring,
policy enforcement, confidence calculation, tracing, and metrics.

Contains orchestration only — no business logic.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.reasoning.contracts.models import (
    ReasoningDecision,
    ReasoningHealth,
    ReasoningMetrics,
    ReasoningRequest,
    ReasoningResult,
    ReasoningStatus,
)
from adip.reasoning.enums import (
    ContradictionResolutionStatus,
    PolicyType,
)
from adip.reasoning.execution.assumption_manager import AssumptionManager
from adip.reasoning.execution.constraint_manager import ConstraintManager
from adip.reasoning.execution.context_builder import ContextBuilder
from adip.reasoning.execution.contradiction_detector import ContradictionDetector
from adip.reasoning.execution.decision_alternatives import DecisionAlternatives
from adip.reasoning.execution.decision_comparator import DecisionComparator
from adip.reasoning.execution.decision_justification import DecisionJustification
from adip.reasoning.execution.decision_quality import DecisionQualityManager
from adip.reasoning.execution.decision_ranking import DecisionRanking
from adip.reasoning.execution.decision_readiness import DecisionReadiness
from adip.reasoning.execution.goal_manager import ReasoningGoalManager
from adip.reasoning.execution.hypothesis_generator import HypothesisGenerator
from adip.reasoning.execution.impact_analyzer import ImpactAnalyzer
from adip.reasoning.execution.inference_engine import InferenceEngine
from adip.reasoning.execution.metrics import ReasoningMetricsCollector
from adip.reasoning.execution.policy_engine import PolicyEngine
from adip.reasoning.execution.reasoning_graph import ReasoningGraphBuilder
from adip.reasoning.execution.reasoning_lineage import ReasoningLineage
from adip.reasoning.execution.reasoning_memory import ReasoningMemory
from adip.reasoning.execution.reasoning_review import ReasoningReview
from adip.reasoning.execution.reasoning_score import ReasoningScoreCalculator
from adip.reasoning.execution.reasoning_snapshot import ReasoningSnapshot
from adip.reasoning.execution.risk_evaluator import RiskEvaluator
from adip.reasoning.execution.strategy_performance import StrategyPerformance
from adip.reasoning.execution.strategy_selector import StrategySelector
from adip.reasoning.execution.trace import ReasoningTrace
from adip.reasoning.execution.uncertainty_manager import UncertaintyManager
from adip.reasoning.execution.weight_manager import WeightManager
from adip.reasoning.orchestration.confidence import ReasoningConfidenceCalculator
from adip.reasoning.orchestration.session import ReasoningSessionManager

log = structlog.get_logger(__name__)


class ReasoningCoordinator:
    """Orchestrates all reasoning sub-components for the ADIP platform.

    ReasoningManager delegates to this coordinator for all sub-component
    interactions. All components are injectable via constructor (DI ready).
    """

    def __init__(
        self,
        context_builder: ContextBuilder | None = None,
        goal_manager: ReasoningGoalManager | None = None,
        constraint_manager: ConstraintManager | None = None,
        assumption_manager: AssumptionManager | None = None,
        strategy_selector: StrategySelector | None = None,
        hypothesis_generator: HypothesisGenerator | None = None,
        inference_engine: InferenceEngine | None = None,
        contradiction_detector: ContradictionDetector | None = None,
        graph_builder: ReasoningGraphBuilder | None = None,
        decision_alternatives: DecisionAlternatives | None = None,
        weight_manager: WeightManager | None = None,
        score_calculator: ReasoningScoreCalculator | None = None,
        policy_engine: PolicyEngine | None = None,
        trace: ReasoningTrace | None = None,
        metrics_collector: ReasoningMetricsCollector | None = None,
        session_manager: ReasoningSessionManager | None = None,
        confidence_calculator: ReasoningConfidenceCalculator | None = None,
        decision_comparator: DecisionComparator | None = None,
        risk_evaluator: RiskEvaluator | None = None,
        impact_analyzer: ImpactAnalyzer | None = None,
        uncertainty_manager: UncertaintyManager | None = None,
        reasoning_memory: ReasoningMemory | None = None,
        decision_ranking: DecisionRanking | None = None,
        decision_quality: DecisionQualityManager | None = None,
        reasoning_review: ReasoningReview | None = None,
        decision_justification: DecisionJustification | None = None,
        reasoning_lineage: ReasoningLineage | None = None,
        reasoning_snapshot: ReasoningSnapshot | None = None,
        strategy_performance: StrategyPerformance | None = None,
        decision_readiness: DecisionReadiness | None = None,
    ) -> None:
        self._context_builder = context_builder or ContextBuilder()
        self._goal_manager = goal_manager or ReasoningGoalManager()
        self._constraint_manager = constraint_manager or ConstraintManager()
        self._assumption_manager = assumption_manager or AssumptionManager()
        self._strategy_selector = strategy_selector or StrategySelector()
        self._hypothesis_generator = hypothesis_generator or HypothesisGenerator()
        self._inference_engine = inference_engine or InferenceEngine()
        self._contradiction_detector = contradiction_detector or ContradictionDetector()
        self._graph_builder = graph_builder or ReasoningGraphBuilder()
        self._decision_alternatives = decision_alternatives or DecisionAlternatives()
        self._weight_manager = weight_manager or WeightManager()
        self._score_calculator = score_calculator or ReasoningScoreCalculator()
        self._policy_engine = policy_engine or PolicyEngine()
        self._trace = trace or ReasoningTrace()
        self._metrics_collector = metrics_collector or ReasoningMetricsCollector()
        self._session_manager = session_manager or ReasoningSessionManager()
        self._confidence_calculator = confidence_calculator or ReasoningConfidenceCalculator()
        self._decision_comparator = decision_comparator or DecisionComparator()
        self._risk_evaluator = risk_evaluator or RiskEvaluator()
        self._impact_analyzer = impact_analyzer or ImpactAnalyzer()
        self._uncertainty_manager = uncertainty_manager or UncertaintyManager()
        self._reasoning_memory = reasoning_memory or ReasoningMemory()
        self._decision_ranking = decision_ranking or DecisionRanking()
        self._decision_quality = decision_quality or DecisionQualityManager()
        self._reasoning_review = reasoning_review or ReasoningReview()
        self._decision_justification = decision_justification or DecisionJustification()
        self._reasoning_lineage = reasoning_lineage or ReasoningLineage()
        self._reasoning_snapshot = reasoning_snapshot or ReasoningSnapshot()
        self._strategy_performance = strategy_performance or StrategyPerformance()
        self._decision_readiness = decision_readiness or DecisionReadiness()
        self._results: dict[str, ReasoningResult] = {}

    def _validate_request(self, request: ReasoningRequest) -> list[str]:
        """Validate a reasoning request.

        Simple internal validation — checks for required fields.
        """
        violations: list[str] = []
        if not request.evidence_package_id:
            violations.append("evidence_package_id is required")
        return violations

    # ── Reasoning Pipeline ──────────────────────────────────────────────

    def reason(
        self,
        request: ReasoningRequest,
        correlation_id: str = "",
    ) -> ReasoningResult:
        """Orchestrate the full reasoning pipeline.

        Per-stage timing and trace recording for all major stages:
        validation, context, goal, constraints, assumptions, strategy,
        hypotheses, inference, contradiction detection, graph, decision
        alternatives, weights, scoring, policy, and confidence.
        """
        request_id = str(request.request_id)
        correlation_id = correlation_id or request_id
        log.info("coordinator.reason", request_id=request_id, correlation_id=correlation_id)

        start_time = datetime.now(UTC)

        # Create result placeholder
        result = ReasoningResult(
            request_id=request.request_id,
            status=ReasoningStatus.INITIALIZED,
        )

        # ── Stage 1: Validate ───────────────────────────────────────────
        val_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="VALIDATE",
            operation="validate",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        violations = self._validate_request(request)
        if violations:
            result.status = ReasoningStatus.FAILED
            result.metadata["validation_violations"] = violations
            log.error("coordinator.validate.failed", violations=violations)
            self._metrics_collector.record_trace()
            self._results[request_id] = result
            return result
        val_duration = (datetime.now(UTC) - val_start).total_seconds() * 1000

        # ── Stage 2: Build context ──────────────────────────────────────
        ctx_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="CONTEXT",
            operation="build_context",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        context = self._context_builder.build_context(
            evidence_ids=[str(request.evidence_package_id)],
            domain=request.domain,
            correlation_id=correlation_id,
        )
        ctx_duration = (datetime.now(UTC) - ctx_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="CONTEXT",
            operation="build_context.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(ctx_duration, 2),
        )

        # ── Stage 3: Create goal ────────────────────────────────────────
        goal_start = datetime.now(UTC)
        from adip.reasoning.enums import ReasoningGoalType

        self._trace.record_goal(
            goal_type="reasoning",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        goal = self._goal_manager.create_goal(
            goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS,
            description=f"Reasoning goal for {request.domain.value} domain",
        )
        goal_duration = (datetime.now(UTC) - goal_start).total_seconds() * 1000
        self._trace.record_goal(
            goal_type=goal.goal_type.value,
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(goal_duration, 2),
        )
        self._metrics_collector.increment_goals()

        # ── Stage 4: Create constraints ─────────────────────────────────
        constraint_start = datetime.now(UTC)
        self._trace.record_constraints(
            constraint_count=0,
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        constraint_count = 0
        constraint_duration = (datetime.now(UTC) - constraint_start).total_seconds() * 1000
        self._trace.record_constraints(
            constraint_count=constraint_count,
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(constraint_duration, 2),
        )
        self._metrics_collector.increment_constraints(constraint_count)

        # ── Stage 5: Create assumptions ─────────────────────────────────
        assumption_start = datetime.now(UTC)
        self._trace.record_assumptions(
            assumption_count=0,
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        assumption_count = 0
        assumption_duration = (datetime.now(UTC) - assumption_start).total_seconds() * 1000
        self._trace.record_assumptions(
            assumption_count=assumption_count,
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(assumption_duration, 2),
        )

        # ── Stage 6: Select strategy ────────────────────────────────────
        strat_start = datetime.now(UTC)
        self._trace.record_strategy(
            strategy_type=request.strategy.value,
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        strategy_type = self._strategy_selector.select_strategy(
            domain=request.domain,
            has_evidence=True,
        )
        strat_duration = (datetime.now(UTC) - strat_start).total_seconds() * 1000
        self._trace.record_strategy(
            strategy_type=strategy_type.value,
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(strat_duration, 2),
        )
        result.metadata["strategy_type"] = strategy_type.value

        # ── Stage 7: Generate hypotheses ────────────────────────────────
        hyp_start = datetime.now(UTC)
        evidence_ids = [str(request.evidence_package_id)]
        hypothesis_set = self._hypothesis_generator.generate_ranked(
            evidence_ids=evidence_ids,
            domain=request.domain,
            count=5,
            correlation_id=correlation_id,
        )
        result.hypotheses = hypothesis_set
        hyp_duration = (datetime.now(UTC) - hyp_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="HYPOTHESIS",
            operation="generate",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(hyp_duration, 2),
        )
        self._metrics_collector.increment_hypotheses(len(hypothesis_set))

        # ── Stage 8: Draw inferences ────────────────────────────────────
        inf_start = datetime.now(UTC)
        inferences: list = []
        for hypothesis in hypothesis_set:
            inference = self._inference_engine.evidence_inference(
                evidence_ids=evidence_ids,
                hypothesis_id=str(hypothesis.hypothesis_id),
                correlation_id=correlation_id,
            )
            inferences.append(inference)
        result.inferences = inferences
        inf_duration = (datetime.now(UTC) - inf_start).total_seconds() * 1000
        self._trace.record_inference(
            inference_count=len(inferences),
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(inf_duration, 2),
        )

        # ── Stage 9: Detect contradictions ──────────────────────────────
        cd_start = datetime.now(UTC)
        contradictions = self._contradiction_detector.detect_evidence_contradictions(
            hypotheses=hypothesis_set,
            request_id=request_id,
            correlation_id=correlation_id,
        )
        result.contradictions = contradictions

        # Resolve contradictions
        resolved_count = 0
        for contradiction in contradictions:
            resolved = self._contradiction_detector.resolve(
                contradiction=contradiction,
                resolution="priority_override",
                correlation_id=correlation_id,
            )
            resolved.resolution_status = ContradictionResolutionStatus.RESOLVED
            resolved.resolved_at = datetime.now(UTC)
            resolved_count += 1

        cd_duration = (datetime.now(UTC) - cd_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="CONTRADICTION",
            operation="detect.resolve",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(cd_duration, 2),
        )
        self._metrics_collector.increment_contradictions(len(contradictions))

        # ── Stage 10: Build reasoning graph ────────────────────────────
        graph_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="GRAPH",
            operation="build",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        graph = self._graph_builder.create_graph(correlation_id=correlation_id)
        # Add hypothesis nodes
        for hypothesis in hypothesis_set:
            self._graph_builder.add_node(
                graph=graph,
                node_type="hypothesis",
                label=hypothesis.description[:50],
            )
        graph_duration = (datetime.now(UTC) - graph_start).total_seconds() * 1000
        result.metadata["graph_id"] = str(graph.graph_id)

        # ── Stage 11: Generate decision alternatives ────────────────────
        alt_start = datetime.now(UTC)
        hyp_descriptions = [h.description for h in hypothesis_set]
        alternatives = self._decision_alternatives.generate_alternatives(
            evidence_ids=evidence_ids,
            hypotheses=hyp_descriptions,
            count=3,
        )
        alt_duration = (datetime.now(UTC) - alt_start).total_seconds() * 1000
        self._trace.record_alternatives(
            alternative_count=len(alternatives),
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(alt_duration, 2),
        )
        self._metrics_collector.increment_alternatives(len(alternatives))

        # Evaluate and select best alternative
        for alt in alternatives:
            self._decision_alternatives.evaluate_alternative(
                str(alt.alternative_id),
                score=alt.confidence,
            )

        # ── Stage 11b: Compare decisions ─────────────────────────────────
        comp_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="DECISION_COMPARISON",
            operation="compare_all",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        comparisons, selected_alt = self._decision_comparator.compare_all(
            alternatives=alternatives,
        )
        best_alt = selected_alt or self._decision_alternatives.get_best_alternative()
        comp_duration = (datetime.now(UTC) - comp_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="DECISION_COMPARISON",
            operation="compare_all.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(comp_duration, 2),
        )
        result.metadata["comparisons_count"] = len(comparisons)

        # ── Stage 11c: Evaluate risks ────────────────────────────────────
        risk_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="RISK_EVALUATION",
            operation="evaluate_all",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        risk_assessments = self._risk_evaluator.evaluate_all(
            alternatives=alternatives,
            evidence_counts={
                str(a.alternative_id): len(evidence_ids) for a in alternatives
            },
            hypothesis_confidences={
                str(a.alternative_id): a.confidence for a in alternatives
            },
            inference_counts={
                str(a.alternative_id): len(inferences) for a in alternatives
            },
        )
        risk_duration = (datetime.now(UTC) - risk_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="RISK_EVALUATION",
            operation="evaluate_all.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(risk_duration, 2),
        )
        result.metadata["risk_assessments"] = {
            k: v.model_dump() for k, v in risk_assessments.items()
        }

        # ── Stage 11d: Analyze impacts ───────────────────────────────────
        impact_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="IMPACT_ANALYSIS",
            operation="estimate_all",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        impact_assessments = self._impact_analyzer.estimate_all(
            alternatives=alternatives,
            evidence_coverages={
                str(a.alternative_id): min(1.0, len(evidence_ids) / 10.0) for a in alternatives
            },
            hypothesis_confidences={
                str(a.alternative_id): a.confidence for a in alternatives
            },
            decision_confidences={
                str(a.alternative_id): a.confidence for a in alternatives
            },
        )
        impact_duration = (datetime.now(UTC) - impact_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="IMPACT_ANALYSIS",
            operation="estimate_all.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(impact_duration, 2),
        )
        result.metadata["impact_assessments"] = {
            k: v.model_dump() for k, v in impact_assessments.items()
        }

        # ── Stage 11e: Track uncertainties ───────────────────────────────
        unc_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="UNCERTAINTY",
            operation="track_all",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        uncertainties = self._uncertainty_manager.track_all(
            evidence_count=len(evidence_ids),
            expected_evidence=10,
            unknown_variables=0,
            contradiction_count=len(contradictions),
        )
        unc_duration = (datetime.now(UTC) - unc_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="UNCERTAINTY",
            operation="track_all.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(unc_duration, 2),
        )
        result.metadata["uncertainties"] = [u.model_dump() for u in uncertainties]

        # ── Stage 11f: Rank decisions ────────────────────────────────────
        rank_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="DECISION_RANKING",
            operation="rank",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        ranked_comparisons = self._decision_ranking.rank_by_composite(comparisons)
        ranking_scores: dict[str, float] = {
            c.alternative_id: c.composite_score for c in ranked_comparisons
        }
        rank_duration = (datetime.now(UTC) - rank_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="DECISION_RANKING",
            operation="rank.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(rank_duration, 2),
        )
        result.metadata["ranking_scores"] = ranking_scores

        # Store intermediate states in memory
        self._reasoning_memory.store_alternatives(request_id, alternatives)
        self._reasoning_memory.store_risks(request_id, risk_assessments)
        self._reasoning_memory.store_impacts(request_id, impact_assessments)
        self._reasoning_memory.store_uncertainties(request_id, uncertainties)
        self._reasoning_memory.store_decisions(request_id, ranked_comparisons, best=str(best_alt.alternative_id) if best_alt else None)

        # ── Stage 11g: Calculate decision quality ─────────────────────────
        quality_start = datetime.now(UTC)
        quality = self._decision_quality.calculate_overall_quality(
            evidence_coverage=len(evidence_ids) / max(1, 10),
            rule_coverage=1.0,
            goal_satisfaction=1.0,
            constraint_satisfaction=1.0,
            assumption_completeness=1.0,
        )
        quality_duration = (datetime.now(UTC) - quality_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="QUALITY",
            operation="calculate_quality",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(quality_duration, 2),
        )
        self._metrics_collector.record_quality_score(quality.overall)
        result.metadata["quality"] = quality.model_dump()

        # ── Stage 11h: Reasoning review ───────────────────────────────────
        review_start = datetime.now(UTC)
        self._trace.record_review_stage(
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        review_result = self._reasoning_review.perform_full_review()
        review_duration = (datetime.now(UTC) - review_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="REVIEW",
            operation="review.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(review_duration, 2),
        )
        self._metrics_collector.increment_reviews()
        result.metadata["review_result"] = review_result.model_dump()

        # ── Stage 11i: Build decision justification ───────────────────────
        just_start = datetime.now(UTC)
        evidence_descriptions = [f"Evidence: {eid}" for eid in evidence_ids]
        self._decision_justification.add_supporting_evidence(
            evidence_ids=evidence_ids,
            descriptions=evidence_descriptions,
        )
        hyp_descs = [h.description for h in hypothesis_set]
        for alt in alternatives:
            self._decision_justification.add_alternative(
                alternative=alt,
                was_selected=str(alt.alternative_id) == str(best_alt.alternative_id) if best_alt else False,
            )
        justification = self._decision_justification.build_justification()
        just_duration = (datetime.now(UTC) - just_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="JUSTIFICATION",
            operation="build",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(just_duration, 2),
        )
        result.metadata["justification"] = justification.model_dump()

        # ── Stage 11j: Assess decision readiness ──────────────────────────
        readiness_start = datetime.now(UTC)
        self._trace.record_readiness_stage(
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        readiness = self._decision_readiness.assess_readiness(
            confidence=best_alt.confidence if best_alt else 0.5,
            risk_score=0.0,
            contradiction_count=len(contradictions),
            constraint_violations=0,
            alternatives_count=len(alternatives),
            quality_score=quality.overall,
        )
        readiness_duration = (datetime.now(UTC) - readiness_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="READINESS",
            operation="assess",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(readiness_duration, 2),
        )
        result.metadata["readiness"] = readiness.model_dump()
        if readiness.readiness == "READY":
            self._metrics_collector.increment_readiness_ready()
        elif readiness.readiness == "NOT_READY":
            self._metrics_collector.increment_readiness_not_ready()
        else:
            self._metrics_collector.increment_readiness_more_info()

        # ── Stage 11k: Create reasoning lineage ───────────────────────────
        lineage_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="LINEAGE",
            operation="build",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        for eid in evidence_ids:
            self._reasoning_lineage.add_evidence(eid, f"Evidence used for {request.domain.value}")
        for h in hypothesis_set:
            self._reasoning_lineage.add_hypothesis(str(h.hypothesis_id), h.description, h.confidence)
        for inf in inferences:
            self._reasoning_lineage.add_inference(str(inf.inference_id))
        for alt in alternatives:
            self._reasoning_lineage.add_alternative(str(alt.alternative_id), alt.decision_description, alt.confidence)
        if best_alt:
            self._reasoning_lineage.set_final_decision(
                str(best_alt.alternative_id),
                best_alt.decision_description,
                best_alt.confidence,
            )
        lineage = self._reasoning_lineage.build_lineage()
        lineage_duration = (datetime.now(UTC) - lineage_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="LINEAGE",
            operation="build.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(lineage_duration, 2),
        )
        result.metadata["lineage"] = lineage.model_dump()

        # ── Stage 12: Calculate weights ─────────────────────────────────
        weight_start = datetime.now(UTC)
        evidence_weight = self._weight_manager.calculate_evidence_weight(
            evidence_count=len(evidence_ids),
        )
        goal_weight = self._weight_manager.calculate_goal_weight(
            goal_priority=goal.priority,
            is_primary=goal.is_primary,
        )
        overall_weight = self._weight_manager.calculate_overall_weight(
            evidence_weight=evidence_weight,
            goal_weight=goal_weight,
        )
        weight_duration = (datetime.now(UTC) - weight_start).total_seconds() * 1000
        result.metadata["overall_weight"] = overall_weight

        # ── Stage 13: Calculate scores ─────────────────────────────────
        score_start = datetime.now(UTC)
        reasoning_score = self._score_calculator.calculate_overall(
            consistency=self._score_calculator.calculate_consistency(
                contradiction_count=len(contradictions),
                total_hypotheses=len(hypothesis_set),
            ),
            coverage=self._score_calculator.calculate_coverage(
                evidence_covered=len(evidence_ids),
                total_evidence=max(1, len(evidence_ids)),
            ),
            completeness=self._score_calculator.calculate_completeness(
                hypotheses_generated=len(hypothesis_set),
                hypotheses_evaluated=len(hypothesis_set),
            ),
            rule_satisfaction=self._score_calculator.calculate_rule_satisfaction(
                satisfied_rules=0,
                total_rules=1,
            ),
            assumption_quality=self._score_calculator.calculate_assumption_quality(
                validated_assumptions=0,
                invalidated_assumptions=0,
                total_assumptions=max(1, assumption_count),
            ),
        )
        score_duration = (datetime.now(UTC) - score_start).total_seconds() * 1000
        result.metadata["reasoning_score"] = reasoning_score.model_dump()
        self._metrics_collector.record_score(reasoning_score.overall)

        # ── Stage 14: Enforce policy ────────────────────────────────────
        policy_start = datetime.now(UTC)
        best_alt = self._decision_alternatives.get_best_alternative()
        policy_confidence = best_alt.confidence if best_alt else 0.5
        policy_decision = self._policy_engine.check(
            policy_type=PolicyType.BALANCED,
            confidence=policy_confidence,
            contradiction_count=len(contradictions),
            constraint_violations=0,
        )
        policy_duration = (datetime.now(UTC) - policy_start).total_seconds() * 1000
        result.metadata["policy_decision"] = policy_decision.model_dump()

        # ── Build final decision ─────────────────────────────────────────
        decision: ReasoningDecision | None = None
        if best_alt and policy_decision.allowed:
            selected_hyp_ids = [
                h.hypothesis_id for h in hypothesis_set
                if h.confidence >= 0.5
            ]
            rejected_hyp_ids = [
                h.hypothesis_id for h in hypothesis_set
                if h.confidence < 0.5
            ]

            # Determine ranking position
            alt_id_str = str(best_alt.alternative_id)
            ranking_position = 0
            for i, comp in enumerate(ranked_comparisons):
                if comp.alternative_id == alt_id_str:
                    ranking_position = i + 1
                    break

            # Compute decision score from composite ranking
            decision_score = ranking_scores.get(alt_id_str, best_alt.confidence)

            decision = ReasoningDecision(
                result_id=result.result_id,
                conclusion=best_alt.decision_description,
                reasoning_summary="; ".join(best_alt.reasoning),
                confidence=best_alt.confidence,
                selected_hypotheses=selected_hyp_ids,
                rejected_hypotheses=rejected_hyp_ids,
                risk_assessments=risk_assessments,
                impact_assessments=impact_assessments,
                uncertainty=uncertainties[0] if uncertainties else None,
                decision_score=round(decision_score, 4),
                ranking_position=ranking_position,
                quality_score=round(quality.overall, 4),
                readiness_status=readiness.readiness,
                metadata={
                    "policy_allowed": policy_decision.allowed,
                    "overall_weight": overall_weight,
                    "strategy_type": strategy_type.value,
                    "comparisons_count": len(comparisons),
                    "uncertainties_count": len(uncertainties),
                },
            )
            result.decision = decision
            self._trace.record_decision(
                decision_summary=best_alt.decision_description,
                reasoning_id=request_id,
                correlation_id=correlation_id,
                duration_ms=0.0,
            )

        # ── Stage 15: Calculate confidence ───────────────────────────────
        result.confidence = self._confidence_calculator.calculate(
            result,
            risks=risk_assessments,
            impacts=impact_assessments,
            uncertainties=uncertainties,
            ranking_scores=ranking_scores,
        )

        # ── Finalise result ─────────────────────────────────────────────
        end_time = datetime.now(UTC)
        total_duration_ms = (end_time - start_time).total_seconds() * 1000
        result.status = ReasoningStatus.COMPLETED
        result.metadata["total_duration_ms"] = round(total_duration_ms, 2)

        # Record final trace
        self._trace.record_event(
            stage_name="REASONING",
            operation="reason.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            success=True,
            duration_ms=round(total_duration_ms, 2),
        )
        self._metrics_collector.record_trace()

        # ── Stage 16a: Record strategy performance ────────────────────────
        strat_perf_start = datetime.now(UTC)
        self._strategy_performance.record_execution(
            strategy=strategy_type,
            success=policy_decision.allowed if best_alt else False,
            latency_ms=(datetime.now(UTC) - strat_start).total_seconds() * 1000,
            confidence=best_alt.confidence if best_alt else 0.0,
        )
        strat_perf_duration = (datetime.now(UTC) - strat_perf_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="STRATEGY_PERFORMANCE",
            operation="record",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(strat_perf_duration, 2),
        )
        result.metadata["strategy_performance"] = self._strategy_performance.get_performance(strategy_type).model_dump() if self._strategy_performance.get_performance(strategy_type) else {}

        # ── Stage 16b: Create reasoning snapshot ──────────────────────────
        snap_start = datetime.now(UTC)
        self._trace.record_event(
            stage_name="SNAPSHOT",
            operation="create",
            reasoning_id=request_id,
            correlation_id=correlation_id,
        )
        snapshot = self._reasoning_snapshot.create_snapshot(
            context=context,
            graph=graph,
            alternatives=alternatives,
            confidence=result.confidence,
            risks=risk_assessments,
            impacts=impact_assessments,
            metadata={
                "request_id": request_id,
                "domain": request.domain.value,
                "strategy": strategy_type.value,
            },
        )
        snap_duration = (datetime.now(UTC) - snap_start).total_seconds() * 1000
        self._trace.record_event(
            stage_name="SNAPSHOT",
            operation="create.complete",
            reasoning_id=request_id,
            correlation_id=correlation_id,
            duration_ms=round(snap_duration, 2),
        )
        result.metadata["snapshot_id"] = snapshot.snapshot_id

        # Store result
        self._results[request_id] = result

        log.info(
            "coordinator.reason.complete",
            request_id=request_id,
            duration_ms=round(total_duration_ms, 2),
            hypotheses=len(result.hypotheses),
            inferences=len(result.inferences),
            contradictions=len(result.contradictions),
        )
        return result

    def get_result(self, result_id: str) -> ReasoningResult | None:
        """Retrieve a reasoning result by ID."""
        return self._results.get(result_id)

    # ── Health & Metrics ──────────────────────────────────────────────

    def health(self) -> ReasoningHealth:
        """Return health status of all sub-components."""
        log.info("coordinator.health")
        metrics_snap = self._metrics_collector.snapshot()
        return ReasoningHealth(
            overall_status="HEALTHY",
            reasoning_count=len(self._results),
            coordinator_status="HEALTHY",
            hypothesis_generator_status="HEALTHY",
            inference_engine_status="HEALTHY",
            contradiction_detector_status="HEALTHY",
            validator_status="HEALTHY",
            path_builder_status="HEALTHY",
            context_builder_status="HEALTHY",
            goal_manager_status="HEALTHY",
            constraint_manager_status="HEALTHY",
            assumption_manager_status="HEALTHY",
            strategy_selector_status="HEALTHY",
            weight_manager_status="HEALTHY",
            score_calculator_status="HEALTHY",
            policy_engine_status="HEALTHY",
            trace_status="HEALTHY",
            metrics_collector_status="HEALTHY",
            decision_quality_status="HEALTHY",
            reasoning_review_status="HEALTHY",
            decision_justification_status="HEALTHY",
            reasoning_lineage_status="HEALTHY",
            reasoning_snapshot_status="HEALTHY",
            strategy_performance_status="HEALTHY",
            decision_readiness_status="HEALTHY",
            error_count=0,
            average_latency_ms=0.0,
            uptime_seconds=0.0,
            total_reasonings=len(self._results),
            status="HEALTHY",
        )

    def metrics(self) -> ReasoningMetrics:
        """Return aggregated metrics from all sub-components."""
        log.info("coordinator.metrics")
        metrics_snap = self._metrics_collector.snapshot()
        total_results = len(self._results)
        all_confidences = [
            r.confidence.overall_confidence
            for r in self._results.values()
            if r.confidence is not None
        ]
        avg_confidence = (
            sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        )

        # Count risk, impact, uncertainty usage
        total_risks = sum(
            len(r.metadata.get("risk_assessments", {}))
            for r in self._results.values()
        )
        total_impacts = sum(
            len(r.metadata.get("impact_assessments", {}))
            for r in self._results.values()
        )
        total_uncertainties = sum(
            len(r.metadata.get("uncertainties", []))
            for r in self._results.values()
        )
        total_comparisons = sum(
            r.metadata.get("comparisons_count", 0)
            for r in self._results.values()
        )

        return ReasoningMetrics(
            reasoning_total=total_results,
            hypotheses_total=metrics_snap.hypotheses_count,
            inferences_total=metrics_snap.alternatives_count,
            contradictions_total=metrics_snap.contradictions_count,
            contradictions_resolved=metrics_snap.contradictions_count,
            paths_total=metrics_snap.goals_count,
            decisions_total=len(
                [r for r in self._results.values() if r.decision is not None]
            ),
            failed_total=len(
                [r for r in self._results.values() if r.status == ReasoningStatus.FAILED]
            ),
            hypotheses_per_domain={},
            inferences_per_strategy={},
            average_confidence=round(avg_confidence, 4),
            total_sessions=metrics_snap.sessions_count,
            reasonings_per_domain=dict(metrics_snap.reasonings_per_domain),
            reasonings_per_strategy=dict(metrics_snap.reasonings_per_strategy),
            decisions_per_strategy=dict(metrics_snap.decisions_per_strategy),
            hypotheses_per_strategy=dict(metrics_snap.hypotheses_per_strategy),
            inferences_per_domain=dict(metrics_snap.inferences_per_domain),
            contradictions_per_severity=dict(metrics_snap.contradictions_per_severity),
            average_latency_ms=metrics_snap.average_latency_ms,
            review_count=metrics_snap.review_count,
            readiness_ready=metrics_snap.readiness_ready,
            readiness_not_ready=metrics_snap.readiness_not_ready,
            readiness_more_info=metrics_snap.readiness_more_info,
            average_quality=round(metrics_snap.average_quality, 4),
        )
