"""RecommendationCoordinator — orchestrates the recommendation pipeline.

Coordinates the full recommendation pipeline by delegating to
Phase 2 execution components and Phase 3 orchestration components.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid

import structlog
from sqlalchemy.orm import Session

from adip.recommendation.contracts.models import (
    RecommendationDecision,
    RecommendationHealth,
    RecommendationMetrics,
    RecommendationRequest,
    RecommendationResult,
)
from adip.recommendation.enums import (
    RecommendationReadinessStatus,
    RecommendationStatus,
)
from adip.recommendation.execution.cost_analyzer import CostAnalyzer
from adip.recommendation.execution.dependency_manager import DependencyManager
from adip.recommendation.execution.feasibility_analyzer import FeasibilityAnalyzer
from adip.recommendation.execution.generator import RecommendationGenerator
from adip.recommendation.execution.implementation_plan_builder import ImplementationPlanBuilder
from adip.recommendation.execution.metrics import RecommendationMetricsCollector
from adip.recommendation.execution.outcome_predictor import OutcomePredictor
from adip.recommendation.execution.policy_evaluator import PolicyEvaluator
from adip.recommendation.execution.portfolio import RecommendationPortfolio as PortfolioComponent
from adip.recommendation.execution.ranker import RecommendationRanker
from adip.recommendation.execution.score_manager import ScoreManager
from adip.recommendation.execution.strategy_selector import StrategySelector
from adip.recommendation.execution.timeline_manager import TimelineManager
from adip.recommendation.execution.trace import RecommendationTrace
from adip.recommendation.execution.tradeoff_analyzer import TradeoffAnalyzer
from adip.recommendation.orchestration.approval_readiness import RecommendationApprovalReadiness
from adip.recommendation.orchestration.confidence import RecommendationConfidenceCalculator
from adip.recommendation.orchestration.justification import RecommendationJustification
from adip.recommendation.orchestration.lineage import RecommendationLineage
from adip.recommendation.orchestration.portfolio_comparator import PortfolioComparator
from adip.recommendation.orchestration.portfolio_quality import PortfolioQuality
from adip.recommendation.orchestration.quality import RecommendationQualityManager
from adip.recommendation.orchestration.readiness import RecommendationReadiness
from adip.recommendation.orchestration.review import RecommendationReview
from adip.recommendation.orchestration.session import RecommendationSessionManager
from adip.recommendation.orchestration.snapshot import RecommendationSnapshot
from adip.recommendation.orchestration.version_manager import RecommendationVersionManager
from adip.infrastructure.repositories.recommendation_repo import (
    get_all_recommendations as _db_get_all_recommendations,
    save_recommendation_dict as _db_save_recommendation_dict,
)

log = structlog.get_logger(__name__)


class RecommendationCoordinator:
    """Orchestrates the full recommendation pipeline.

    Coordinates strategy selection, generation, ranking, scoring,
    feasibility, cost, dependency, plan, timeline, tradeoff, policy,
    outcome, portfolio, version, review, confidence, readiness,
    lineage, snapshot, metric, and trace stages.
    """

    def __init__(
        self,
        strategy_selector: StrategySelector | None = None,
        generator: RecommendationGenerator | None = None,
        ranker: RecommendationRanker | None = None,
        score_manager: ScoreManager | None = None,
        feasibility_analyzer: FeasibilityAnalyzer | None = None,
        cost_analyzer: CostAnalyzer | None = None,
        dependency_manager: DependencyManager | None = None,
        plan_builder: ImplementationPlanBuilder | None = None,
        timeline_manager: TimelineManager | None = None,
        tradeoff_analyzer: TradeoffAnalyzer | None = None,
        policy_evaluator: PolicyEvaluator | None = None,
        outcome_predictor: OutcomePredictor | None = None,
        portfolio_component: PortfolioComponent | None = None,
        session_manager: RecommendationSessionManager | None = None,
        confidence_calculator: RecommendationConfidenceCalculator | None = None,
        review: RecommendationReview | None = None,
        version_manager: RecommendationVersionManager | None = None,
        readiness: RecommendationReadiness | None = None,
        lineage: RecommendationLineage | None = None,
        snapshot: RecommendationSnapshot | None = None,
        portfolio_comparator: PortfolioComparator | None = None,
        quality_manager: RecommendationQualityManager | None = None,
        justification: RecommendationJustification | None = None,
        approval_readiness: RecommendationApprovalReadiness | None = None,
        portfolio_quality: PortfolioQuality | None = None,
        trace: RecommendationTrace | None = None,
        metrics_collector: RecommendationMetricsCollector | None = None,
        db_session: Session | None = None,
    ) -> None:
        self.db_session: Session | None = db_session
        self.strategy_selector = strategy_selector or StrategySelector()
        self.generator = generator or RecommendationGenerator()
        self.ranker = ranker or RecommendationRanker()
        self.score_manager = score_manager or ScoreManager()
        self.feasibility_analyzer = feasibility_analyzer or FeasibilityAnalyzer()
        self.cost_analyzer = cost_analyzer or CostAnalyzer()
        self.dependency_manager = dependency_manager or DependencyManager()
        self.plan_builder = plan_builder or ImplementationPlanBuilder()
        self.timeline_manager = timeline_manager or TimelineManager()
        self.tradeoff_analyzer = tradeoff_analyzer or TradeoffAnalyzer()
        self.policy_evaluator = policy_evaluator or PolicyEvaluator()
        self.outcome_predictor = outcome_predictor or OutcomePredictor()
        self.portfolio_component = portfolio_component or PortfolioComponent()
        self.session_manager = session_manager or RecommendationSessionManager()
        self.confidence_calculator = confidence_calculator or RecommendationConfidenceCalculator()
        self.review = review or RecommendationReview()
        self.version_manager = version_manager or RecommendationVersionManager()
        self.readiness = readiness or RecommendationReadiness()
        self.lineage = lineage or RecommendationLineage()
        self.snapshot = snapshot or RecommendationSnapshot()
        self.portfolio_comparator = portfolio_comparator or PortfolioComparator()
        self.quality_manager = quality_manager or RecommendationQualityManager()
        self.justification = justification or RecommendationJustification()
        self.approval_readiness = approval_readiness or RecommendationApprovalReadiness()
        self.portfolio_quality = portfolio_quality or PortfolioQuality()
        self.trace = trace or RecommendationTrace()
        self.metrics_collector = metrics_collector or RecommendationMetricsCollector()

    def recommend(
        self,
        request: RecommendationRequest,
        correlation_id: str = "",
    ) -> RecommendationResult:
        """Execute a full recommendation pipeline.

        Args:
            request: The recommendation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The recommendation result with decision, candidates, and confidence.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("coordinator.recommend.start", request_id=str(request.request_id), cid=cid)

        result = RecommendationResult(
            request_id=request.request_id,
            status=RecommendationStatus.INITIALIZED,
        )

        session = self.session_manager.create_session(
            request_id=str(request.request_id),
            domain=request.domain,
            goal=",".join(g.value for g in request.goals) if request.goals else "",
            strategy=request.strategy.value,
        )

        try:
            # Stage 1: Strategy selection
            self.trace.record_strategy_stage(str(request.request_id), correlation_id=cid)
            strategy = self.strategy_selector.select_strategy(
                goals=request.goals,
                domain=request.domain,
                has_policy=True,
                has_context=bool(request.context),
            )
            log.info("coordinator.strategy", strategy=strategy.value)

            # Stage 2: Generation
            self.trace.record_generation_stage(str(request.request_id), correlation_id=cid)
            candidates = self.generator.generate(
                reasoning_result_id=str(request.reasoning_result_id),
                strategy=strategy,
                domain=request.domain,
                goals=request.goals,
                count=5,
            )
            self.metrics_collector.increment_candidates(len(candidates))
            log.info("coordinator.generation", count=len(candidates))

            # Stage 3: Ranking
            self.trace.record_ranking_stage(str(request.request_id), correlation_id=cid)
            ranked = self.ranker.rank(candidates, goals=request.goals)
            self.metrics_collector.increment_rankings(len(ranked))
            log.info("coordinator.ranking", count=len(ranked))

            # Stage 4: Scoring
            self.trace.record_scoring_stage(str(request.request_id), correlation_id=cid)
            best = ranked[0] if ranked else None
            if best:
                score = self.score_manager.calculate(
                    business_value=best.confidence * 0.8,
                    feasibility=0.7,
                    impact=0.6,
                    risk_adjustment=1.0 - (best.confidence * 0.2),
                    policy_compliance=0.9,
                )
                self.metrics_collector.increment_scores()
                self.metrics_collector.record_confidence(score.overall)
            else:
                score = self.score_manager.calculate()

            # Stage 5: Feasibility
            self.trace.record_feasibility_stage(str(request.request_id), correlation_id=cid)
            feasibility = self.feasibility_analyzer.analyze(
                resource_score=0.7,
                budget_score=0.8,
                inventory_score=0.6,
                technician_score=0.7,
                time_window_score=0.5,
                operational_score=0.6,
            )
            self.metrics_collector.record_feasibility(feasibility.feasibility_score)
            log.info("coordinator.feasibility", status=feasibility.status.value)

            # Stage 6: Cost
            self.trace.record_cost_stage(str(request.request_id), correlation_id=cid)
            cost = self.cost_analyzer.estimate(
                implementation_cost=5000.0,
                operational_cost=2000.0,
                downtime_cost=1000.0,
                expected_benefit=20000.0,
            )
            self.metrics_collector.record_cost(cost.total_cost)
            log.info("coordinator.cost", total=cost.total_cost, roi=cost.roi)

            # Stage 7: Dependencies
            self.trace.record_dependency_stage(str(request.request_id), correlation_id=cid)
            rec_ids = [str(c.candidate_id) for c in ranked[:3]] if ranked else []
            deps = self.dependency_manager.build_graph(rec_ids)

            # Stage 8: Plan
            self.trace.record_plan_stage(str(request.request_id), correlation_id=cid)
            if best:
                plan = self.plan_builder.build(
                    recommendation_id=str(best.candidate_id),
                    action=best.action,
                    step_count=3,
                )

            # Stage 9: Timeline
            self.trace.record_timeline_stage(str(request.request_id), correlation_id=cid)
            timeline = self.timeline_manager.estimate(
                urgency_score=0.7,
                complexity="medium",
            )

            # Stage 10: Tradeoffs
            self.trace.record_tradeoff_stage(str(request.request_id), correlation_id=cid)
            if ranked and len(ranked) > 1:
                tradeoffs = self.tradeoff_analyzer.analyze_candidates(ranked[0], ranked[1:])

            # Stage 11: Policy
            self.trace.record_policy_stage(str(request.request_id), correlation_id=cid)
            policy_result = self.policy_evaluator.evaluate(
                safety_score=0.9,
                compliance_score=0.8,
                business_score=0.7,
                operational_score=0.8,
            )
            if not policy_result.overall_passed:
                self.metrics_collector.increment_policy_violations()
            log.info("coordinator.policy", passed=policy_result.overall_passed)

            # Stage 12: Outcome prediction
            self.trace.record_outcome_stage(str(request.request_id), correlation_id=cid)
            predictions = self.outcome_predictor.predict_batch(ranked) if ranked else []

            # Stage 13: Portfolio
            self.trace.record_portfolio_stage(str(request.request_id), correlation_id=cid)
            primary_id = str(best.candidate_id) if best else ""
            alt_ids = [str(c.candidate_id) for c in ranked[1:4]] if ranked and len(ranked) > 1 else []
            portfolio = self.portfolio_component.create(
                primary_id=primary_id,
                alternative_ids=alt_ids,
                outcomes=predictions,
                dependencies=deps if deps.nodes else None,
            )
            self.metrics_collector.increment_portfolios()
            log.info("coordinator.portfolio", primary=primary_id, alternatives=len(alt_ids))

            # Stage 14: Version
            self.trace.record_event(stage_name="VERSION", operation="create", recommendation_id=primary_id, correlation_id=cid)
            version = self.version_manager.create_version(
                recommendation_id=primary_id,
                data={"strategy": strategy.value, "domain": request.domain.value, "confidence": score.overall},
                description=f"Version for recommendation {primary_id[:8]}",
            )

            # Stage 15: Review
            self.trace.record_event(stage_name="REVIEW", operation="review", recommendation_id=primary_id, correlation_id=cid)
            review_result = self.review.review(
                policy_result=policy_result,
                feasibility=feasibility,
                portfolio=portfolio,
                confidence=score.overall,
                has_dependencies=bool(deps.nodes),
            )

            # Stage 16: Confidence
            self.trace.record_event(stage_name="CONFIDENCE", operation="calculate", recommendation_id=primary_id, correlation_id=cid)
            confidence = self.confidence_calculator.calculate(
                reasoning_confidence=best.confidence if best else 0.0,
                business_score=score.overall,
                feasibility=feasibility.feasibility_score,
                policy_compliance=0.9 if policy_result.overall_passed else 0.3,
                outcome_prediction=(
                    max(p.success_probability for p in predictions) if predictions else 0.0
                ),
                portfolio_quality=portfolio.overall_confidence,
            )
            self.metrics_collector.record_confidence(confidence.overall_confidence)

            # Stage 17: Readiness
            self.trace.record_event(stage_name="READINESS", operation="assess", recommendation_id=primary_id, correlation_id=cid)
            readiness_status = self.readiness.assess(
                review_result=review_result,
                confidence=confidence.overall_confidence,
                feasibility_score=feasibility.feasibility_score,
                policy_passed=policy_result.overall_passed,
            )

            # Stage 18: Lineage
            self.trace.record_event(stage_name="LINEAGE", operation="record", recommendation_id=primary_id, correlation_id=cid)
            self.lineage.record(
                lineage_type="recommendation",
                source_id=str(request.reasoning_result_id),
                target_id=primary_id,
                description="Recommendation from reasoning result",
            )

            # Stage 19: Snapshot
            self.trace.record_event(stage_name="SNAPSHOT", operation="create", recommendation_id=primary_id, correlation_id=cid)
            snap = self.snapshot.create_portfolio_snapshot(
                recommendation_id=primary_id,
                portfolio=portfolio,
            )

            self.lineage.record_review(
                source_id=primary_id,
                target_id=primary_id,
                description=f"Review: {review_result.passed}",
            )
            self.lineage.record_action(
                source_id=primary_id,
                target_id=primary_id,
                description=f"Action for recommendation {primary_id[:8]}",
            )

            # Stage 20: Quality
            self.trace.record_quality_stage(primary_id, correlation_id=cid)
            quality_result = self.quality_manager.calculate(
                portfolio=portfolio,
                feasibility=feasibility,
                policy_result=policy_result,
                outcomes=predictions,
                business_goals=[g.value for g in request.goals],
            )
            self.metrics_collector.increment_quality()
            self.metrics_collector.record_quality(quality_result.overall_quality)

            # Stage 21: Portfolio Quality
            self.trace.record_event(stage_name="PORTFOLIO_QUALITY", operation="evaluate", recommendation_id=primary_id, correlation_id=cid)
            pq_result = self.portfolio_quality.evaluate(
                portfolio=portfolio,
                policy_result=policy_result,
                feasibility=feasibility,
                alternatives=ranked[1:4] if ranked and len(ranked) > 1 else [],
            )
            self.metrics_collector.increment_portfolio_quality()

            # Stage 22: Justification
            self.trace.record_event(stage_name="JUSTIFICATION", operation="record", recommendation_id=primary_id, correlation_id=cid)
            justification = self.justification.record(
                recommendation_id=primary_id,
                supporting_reasoning=f"Generated via {strategy.value} strategy",
                supporting_evidence=[f"Candidate: {c.action}" for c in ranked[:3]] if ranked else [],
                business_goals=[g.value for g in request.goals],
                constraints=[],
                policies=[f"Safety: {policy_result.safety_passed}, Compliance: {policy_result.compliance_passed}"] if policy_result else [],
                tradeoffs=[f"Cost vs Risk: {t.overall_recommendation}" for t in (tradeoffs if hasattr(self, 'tradeoffs') else [])],
            )
            self.metrics_collector.increment_justifications()

            # Stage 23: Approval Readiness
            self.trace.record_approval_readiness_stage(primary_id, correlation_id=cid)
            approval_result = self.approval_readiness.assess(
                review_result=review_result,
                confidence=confidence.overall_confidence,
                feasibility_score=feasibility.feasibility_score,
                policy_passed=policy_result.overall_passed,
                quality_score=quality_result.overall_quality,
            )
            self.metrics_collector.increment_approval_readiness(approval_result.status)

            # Build decision
            primary_rec = best.action if best else ""
            alt_recs = [c.action for c in ranked[1:4]] if ranked else []

            decision = RecommendationDecision(
                result_id=result.result_id,
                conclusion=primary_rec,
                reasoning_summary=f"Generated via {strategy.value} strategy in {request.domain.value} domain",
                confidence=confidence.overall_confidence,
                selected_candidates=[str(best.candidate_id)] if best else [],
                rejected_candidates=[str(c.candidate_id) for c in ranked[4:]] if ranked and len(ranked) > 4 else [],
                business_score=score.overall,
                primary_recommendation=primary_rec,
                alternative_recommendations=alt_recs,
                quality_score=quality_result.overall_quality,
                feasibility=feasibility.status.value,
                readiness=readiness_status.value,
                package=None,
            )

            result.decision = decision

            # Persist to database
            if self.db_session is not None and best:
                _db_save_recommendation_dict(
                    self.db_session,
                    entity_id=best.candidate_id,
                    status=result.status.value if hasattr(result.status, "value") else str(result.status),
                    priority=best.priority.value if hasattr(best.priority, "value") else str(best.priority),
                    recommendation_type=request.recommendation_type.value if hasattr(request, 'recommendation_type') and hasattr(request.recommendation_type, 'value') else str(getattr(request, 'recommendation_type', '')),
                    source=request.source.value if hasattr(request, 'source') and hasattr(request.source, 'value') else str(getattr(request, 'source', '')),
                    title=(best.action or primary_rec)[:512],
                    description=best.description or "",
                    domain=request.domain.value if hasattr(request.domain, "value") else str(request.domain),
                    confidence=confidence.overall_confidence,
                    estimated_cost=cost.total_cost if cost else None,
                    estimated_savings=0.0,
                    action=primary_rec or "",
                    reasoning_session_id=str(request.reasoning_result_id) if request.reasoning_result_id else None,
                    serialized=None,
                )
            result.candidates = ranked
            result.confidence = confidence
            result.status = RecommendationStatus.COMPLETED
            result.readiness = readiness_status.value

            if readiness_status == RecommendationReadinessStatus.BLOCKED:
                result.status = RecommendationStatus.FAILED
            elif readiness_status == RecommendationReadinessStatus.REQUIRES_REVIEW:
                result.status = RecommendationStatus.VALIDATED

            self.trace.record_event(
                stage_name="COMPLETED",
                operation="complete",
                recommendation_id=primary_id,
                correlation_id=cid,
                success=result.status != RecommendationStatus.FAILED,
            )

            self.session_manager.complete_session(
                str(session.session_id),
                statistics={
                    "candidates": len(candidates),
                    "confidence": confidence.overall_confidence,
                    "readiness": readiness_status.value,
                    "feasibility": feasibility.feasibility_score,
                    "quality": quality_result.overall_quality,
                },
            )

            self.metrics_collector.record_trace()
            log.info(
                "coordinator.recommend.complete",
                status=result.status.value,
                confidence=confidence.overall_confidence,
                readiness=readiness_status.value,
            )

        except Exception as e:
            log.error("coordinator.recommend.error", error=str(e))
            result.status = RecommendationStatus.FAILED
            self.session_manager.fail_session(str(session.session_id), error=str(e))
            self.trace.record_event(
                stage_name="COMPLETED",
                operation="fail",
                recommendation_id="",
                correlation_id=cid,
                success=False,
                errors=[str(e)],
            )

        return result

    def get_result(self, result_id: str) -> RecommendationResult | None:
        """Retrieve a recommendation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            RecommendationResult if found, None otherwise.
        """
        if self.db_session is not None:
            rec = _db_get_all_recommendations(self.db_session)
            for r in rec:
                if str(r.get("entity_id", "")) == result_id or str(r.get("id", "")) == result_id:
                    return RecommendationResult(
                        request_id=result_id,
                        status=RecommendationStatus(r.get("status", "completed")),
                    )
        return None

    def _db_recommendation_count(self) -> int:
        if self.db_session is not None:
            return len(_db_get_all_recommendations(self.db_session))
        return 0

    def health(self) -> RecommendationHealth:
        """Get the health status of all sub-components.

        Returns:
            RecommendationHealth with component statuses.
        """
        db_count = self._db_recommendation_count()
        return RecommendationHealth(
            overall_status="HEALTHY",
            coordinator_status="HEALTHY",
            generator_status="HEALTHY",
            ranker_status="HEALTHY",
            validator_status="HEALTHY",
            policy_engine_status="HEALTHY",
            session_manager_status="HEALTHY",
            confidence_calculator_status="HEALTHY",
            review_status="HEALTHY",
            version_manager_status="HEALTHY",
            readiness_status="HEALTHY",
            lineage_status="HEALTHY",
            snapshot_status="HEALTHY",
            portfolio_comparator_status="HEALTHY",
            quality_status="HEALTHY",
            justification_status="HEALTHY",
            approval_readiness_status="HEALTHY",
            portfolio_quality_status="HEALTHY",
            hooks_status="HEALTHY",
            recommendation_count=db_count,
            error_count=0,
            average_latency_ms=0.0,
        )

    def metrics(self) -> RecommendationMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            RecommendationMetrics with current values.
        """
        db_count = self._db_recommendation_count()
        return RecommendationMetrics(
            recommendation_total=db_count,
            candidates_total=0,
            decisions_total=0,
            packages_total=0,
            validated_total=0,
            failed_total=0,
            average_confidence=0.0,
            sessions_total=self.session_manager.count(),
            reviews_total=0,
            versions_created=self.version_manager.count(),
            snapshots_taken=self.snapshot.count(),
            readiness_ready=0,
            readiness_blocked=0,
            average_business_score=0.0,
            average_feasibility=0.0,
            quality_total=self.metrics_collector._quality_assessments if hasattr(self.metrics_collector, '_quality_assessments') else 0,
            justifications_total=self.metrics_collector._justifications_created if hasattr(self.metrics_collector, '_justifications_created') else 0,
            approval_readiness_ready=self.metrics_collector._approval_readiness_ready if hasattr(self.metrics_collector, '_approval_readiness_ready') else 0,
            approval_readiness_review_required=self.metrics_collector._approval_readiness_review_required if hasattr(self.metrics_collector, '_approval_readiness_review_required') else 0,
            approval_readiness_blocked=self.metrics_collector._approval_readiness_blocked if hasattr(self.metrics_collector, '_approval_readiness_blocked') else 0,
            average_quality=round(sum(self.metrics_collector._quality_scores) / len(self.metrics_collector._quality_scores), 4) if hasattr(self.metrics_collector, '_quality_scores') and self.metrics_collector._quality_scores else 0.0,
            portfolios_quality_total=self.metrics_collector._portfolio_quality_assessments if hasattr(self.metrics_collector, '_portfolio_quality_assessments') else 0,
        )
