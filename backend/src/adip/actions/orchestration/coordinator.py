"""ActionCoordinator — orchestrates the action planning pipeline.

Orchestrates the full action planning pipeline by delegating to
Phase 2 and Phase 3 components. Deterministic placeholder.

22-stage pipeline:
  1.  Validate request
  2.  Build execution context
  3.  Create session (INITIALIZED)
  4.  Generate plan (ActionPlanner)
  5.  Build action graph
  6.  Parallel planning (identify parallel groups)
  7.  Critical path analysis
  8.  Dependency resolution
  9.  Resource allocation
  10. Conflict detection
  11. Execution window assignment
  12. Compensation strategy
  13. Cost estimation
  14. Risk evaluation
  15. Policy validation
  16. Timeline generation
  17. Optimization
  18. Feasibility analysis
  19. Plan quality assessment
  20. Plan review
  21. Readiness assessment
  22. Build execution package
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.actions.contracts.models import (
    ActionDecision,
    ActionExplainabilityMetadata,
    ActionHealth,
    ActionMetrics,
    ActionPlan,
    ActionRequest,
)
from adip.actions.execution.action_graph import ActionGraphBuilder
from adip.actions.execution.action_planner import ActionPlanner
from adip.actions.execution.compensation_strategy import (
    CompensationStrategyManager,
)
from adip.actions.execution.conflict_detector import ResourceConflictDetector
from adip.actions.execution.cost_estimator import ActionCostEstimator
from adip.actions.execution.critical_path import CriticalPathAnalyzer
from adip.actions.execution.dependency_resolver import DependencyResolver
from adip.actions.execution.execution_window import ExecutionWindowManager
from adip.actions.execution.feasibility_analyzer import ActionFeasibilityAnalyzer
from adip.actions.execution.metrics import ActionMetrics as ExecutionMetrics
from adip.actions.execution.optimization_engine import ActionOptimizationEngine
from adip.actions.execution.parallel_planner import ParallelActionPlanner
from adip.actions.execution.policy_engine import ActionPolicyEngine
from adip.actions.execution.resource_allocator import ResourceAllocator
from adip.actions.execution.risk_evaluator import ActionRiskEvaluator
from adip.actions.execution.timeline import ExecutionTimeline
from adip.actions.execution.trace import ActionTrace
from adip.actions.orchestration.confidence import ActionConfidenceCalculator
from adip.actions.orchestration.context import ExecutionContextBuilder
from adip.actions.orchestration.execution_package import (
    ExecutionPackageBuilder,
)
from adip.actions.orchestration.health import ExecutionHealth
from adip.actions.orchestration.lineage import ActionLineage
from adip.actions.orchestration.policy_compliance import ActionPolicyCompliance
from adip.actions.orchestration.quality import PlanQualityManager
from adip.actions.orchestration.readiness import ActionExecutionReadiness
from adip.actions.orchestration.review import ActionReview
from adip.actions.orchestration.session import ActionSessionManager
from adip.actions.orchestration.snapshot import ActionSnapshot
from adip.actions.orchestration.version_manager import ActionVersionManager

log = structlog.get_logger(__name__)


class ActionCoordinator:
    """Orchestrates the full action planning pipeline.

    22-stage pipeline with per-stage timing, tracing, and
    explainability metadata generation.
    """

    def __init__(
        self,
        session_manager: ActionSessionManager | None = None,
        context_builder: ExecutionContextBuilder | None = None,
        planner: ActionPlanner | None = None,
        graph_builder: ActionGraphBuilder | None = None,
        parallel_planner: ParallelActionPlanner | None = None,
        critical_path: CriticalPathAnalyzer | None = None,
        dependency_resolver: DependencyResolver | None = None,
        resource_allocator: ResourceAllocator | None = None,
        conflict_detector: ResourceConflictDetector | None = None,
        execution_window: ExecutionWindowManager | None = None,
        compensation_strategy: CompensationStrategyManager | None = None,
        cost_estimator: ActionCostEstimator | None = None,
        risk_evaluator: ActionRiskEvaluator | None = None,
        policy_engine: ActionPolicyEngine | None = None,
        timeline: ExecutionTimeline | None = None,
        optimization_engine: ActionOptimizationEngine | None = None,
        feasibility_analyzer: ActionFeasibilityAnalyzer | None = None,
        quality_manager: PlanQualityManager | None = None,
        review: ActionReview | None = None,
        readiness: ActionExecutionReadiness | None = None,
        package_builder: ExecutionPackageBuilder | None = None,
        confidence_calculator: ActionConfidenceCalculator | None = None,
        version_manager: ActionVersionManager | None = None,
        lineage: ActionLineage | None = None,
        snapshot: ActionSnapshot | None = None,
        policy_compliance: ActionPolicyCompliance | None = None,
        health: ExecutionHealth | None = None,
        metrics_collector: ExecutionMetrics | None = None,
        trace: ActionTrace | None = None,
    ) -> None:
        self.session_manager = session_manager or ActionSessionManager()
        self.context_builder = context_builder or ExecutionContextBuilder()
        self.planner = planner or ActionPlanner()
        self.graph_builder = graph_builder or ActionGraphBuilder()
        self.parallel_planner = parallel_planner or ParallelActionPlanner()
        self.critical_path = critical_path or CriticalPathAnalyzer()
        self.dependency_resolver = dependency_resolver or DependencyResolver()
        self.resource_allocator = resource_allocator or ResourceAllocator()
        self.conflict_detector = conflict_detector or ResourceConflictDetector()
        self.execution_window = execution_window or ExecutionWindowManager()
        self.compensation_strategy = compensation_strategy or CompensationStrategyManager()
        self.cost_estimator = cost_estimator or ActionCostEstimator()
        self.risk_evaluator = risk_evaluator or ActionRiskEvaluator()
        self.policy_engine = policy_engine or ActionPolicyEngine()
        self.timeline = timeline or ExecutionTimeline()
        self.optimization_engine = optimization_engine or ActionOptimizationEngine()
        self.feasibility_analyzer = feasibility_analyzer or ActionFeasibilityAnalyzer()
        self.quality_manager = quality_manager or PlanQualityManager()
        self.review = review or ActionReview()
        self.readiness = readiness or ActionExecutionReadiness()
        self.package_builder = package_builder or ExecutionPackageBuilder()
        self.confidence_calculator = confidence_calculator or ActionConfidenceCalculator()
        self.version_manager = version_manager or ActionVersionManager()
        self.lineage = lineage or ActionLineage()
        self.snapshot = snapshot or ActionSnapshot()
        self.policy_compliance = policy_compliance or ActionPolicyCompliance()
        self._health = health or ExecutionHealth()
        self.metrics_collector = metrics_collector or ExecutionMetrics()
        self.trace = trace or ActionTrace()
        self._decisions: dict[str, ActionDecision] = {}

    def plan(
        self,
        request: ActionRequest,
        correlation_id: str = "",
    ) -> ActionDecision:
        """Execute the full action planning pipeline.

        Args:
            request: The action request to plan.
            correlation_id: Optional correlation ID.

        Returns:
            ActionDecision with the complete planning result.
        """
        cid = correlation_id or str(uuid.uuid4())
        start_time = datetime.now(UTC)
        request_id = str(request.request_id)

        log.info("coordinator.plan.start", request_id=request_id, cid=cid)

        # Stage 1: Validate request
        t1 = datetime.now(UTC)
        issues: list[str] = []
        warnings: list[str] = []
        if not request.review_decision_id:
            issues.append("Missing review_decision_id")
        if not request.action_type:
            issues.append("Missing action_type")
        self.trace.record_stage("validate_request", plan_id=request_id, correlation_id=cid, success=len(issues) == 0)
        self._health.record_latency((datetime.now(UTC) - t1).total_seconds() * 1000)

        # Stage 2: Build execution context
        t2 = datetime.now(UTC)
        context = self.context_builder.build(request, correlation_id=cid)
        self.trace.record_stage("build_context", plan_id=request_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t2).total_seconds() * 1000)

        # Stage 3: Create session (INITIALIZED)
        t3 = datetime.now(UTC)
        session = self.session_manager.create_session(
            request_id=request_id,
            action_type=str(request.action_type),
            priority=str(request.priority),
        )
        self.trace.record_stage("create_session", plan_id=request_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t3).total_seconds() * 1000)

        # Stage 4: Generate plan
        t4 = datetime.now(UTC)
        plan = self.planner.generate_plan(request, correlation_id=cid)
        plan_id = str(plan.plan_id)
        plan_has_rollback = plan.rollback_plan is not None
        self.session_manager.update_session(
            str(session.session_id),
            plan_id=plan_id,
            step_count=len(plan.steps),
            has_rollback=plan_has_rollback,
        )
        self.session_manager.update_status(str(session.session_id), "PLANNING")
        self.trace.record_stage("generate_plan", plan_id=plan_id, correlation_id=cid, details=f"Steps: {len(plan.steps)}")
        self._health.record_latency((datetime.now(UTC) - t4).total_seconds() * 1000)

        # Stage 5: Build action graph
        t5 = datetime.now(UTC)
        step_ids = [str(s.step_id) for s in plan.steps]
        deps = []
        for s in plan.steps:
            for dep_id in s.dependencies:
                deps.append((str(dep_id), str(s.step_id), "hard"))
        graph = self.graph_builder.build_graph(
            plan_id=str(plan.plan_id),
            step_ids=step_ids,
            dependencies=deps,
            correlation_id=cid,
        )
        self.trace.record_stage("build_graph", plan_id=plan_id, correlation_id=cid, details=f"Nodes: {len(graph.nodes)}")
        self._health.record_latency((datetime.now(UTC) - t5).total_seconds() * 1000)
        if not graph.is_dag:
            issues.append("Action graph contains cycles")

        # Stage 6: Parallel planning
        t6 = datetime.now(UTC)
        parallel_groups = self.parallel_planner.identify_parallel_groups(graph, correlation_id=cid)
        self.trace.record_stage("parallel_planning", plan_id=plan_id, correlation_id=cid, details=f"Groups: {len(parallel_groups)}")
        self._health.record_latency((datetime.now(UTC) - t6).total_seconds() * 1000)

        # Stage 7: Critical path analysis
        t7 = datetime.now(UTC)
        critical_path = self.critical_path.analyze(graph, correlation_id=cid)
        self.trace.record_stage("critical_path", plan_id=plan_id, correlation_id=cid, details=f"Duration: {critical_path.total_duration_minutes}min")
        self._health.record_latency((datetime.now(UTC) - t7).total_seconds() * 1000)

        # Stage 8: Dependency resolution
        t8 = datetime.now(UTC)
        dep_resolution = self.dependency_resolver.resolve_dependencies(
            plan_id=plan_id,
            step_ids=step_ids,
            dependencies=deps,
            correlation_id=cid,
        )
        self.trace.record_stage("dependency_resolution", plan_id=plan_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t8).total_seconds() * 1000)

        # Stage 9: Resource allocation
        t9 = datetime.now(UTC)
        allocation = self.resource_allocator.allocate_resources(
            plan_id=plan_id,
            step_ids=step_ids,
            correlation_id=cid,
        )
        self.trace.record_stage("resource_allocation", plan_id=plan_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t9).total_seconds() * 1000)

        # Stage 13: Cost estimation
        t13 = datetime.now(UTC)
        cost = self.cost_estimator.estimate_costs(
            plan_id=plan_id,
            step_count=len(plan.steps),
            step_ids=[str(s.step_id) for s in plan.steps],
            correlation_id=cid,
        )
        self.trace.record_stage("cost_estimation", plan_id=plan_id, correlation_id=cid, details=f"Cost: ${cost.total_cost:.2f}")
        self._health.record_latency((datetime.now(UTC) - t13).total_seconds() * 1000)
        total_cost = cost.total_cost

        # Stage 14: Risk evaluation
        t14 = datetime.now(UTC)
        risk = self.risk_evaluator.evaluate(
            plan_id=plan_id,
            action_type=str(request.action_type),
            priority=str(request.priority),
            step_count=len(plan.steps),
            domain=request.domain,
            correlation_id=cid,
        )
        self.trace.record_stage("risk_evaluation", plan_id=plan_id, correlation_id=cid, details=f"Risk: {risk.overall_risk}")
        self._health.record_latency((datetime.now(UTC) - t14).total_seconds() * 1000)
        overall_risk = risk.overall_risk

        # Stage 15: Policy validation
        t15 = datetime.now(UTC)
        policy_result = self.policy_engine.validate(
            plan_id=plan_id,
            action_type=str(request.action_type),
            priority=str(request.priority),
            domain=request.domain,
            step_count=len(plan.steps),
            correlation_id=cid,
        )
        if not policy_result.is_policy_compliant:
            warnings.append(f"Policy violations: {policy_result.total_violations}")
        self.trace.record_stage("policy_validation", plan_id=plan_id, correlation_id=cid, details=f"Compliant: {policy_result.is_policy_compliant}")
        self._health.record_latency((datetime.now(UTC) - t15).total_seconds() * 1000)

        # Stage 16: Timeline generation
        t16 = datetime.now(UTC)
        timeline_entries = self.timeline.generate(
            plan_id=plan_id,
            graph=graph,
            parallel_groups=parallel_groups,
            critical_path=critical_path,
            correlation_id=cid,
        )
        self.trace.record_stage("timeline_generation", plan_id=plan_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t16).total_seconds() * 1000)

        # Stage 17: Optimization
        t17 = datetime.now(UTC)
        optimized = self.optimization_engine.optimize(
            plan_id=plan_id,
            cost_estimate=cost,
            critical_path=critical_path,
            step_count=len(plan.steps),
            correlation_id=cid,
        )
        self.trace.record_stage("optimization", plan_id=plan_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t17).total_seconds() * 1000)

        # Stage 18: Feasibility analysis
        t18 = datetime.now(UTC)
        feasibility = self.feasibility_analyzer.analyze(
            plan_id=plan_id,
            allocation=allocation,
            step_count=len(plan.steps),
            correlation_id=cid,
        )
        if not feasibility.is_feasible:
            issues.extend(feasibility.issues)
        self.trace.record_stage("feasibility_analysis", plan_id=plan_id, correlation_id=cid, details=f"Feasible: {feasibility.is_feasible}")
        self._health.record_latency((datetime.now(UTC) - t18).total_seconds() * 1000)

        has_resources = allocation is not None and (allocation.total_personnel > 0 or allocation.total_equipment > 0)
        has_schedule = plan.schedule is not None

        # Stage 19: Plan quality assessment
        t19 = datetime.now(UTC)
        quality = self.quality_manager.assess(
            plan_id=plan_id,
            step_count=len(plan.steps),
            has_dependencies=len(plan.dependencies) > 0,
            has_resources=has_resources,
            has_schedule=has_schedule,
            has_rollback=plan_has_rollback,
            has_preconditions=any(s.preconditions for s in plan.steps),
            has_postconditions=any(s.postconditions for s in plan.steps),
            correlation_id=cid,
        )
        self.trace.record_stage("quality_assessment", plan_id=plan_id, correlation_id=cid, details=f"Quality: {quality.overall_quality}")
        self._health.record_latency((datetime.now(UTC) - t19).total_seconds() * 1000)

        # Stage 20: Plan review
        t20 = datetime.now(UTC)
        review_result = self.review.review(
            plan_id=plan_id,
            step_count=len(plan.steps),
            has_dependencies=len(plan.dependencies) > 0,
            has_resources=has_resources,
            has_schedule=has_schedule,
            has_rollback=plan_has_rollback,
            has_preconditions=any(s.preconditions for s in plan.steps),
            correlation_id=cid,
        )
        if not review_result.passed:
            issues.extend(review_result.issues)
        self.trace.record_stage("plan_review", plan_id=plan_id, correlation_id=cid, details=f"Score: {review_result.overall_score}, Passed: {review_result.passed}")
        self._health.record_latency((datetime.now(UTC) - t20).total_seconds() * 1000)

        # Stage 21: Readiness assessment
        t21 = datetime.now(UTC)
        resources_available = has_resources
        deps_satisfied = all(d.satisfied for d in plan.dependencies) if plan.dependencies else True
        schedule_feasible = has_schedule
        policy_compliant = policy_result.is_policy_compliant
        risk_accepted = overall_risk in ("LOW", "MEDIUM")

        readiness_assessment = self.readiness.assess(
            plan_id=plan_id,
            resources_available=resources_available,
            dependencies_satisfied=deps_satisfied,
            schedule_feasible=schedule_feasible,
            policy_compliant=policy_compliant,
            risk_accepted=risk_accepted,
            correlation_id=cid,
        )
        self.trace.record_stage("readiness_assessment", plan_id=plan_id, correlation_id=cid, details=f"Status: {readiness_assessment.status}, Score: {readiness_assessment.score}")
        self._health.record_latency((datetime.now(UTC) - t21).total_seconds() * 1000)

        # Stage 22: Build execution package
        t22 = datetime.now(UTC)
        pkg = self.package_builder.build(
            plan_id=plan_id,
            step_count=len(plan.steps),
            has_rollback=plan_has_rollback,
            readiness_score=readiness_assessment.score,
            correlation_id=cid,
        )
        self.trace.record_stage("build_execution_package", plan_id=plan_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t22).total_seconds() * 1000)

        # Calculate confidence
        confidence = self.confidence_calculator.calculate(
            resource_confidence=0.8 if resources_available else 0.3,
            schedule_confidence=0.8 if schedule_feasible else 0.3,
            cost_confidence=0.75,
            risk_confidence=0.8 if risk_accepted else 0.4,
            feasibility_confidence=0.8 if feasibility.is_feasible else 0.3,
            quality_score=quality.overall_quality,
        )

        # Create version
        self.version_manager.create_version(plan_id, correlation_id=cid)

        # Record lineage
        self.lineage.record(
            request_id=request_id,
            plan_id=plan_id,
            session_id=str(session.session_id),
            stage="planning_complete",
            summary=f"Plan generated with {len(plan.steps)} steps, readiness={readiness_assessment.status}",
            correlation_id=cid,
        )

        # Create snapshot
        self.snapshot.create_snapshot(
            plan_id=plan_id,
            request_id=request_id,
            session_id=str(session.session_id),
            step_count=len(plan.steps),
            readiness_score=readiness_assessment.score,
            quality_score=quality.overall_quality,
            confidence_score=confidence.overall_confidence,
            correlation_id=cid,
        )

        # Explainability metadata
        explainability = ActionExplainabilityMetadata(
            why_plan_generated=f"Plan generated for {request.action_type} action in domain {request.domain}",
            why_step_ordered=f"Steps ordered by dependencies with {len(parallel_groups)} parallel groups",
            why_resource_allocated=f"Resources allocated: {allocation.total_personnel if allocation else 0} personnel",
            why_schedule_chosen=f"Schedule: {plan.schedule.schedule_window if plan.schedule else 'immediate'}",
            why_readiness_assessed=f"Readiness: {readiness_assessment.status} ({readiness_assessment.score:.2f})",
            why_rollback_configured=f"Rollback: {'configured' if plan_has_rollback else 'not configured'}",
            why_optimization_applied="Optimization applied: cost savings, duration reduction",
        )

        # Complete session
        self.session_manager.update_session(
            str(session.session_id),
            decision_id=str(session.session_id),
        )
        self.session_manager.update_status(str(session.session_id), "COMPLETED")

        # Record metrics
        self.metrics_collector.record_plan(action_type=str(request.action_type), step_count=len(plan.steps))
        total_time_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
        self._health.record_plan()
        self._health.record_latency(total_time_ms)

        is_ready = readiness_assessment.status.value == "READY"
        decision = ActionDecision(
            request_id=request.request_id,
            plan=plan,
            readiness=readiness_assessment.status,
            readiness_reason=readiness_assessment.reason,
            is_ready=is_ready,
            issues=issues,
            warnings=warnings,
            confidence=confidence,
            explainability=explainability,
            quality_score=round(quality.overall_quality, 4),
            readiness_score=readiness_assessment.score,
        )
        self._decisions[str(decision.decision_id)] = decision

        log.info(
            "coordinator.plan.complete",
            request_id=request_id,
            decision_id=str(decision.decision_id),
            ready=is_ready,
            issues=len(issues),
            latency_ms=round(total_time_ms, 2),
        )
        return decision

    def get_decision(self, decision_id: str) -> ActionDecision | None:
        """Retrieve a decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ActionDecision if found, None otherwise.
        """
        return self._decisions.get(decision_id)

    def get_plan(self, plan_id: str) -> ActionPlan | None:
        """Retrieve a plan by ID.

        Args:
            plan_id: The plan identifier.

        Returns:
            ActionPlan if found, None otherwise.
        """
        for decision in self._decisions.values():
            if decision.plan and str(decision.plan.plan_id) == plan_id:
                return decision.plan
        return None

    def health(self) -> ActionHealth:
        """Get comprehensive health status.

        Returns:
            ActionHealth with all component statuses.
        """
        return self._health.get_health()

    def metrics(self) -> ActionMetrics:
        """Get aggregated metrics.

        Returns:
            ActionMetrics with current values.
        """
        snapshot = self.metrics_collector.snapshot()
        confidences = self.confidence_calculator.get_history()
        avg_conf = (
            sum(c.overall_confidence for c in confidences) / len(confidences)
            if confidences else 0.0
        )
        qualities = self.quality_manager.get_all_assessments()
        avg_qual = (
            sum(a.overall_quality for a in qualities) / len(qualities)
            if qualities else 0.0
        )

        decisions = list(self._decisions.values())
        plans_with_rb = sum(1 for d in decisions if d.plan and d.plan.rollback_plan)
        avg_steps = (
            sum(len(d.plan.steps) for d in decisions if d.plan) / len(decisions)
            if decisions else 0.0
        )

        all_versions = 0
        for p_id in set(
            str(d.plan.plan_id) for d in decisions if d.plan
        ):
            all_versions += len(self.version_manager.get_versions(p_id))

        plan_snapshots = sum(
            len(self.snapshot.get_snapshots_for_plan(str(d.plan.plan_id)))
            for d in decisions if d.plan
        )

        return ActionMetrics(
            plans_total=snapshot.plans_total,
            plans_ready=len([d for d in decisions if d.is_ready]),
            plans_blocked=len([d for d in decisions if not d.is_ready]),
            plans_with_rollback=plans_with_rb,
            average_steps_per_plan=round(avg_steps, 2),
            average_planning_time_ms=self._health.get_health().average_planning_time_ms,
            plans_per_action_type=snapshot.plans_per_action_type,
            sessions_total=self.session_manager.count(),
            readiness_total=len(self.readiness.get_all_assessments()),
            optimizations_total=len(snapshot.optimization_scores),
            reviews_total=len(self.review.get_all_reviews()),
            versions_total=all_versions,
            snapshots_total=plan_snapshots,
            average_confidence=round(avg_conf, 4),
            average_quality=round(avg_qual, 4),
        )
