"""PlannerAgent — central orchestrator for the planning pipeline."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

import structlog

from adip.planner.contracts.events import (
    CapabilitiesMatched,
    ContextAnalyzed,
    GoalAnalyzed,
    PlanGenerated,
    PlanningCompleted,
    PlanningFailed,
    PlanningStarted,
    PlanOptimized,
    PlanValidated,
    StrategySelected,
    TasksDecomposed,
)
from adip.planner.contracts.models import (
    ExecutionPlan,
    PlanningContext,
    PlanningDecision,
    PlanningGoal,
    PlanningRequest,
    PlanningResult,
    PlanningTask,
    PlanningTrace,
)
from adip.planner.contracts.policy import PlanningPolicy
from adip.planner.enums import PlanningStatusEnum
from adip.planner.interfaces.pipeline import (
    CapabilityMatcher,
    ConfidenceCalculator,
    ContextAnalyzer,
    ExecutionDispatcher,
    GoalAnalyzer,
    PlanGenerator,
    PlannerInterface,
    PlanOptimizer,
    PlanValidator,
    Replanner,
    StrategySelector,
    TaskDecomposer,
)

log = structlog.get_logger(__name__)

PLANNER_VERSION = "0.1.0"


class PlannerAgent(PlannerInterface):
    """Orchestrates the full planning pipeline via dependency injection.

    Pipeline order (state transitions in ``PlanningResult.execution_status``):
      1. CREATED → ANALYZING   — goal & context analysis
      2. ANALYZING → PLANNING   — strategy selection + task decomposition
      3. PLANNING → VALIDATING  — plan validation
      4. VALIDATING → OPTIMIZING — confidence + optimisation
      5. OPTIMIZING → EXECUTING — dispatch tasks (placeholder)
      6. EXECUTING → COMPLETED  — finalise result
      * Any step → FAILED       — on unhandled exception

    Each pipeline stage emits a ``PlannerEvent`` and records a
    ``PlanningTrace`` for observability.
    """

    def __init__(
        self,
        goal_analyzer: GoalAnalyzer,
        context_analyzer: ContextAnalyzer,
        strategy_selector: StrategySelector,
        capability_matcher: CapabilityMatcher,
        task_decomposer: TaskDecomposer,
        plan_generator: PlanGenerator,
        plan_validator: PlanValidator,
        confidence_calculator: ConfidenceCalculator,
        plan_optimizer: PlanOptimizer,
        execution_dispatcher: ExecutionDispatcher,
        replanner: Replanner,
        policy: PlanningPolicy | None = None,
    ) -> None:
        self._goal_analyzer = goal_analyzer
        self._context_analyzer = context_analyzer
        self._strategy_selector = strategy_selector
        self._capability_matcher = capability_matcher
        self._task_decomposer = task_decomposer
        self._plan_generator = plan_generator
        self._plan_validator = plan_validator
        self._confidence_calculator = confidence_calculator
        self._plan_optimizer = plan_optimizer
        self._execution_dispatcher = execution_dispatcher
        self._replanner = replanner
        self._policy = policy or PlanningPolicy()

    # ── Public API ─────────────────────────────────────────────────────

    async def plan(self, request: PlanningRequest) -> PlanningResult:
        return await self.create_plan(request)

    async def create_plan(self, request: PlanningRequest) -> PlanningResult:
        correlation_id = str(uuid.uuid4())
        result = PlanningResult(
            request_id=uuid.uuid4(),
            execution_status=PlanningStatusEnum.CREATED,
        )
        start_time = time.monotonic()
        bound_log = log.bind(
            goal=request.goal.objective[:60],
            correlation_id=correlation_id,
        )
        events: list = []
        traces: list[PlanningTrace] = []

        try:
            events.append(PlanningStarted(
                goal=request.goal,
                context=request.context,
                request_id=result.request_id,
                correlation_id=correlation_id,
            ))

            # ── 1. ANALYZE ────────────────────────────────────────────
            result.execution_status = PlanningStatusEnum.ANALYZING
            bound_log.info("planner.state.analyzing")

            goal, goal_trace = await self._trace_stage(
                "goal_analyzer",
                lambda: self._goal_analyzer.analyze(request.goal),
                input_summary={"objective": request.goal.objective[:80]},
                correlation_id=correlation_id,
            )
            traces.append(goal_trace)
            events.append(GoalAnalyzed(
                trace=goal_trace, request_id=result.request_id,
                correlation_id=correlation_id,
            ))
            bound_log.debug(
                "planner.goal_analyzed", domain=goal.domain, intent=goal.intent,
            )

            context, ctx_trace = await self._trace_stage(
                "context_analyzer",
                lambda: self._context_analyzer.analyze(goal, request.context),
                input_summary={"capabilities": request.context.available_capabilities},
                correlation_id=correlation_id,
            )
            traces.append(ctx_trace)
            events.append(ContextAnalyzed(
                trace=ctx_trace,
                enriched_capabilities=context.available_capabilities,
                request_id=result.request_id,
                correlation_id=correlation_id,
            ))
            bound_log.debug(
                "planner.context_analyzed", capabilities=context.available_capabilities,
            )

            strategy, strat_trace = await self._trace_stage(
                "strategy_selector",
                lambda: self._strategy_selector.select(goal, context),
                correlation_id=correlation_id,
            )
            traces.append(strat_trace)
            goal.selected_strategy = strategy
            events.append(StrategySelected(
                strategy=strategy, trace=strat_trace,
                request_id=result.request_id, correlation_id=correlation_id,
            ))
            bound_log.debug("planner.strategy_selected", strategy=strategy.value)

            result.metrics.capabilities_considered = len(context.available_capabilities)

            # ── 2. PLAN ───────────────────────────────────────────────
            result.execution_status = PlanningStatusEnum.PLANNING
            bound_log.info("planner.state.planning")

            tasks, decomp_trace = await self._trace_stage(
                "task_decomposer",
                lambda: self._task_decomposer.decompose(goal, context),
                correlation_id=correlation_id,
            )
            traces.append(decomp_trace)
            events.append(TasksDecomposed(
                tasks=tasks, trace=decomp_trace,
                request_id=result.request_id, correlation_id=correlation_id,
            ))
            bound_log.debug("planner.tasks_decomposed", task_count=len(tasks))

            tasks = await self._match_capabilities(tasks, context)
            result.metrics.capabilities_matched = sum(
                len(t.matched_capabilities) for t in tasks
            )
            events.append(CapabilitiesMatched(
                task_capability_pairs=[
                    {"task_id": str(t.task_id), "matches": len(t.matched_capabilities)}
                    for t in tasks
                ],
                trace=PlanningTrace(
                    stage_name="capability_matcher", success=True,
                    planner_version=PLANNER_VERSION, correlation_id=correlation_id,
                ),
                request_id=result.request_id, correlation_id=correlation_id,
            ))

            plan, gen_trace = await self._trace_stage(
                "plan_generator",
                lambda: self._plan_generator.generate(tasks, context, goal),
                correlation_id=correlation_id,
            )
            traces.append(gen_trace)
            plan.goal = goal
            events.append(PlanGenerated(
                plan=plan, trace=gen_trace,
                request_id=result.request_id, correlation_id=correlation_id,
            ))
            bound_log.debug("planner.plan_generated", task_count=len(plan.tasks))

            result.metrics.tasks_processed = len(plan.tasks)
            result.metrics.generated_tasks = len(plan.tasks)

            # ── 3. VALIDATE ───────────────────────────────────────────
            result.execution_status = PlanningStatusEnum.VALIDATING
            bound_log.info("planner.state.validating")

            validation, val_trace = await self._trace_stage(
                "plan_validator",
                lambda: self._plan_validator.validate(plan, context),
                correlation_id=correlation_id,
            )
            traces.append(val_trace)
            events.append(PlanValidated(
                validation=validation, trace=val_trace,
                request_id=result.request_id, correlation_id=correlation_id,
            ))
            bound_log.debug(
                "planner.plan_validated",
                is_valid=validation.is_valid,
                errors=len(validation.errors),
            )

            result.validation_status = validation
            result.metrics.validation_errors = len(validation.errors)

            if not validation.is_valid:
                result.plan = plan
                result.execution_status = PlanningStatusEnum.FAILED
                result.final_decision = PlanningDecision(
                    reasoning=f"Validation failed: {'; '.join(validation.errors)}",
                )
                elapsed = (time.monotonic() - start_time) * 1000
                result.metrics.total_planning_time = elapsed
                result.metrics.planning_duration_ms = elapsed
                result.traces = traces
                events.append(PlanningFailed(
                    error=validation.errors[0] if validation.errors else "validation_failed",
                    traces=traces, metrics=result.metrics,
                    request_id=result.request_id, correlation_id=correlation_id,
                ))
                bound_log.warning("planner.validation_failed", errors=validation.errors)
                return result

            # ── 4. OPTIMISE ───────────────────────────────────────────
            result.execution_status = PlanningStatusEnum.OPTIMIZING
            bound_log.info("planner.state.optimizing")

            confidence, conf_trace = await self._trace_stage(
                "confidence_calculator",
                lambda: self._confidence_calculator.calculate(
                    plan, validation, context, goal,
                ),
                correlation_id=correlation_id,
            )
            traces.append(conf_trace)
            plan.confidence = confidence
            bound_log.debug("planner.confidence_calculated", confidence=confidence)

            if self._policy.optimization_enabled:
                opt_plan, opt_trace = await self._trace_stage(
                    "plan_optimizer",
                    lambda: self._plan_optimizer.optimize(plan, context, goal),
                    input_summary={"task_count": len(plan.tasks)},
                    correlation_id=correlation_id,
                )
                result.metrics.optimization_percentage = (
                    (len(plan.tasks) - len(opt_plan.tasks))
                    / max(len(plan.tasks), 1)
                ) * 100.0
            else:
                opt_plan = plan
                opt_trace = PlanningTrace(
                    stage_name="plan_optimizer", success=True, duration_ms=0.0,
                    planner_version=PLANNER_VERSION, correlation_id=correlation_id,
                )
            traces.append(opt_trace)
            events.append(PlanOptimized(
                original_task_count=len(plan.tasks),
                optimized_task_count=len(opt_plan.tasks),
                optimization_reduction=(
                    (len(plan.tasks) - len(opt_plan.tasks))
                    / max(len(plan.tasks), 1)
                ),
                trace=opt_trace, request_id=result.request_id,
                correlation_id=correlation_id,
            ))
            bound_log.debug("planner.plan_optimized", task_count=len(opt_plan.tasks))

            result.metrics.planning_confidence = confidence
            result.metrics.parallel_tasks = len([
                t for t in opt_plan.tasks if t.parallelizable
            ])
            result.metrics.decisions_made = 1

            # ── 5. DISPATCH ───────────────────────────────────────────
            result.execution_status = PlanningStatusEnum.EXECUTING
            bound_log.info("planner.state.executing")

            dispatched_tasks: list[PlanningTask] = []
            for task in opt_plan.tasks:
                dispatched = await self._execution_dispatcher.dispatch(task, context)
                dispatched_tasks.append(dispatched)
            opt_plan.tasks = dispatched_tasks

            # ── 6. COMPLETE ───────────────────────────────────────────
            result.plan = opt_plan
            result.execution_status = PlanningStatusEnum.COMPLETED
            result.final_decision = PlanningDecision(
                reasoning=(
                    f"Plan completed successfully with {len(opt_plan.tasks)} tasks. "
                    f"Confidence: {confidence:.1f}/100. "
                    f"Strategy: {strategy.value}. "
                    f"Auto-execute threshold: {self._policy.auto_execute_threshold}"
                ),
            )
            elapsed = (time.monotonic() - start_time) * 1000
            result.metrics.total_planning_time = elapsed
            result.metrics.planning_duration_ms = elapsed
            result.metrics.execution_time_ms = elapsed
            result.traces = traces

            events.append(PlanningCompleted(
                plan=opt_plan,
                decision=result.final_decision,
                traces=traces, metrics=result.metrics,
                request_id=result.request_id, correlation_id=correlation_id,
            ))

            bound_log.info(
                "planner.completed",
                duration_ms=round(elapsed, 2),
                tasks=result.metrics.generated_tasks,
                confidence=confidence,
            )

            return result

        except Exception:
            bound_log.exception("planner.failed")
            result.execution_status = PlanningStatusEnum.FAILED
            elapsed = (time.monotonic() - start_time) * 1000
            result.metrics.total_planning_time = elapsed
            result.metrics.planning_duration_ms = elapsed
            result.traces = traces
            return result

    async def replan(
        self,
        original_plan: ExecutionPlan,
        current_context: PlanningContext,
        deviation_reason: str,
        goal: PlanningGoal,
    ) -> ExecutionPlan | None:
        log.info("planner.replanning", reason=deviation_reason)
        return await self._replanner.replan(
            original_plan, current_context, deviation_reason, goal,
        )

    # ── Internal helpers ───────────────────────────────────────────────

    async def _match_capabilities(
        self,
        tasks: list[PlanningTask],
        context: PlanningContext,
    ) -> list[PlanningTask]:
        matched: list[PlanningTask] = []
        for task in tasks:
            matches = await self._capability_matcher.match_capabilities(
                task.description, context,
            )
            matched.append(
                task.model_copy(update={"matched_capabilities": matches})
            )
        return matched

    async def _trace_stage(
        self,
        stage_name: str,
        fn,
        input_summary: dict | None = None,
        correlation_id: str = "",
    ) -> tuple:
        """Execute a pipeline stage, recording a PlanningTrace.

        Returns ``(output, trace)``.
        """
        start = time.monotonic()
        trace = PlanningTrace(
            stage_name=stage_name,
            input_summary=input_summary or {},
            started_at=datetime.now(UTC),
            planner_version=PLANNER_VERSION,
            correlation_id=correlation_id,
        )
        try:
            output = await fn()
            trace.success = True
            trace.completed_at = datetime.now(UTC)
            trace.duration_ms = round((time.monotonic() - start) * 1000, 2)
            trace.output_summary = self._summarize(output)
            return output, trace
        except Exception as exc:
            trace.success = False
            trace.warnings.append(str(exc))
            trace.completed_at = datetime.now(UTC)
            trace.duration_ms = round((time.monotonic() - start) * 1000, 2)
            raise

    @staticmethod
    def _summarize(value) -> dict:
        """Produce a short dict summary of a component output."""
        if value is None:
            return {"type": "none"}
        if isinstance(value, ExecutionPlan):
            return {
                "type": "ExecutionPlan",
                "task_count": len(value.tasks),
                "plan_id": str(value.plan_id),
            }
        if isinstance(value, PlanningGoal):
            return {
                "type": "PlanningGoal",
                "domain": value.domain,
                "intent": value.intent,
                "entities": len(value.entities),
            }
        if hasattr(value, "model_dump"):
            return {"type": type(value).__name__}
        if isinstance(value, list):
            task_count = sum(
                1 for v in value if isinstance(v, PlanningTask)
            )
            return {"type": "list", "length": len(value), "tasks": task_count}
        return {"type": type(value).__name__}
