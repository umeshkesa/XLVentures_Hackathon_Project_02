"""ExecutionCoordinatorImpl — orchestrates the execution pipeline.

Orchestrates the full execution pipeline by delegating to
Phase 2 and Phase 3 components. Deterministic placeholder.

Enhanced in Phase 3.5 with 5 additional stages:
  19. Execute compliance validation
  20. Execute recovery orchestration
  21. Collect diagnostics
  22. Generate recovery report
  23. Generate export profiles

Previously 18-stage pipeline:
  1.  Validate request
  2.  Build execution context
  3.  Create session (PENDING)
  4.  Build execution graph
  5.  Validate tasks
  6.  Check policy compliance
  7.  Build manifest
  8.  Check adapter availability
  9.  Assess readiness
  10. Execute tasks
  11. Handle retries
  12. Execute compensation (if needed)
  13. Review execution
  14. Assess quality
  15. Calculate confidence
  16. Create snapshot
  17. Record lineage
  18. Build decision

Phase 3.5 additions (23-stage pipeline):
  19. Compliance validation
  20. Recovery orchestration
  21. Diagnostics collection
  22. Recovery report generation
  23. Export generation
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.execution.contracts.models import (
    ExecutionDecision,
    ExecutionExplainabilityMetadata,
    ExecutionHealth,
    ExecutionMetrics,
    ExecutionPackage,
    ExecutionRequest,
    ExecutionResult,
    ExecutionSession,
)
from adip.execution.enums import ExecutionState
from adip.execution.execution.audit_trail import AuditTrail
from adip.execution.execution.checkpoint_manager import CheckpointManager
from adip.execution.execution.compensation_manager import CompensationManager
from adip.execution.execution.event_bus import RuntimeEventBus
from adip.execution.execution.execution_graph import ExecutionGraph
from adip.execution.execution.export_profiles import ExecutionExportProfiles
from adip.execution.execution.failure_classifier import FailureClassifier
from adip.execution.execution.metrics import ExecutionMetricsCollector
from adip.execution.execution.monitor import ExecutionMonitor
from adip.execution.execution.parallel_executor import ParallelTaskExecutor
from adip.execution.execution.pipeline_version import ExecutionPipelineVersion
from adip.execution.execution.policy_engine import ExecutionPolicyEngine
from adip.execution.execution.progress_tracker import ExecutionProgressTracker
from adip.execution.execution.readiness_report import ExecutionReadinessReport
from adip.execution.execution.report import ExecutionReportGenerator
from adip.execution.execution.resource_monitor import ResourceMonitor
from adip.execution.execution.retry_manager import RetryManager
from adip.execution.execution.runtime_diagnostics import RuntimeDiagnostics
from adip.execution.execution.scheduler import ExecutionScheduler
from adip.execution.execution.state_machine import ExecutionStateMachine
from adip.execution.execution.telemetry import ExecutionTelemetry
from adip.execution.execution.trace import ExecutionTrace
from adip.execution.orchestration.adapter_registry import ExecutionAdapterRegistry
from adip.execution.orchestration.audit_package import ExecutionAuditPackage
from adip.execution.orchestration.compliance import ExecutionComplianceManager
from adip.execution.orchestration.confidence import ExecutionConfidenceCalculator
from adip.execution.orchestration.context import ExecutionContextManager
from adip.execution.orchestration.health import ExecutionHealthManager
from adip.execution.orchestration.lineage import ExecutionLineage
from adip.execution.orchestration.manifest import ExecutionManifestBuilder
from adip.execution.orchestration.quality import ExecutionQualityManager
from adip.execution.orchestration.readiness import ExecutionReadinessManager
from adip.execution.orchestration.recovery_orchestrator import ExecutionRecoveryOrchestrator
from adip.execution.orchestration.review import ExecutionReview
from adip.execution.orchestration.session import ExecutionSessionManager
from adip.execution.orchestration.snapshot import ExecutionSnapshot
from adip.execution.orchestration.version_manager import ExecutionVersionManager

log = structlog.get_logger(__name__)


class ExecutionCoordinatorImpl:
    """Orchestrates the full execution pipeline.

    23-stage pipeline (18 original + 5 Phase 3.5) with per-stage
    timing, tracing, and explainability metadata generation.
    """

    def __init__(
        self,
        session_manager: ExecutionSessionManager | None = None,
        context_manager: ExecutionContextManager | None = None,
        graph: ExecutionGraph | None = None,
        executor: ParallelTaskExecutor | None = None,
        policy_engine: ExecutionPolicyEngine | None = None,
        retry_manager: RetryManager | None = None,
        compensation_manager: CompensationManager | None = None,
        scheduler: ExecutionScheduler | None = None,
        checkpoint_manager: CheckpointManager | None = None,
        failure_classifier: FailureClassifier | None = None,
        progress_tracker: ExecutionProgressTracker | None = None,
        monitor: ExecutionMonitor | None = None,
        audit_trail: AuditTrail | None = None,
        telemetry: ExecutionTelemetry | None = None,
        resource_monitor: ResourceMonitor | None = None,
        event_bus: RuntimeEventBus | None = None,
        state_machine: ExecutionStateMachine | None = None,
        report_generator: ExecutionReportGenerator | None = None,
        trace: ExecutionTrace | None = None,
        metrics_collector: ExecutionMetricsCollector | None = None,
        manifest_builder: ExecutionManifestBuilder | None = None,
        adapter_registry: ExecutionAdapterRegistry | None = None,
        readiness: ExecutionReadinessManager | None = None,
        review: ExecutionReview | None = None,
        quality: ExecutionQualityManager | None = None,
        confidence_calculator: ExecutionConfidenceCalculator | None = None,
        version_manager: ExecutionVersionManager | None = None,
        lineage: ExecutionLineage | None = None,
        snapshot: ExecutionSnapshot | None = None,
        health_manager: ExecutionHealthManager | None = None,
        # Phase 3.5 components
        compliance: ExecutionComplianceManager | None = None,
        audit_package: ExecutionAuditPackage | None = None,
        recovery_orchestrator: ExecutionRecoveryOrchestrator | None = None,
        diagnostics: RuntimeDiagnostics | None = None,
        readiness_report: ExecutionReadinessReport | None = None,
        export_profiles: ExecutionExportProfiles | None = None,
        pipeline_version: ExecutionPipelineVersion | None = None,
    ) -> None:
        self.session_manager = session_manager or ExecutionSessionManager()
        self.context_manager = context_manager or ExecutionContextManager()
        self.graph = graph or ExecutionGraph()
        self.executor = executor or ParallelTaskExecutor()
        self.policy_engine = policy_engine or ExecutionPolicyEngine()
        self.retry_manager = retry_manager or RetryManager()
        self.compensation_manager = compensation_manager or CompensationManager()
        self.scheduler = scheduler or ExecutionScheduler()
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.failure_classifier = failure_classifier or FailureClassifier()
        self.progress_tracker = progress_tracker or ExecutionProgressTracker()
        self.monitor = monitor or ExecutionMonitor()
        self.audit_trail = audit_trail or AuditTrail()
        self.telemetry = telemetry or ExecutionTelemetry()
        self.resource_monitor = resource_monitor or ResourceMonitor()
        self.event_bus = event_bus or RuntimeEventBus()
        self.state_machine = state_machine or ExecutionStateMachine()
        self.report_generator = report_generator or ExecutionReportGenerator()
        self.trace = trace or ExecutionTrace()
        self.metrics_collector = metrics_collector or ExecutionMetricsCollector()
        self.manifest_builder = manifest_builder or ExecutionManifestBuilder()
        self.adapter_registry = adapter_registry or ExecutionAdapterRegistry()
        self.readiness = readiness or ExecutionReadinessManager()
        self.review = review or ExecutionReview()
        self.quality = quality or ExecutionQualityManager()
        self.confidence_calculator = confidence_calculator or ExecutionConfidenceCalculator()
        self.version_manager = version_manager or ExecutionVersionManager()
        self.lineage = lineage or ExecutionLineage()
        self.snapshot = snapshot or ExecutionSnapshot()
        self._health = health_manager or ExecutionHealthManager()
        self._decisions: dict[str, ExecutionDecision] = {}
        # Phase 3.5 components
        self.compliance = compliance or ExecutionComplianceManager()
        self.audit_package = audit_package or ExecutionAuditPackage()
        self.recovery_orchestrator = recovery_orchestrator or ExecutionRecoveryOrchestrator()
        self.diagnostics = diagnostics or RuntimeDiagnostics()
        self.readiness_report = readiness_report or ExecutionReadinessReport()
        self.export_profiles = export_profiles or ExecutionExportProfiles()
        self.pipeline_version = pipeline_version or ExecutionPipelineVersion()

    def execute(
        self,
        request: ExecutionRequest,
        correlation_id: str = "",
    ) -> ExecutionResult:
        """Execute the full execution pipeline.

        Args:
            request: The execution request to execute.
            correlation_id: Optional correlation ID.

        Returns:
            The execution result.
        """
        cid = correlation_id or str(uuid.uuid4())
        start_time = datetime.now(UTC)
        request_id = str(request.request_id)

        log.info("coordinator.execute.start", request_id=request_id, cid=cid)

        # Stage 1: Validate request
        t1 = datetime.now(UTC)
        issues: list[str] = []
        warnings: list[str] = []
        if not request.action_decision_id:
            issues.append("Missing action_decision_id")
        self.trace.record_stage(
            "validate_request", session_id=request_id,
            correlation_id=cid, success=len(issues) == 0,
        )
        self._health.record_latency((datetime.now(UTC) - t1).total_seconds() * 1000)

        # Stage 2: Build execution context
        t2 = datetime.now(UTC)
        context = self.context_manager.build(request, correlation_id=cid)
        self.trace.record_stage("build_context", session_id=request_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t2).total_seconds() * 1000)

        # Stage 3: Create session (PENDING)
        t3 = datetime.now(UTC)
        session = self.session_manager.create_session(
            request_id=request_id,
            execution_mode=str(request.execution_mode),
            priority=str(request.priority),
        )
        session_id = str(session.session_id)
        self.trace.record_stage("create_session", session_id=session_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t3).total_seconds() * 1000)

        # Stage 4: Build execution graph
        t4 = datetime.now(UTC)
        task_ids = [str(uuid.uuid4()) for _ in range(3)]
        execution_graph = self.graph.build_graph(
            package_id=request_id,
            task_ids=task_ids,
            dependencies=[],
            correlation_id=cid,
        )
        self.session_manager.update_session(session_id, task_count=len(task_ids))
        self.session_manager.update_status(session_id, "RUNNING")
        self.trace.record_stage(
            "build_graph", session_id=session_id, correlation_id=cid,
            details=f"Nodes: {len(execution_graph.nodes)}",
        )
        self._health.record_latency((datetime.now(UTC) - t4).total_seconds() * 1000)
        if not execution_graph.is_dag:
            issues.append("Execution graph contains cycles")

        # Stage 5: Validate tasks
        t5 = datetime.now(UTC)
        task_issues: list[str] = []
        if not execution_graph.is_dag:
            task_issues.append("Graph has cycles")
        self.trace.record_stage(
            "validate_tasks", session_id=session_id,
            correlation_id=cid, success=len(task_issues) == 0,
        )
        self._health.record_latency((datetime.now(UTC) - t5).total_seconds() * 1000)
        if task_issues:
            warnings.extend(task_issues)

        # Stage 6: Check policy compliance
        t6 = datetime.now(UTC)
        policy_results = self.policy_engine.validate_all(
            task_type="",
            domain=request.domain,
            priority=str(request.priority),
            task_count=len(task_ids),
            task_id=task_ids[0] if task_ids else "",
            correlation_id=cid,
        )
        is_policy_compliant = all(r.is_allowed for r in policy_results)
        self.trace.record_stage(
            "policy_check", session_id=session_id, correlation_id=cid,
            details=f"Compliant: {is_policy_compliant}",
        )
        self._health.record_latency((datetime.now(UTC) - t6).total_seconds() * 1000)

        # Stage 7: Build manifest
        t7 = datetime.now(UTC)
        manifest = self.manifest_builder.build(
            package_id=request_id,
            requires_compensation=True,
            correlation_id=cid,
        )
        self.trace.record_stage("build_manifest", session_id=session_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t7).total_seconds() * 1000)

        # Stage 8: Check adapter availability
        t8 = datetime.now(UTC)
        missing_adapters: list[str] = []
        for adapter_type in manifest.required_adapters:
            if not self.adapter_registry.has_adapter(adapter_type):
                missing_adapters.append(adapter_type)
        if missing_adapters:
            warnings.append(f"Missing adapters: {missing_adapters}")
        self.trace.record_stage("check_adapters", session_id=session_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t8).total_seconds() * 1000)

        # Stage 9: Assess readiness
        t9 = datetime.now(UTC)
        resources_available = True
        deps_satisfied = execution_graph.is_dag
        schedule_feasible = True
        risk_accepted = True

        readiness_assessment = self.readiness.assess(
            session_id=session_id,
            resources_available=resources_available,
            dependencies_satisfied=deps_satisfied,
            schedule_feasible=schedule_feasible,
            policy_compliant=is_policy_compliant,
            risk_accepted=risk_accepted,
            correlation_id=cid,
        )
        self.trace.record_stage(
            "assess_readiness", session_id=session_id, correlation_id=cid,
            details=f"Status: {readiness_assessment.status}, Score: {readiness_assessment.score}",
        )
        self._health.record_latency((datetime.now(UTC) - t9).total_seconds() * 1000)

        # Stage 10: Execute tasks
        t10 = datetime.now(UTC)
        task_results = self.executor.execute_sequentially(
            task_ids=task_ids,
            session_id=session_id,
            correlation_id=cid,
        )
        completed_count = sum(1 for r in task_results.values() if r.get("success"))
        failed_count = sum(1 for r in task_results.values() if not r.get("success"))
        skipped_count = 0
        retry_count = 0

        self.session_manager.update_session(
            session_id,
            tasks_completed=completed_count,
            tasks_failed=failed_count,
        )
        self.trace.record_stage(
            "execute_tasks", session_id=session_id, correlation_id=cid,
            details=f"Completed: {completed_count}, Failed: {failed_count}",
        )
        self._health.record_latency((datetime.now(UTC) - t10).total_seconds() * 1000)

        # Stage 11: Handle retries
        t11 = datetime.now(UTC)
        if failed_count > 0:
            for tid, result in task_results.items():
                if not result.get("success"):
                    should_retry = self.retry_manager.should_retry(
                        task_id=tid,
                        attempt=1,
                        error=result.get("error", "Execution error"),
                        correlation_id=cid,
                    )
                    if should_retry:
                        retry_count += 1
        self.trace.record_stage(
            "handle_retries", session_id=session_id, correlation_id=cid,
            details=f"Retries: {retry_count}",
        )
        self._health.record_latency((datetime.now(UTC) - t11).total_seconds() * 1000)

        # Stage 12: Execute compensation (if needed)
        t12 = datetime.now(UTC)
        compensation_done = False
        if failed_count > 0:
            compensation_done = True
            for tid, result in task_results.items():
                if not result.get("success"):
                    self.compensation_manager.compensate(
                        task_id=tid,
                        session_id=session_id,
                        reason="Task failed, compensating",
                        correlation_id=cid,
                    )
        self.trace.record_stage(
            "execute_compensation", session_id=session_id, correlation_id=cid,
            details=f"Compensation: {compensation_done}",
        )
        self._health.record_latency((datetime.now(UTC) - t12).total_seconds() * 1000)

        # Stage 20: Recovery orchestration (Phase 3.5)
        t20 = datetime.now(UTC)
        recovery_result = None
        if failed_count > 0:
            failed_task_ids = [tid for tid, r in task_results.items() if not r.get("success")]
            comp_result = self.recovery_orchestrator.execute_compensation(
                session_id=session_id,
                task_ids=failed_task_ids,
                correlation_id=cid,
            )
            recovery_result = comp_result
            self.metrics_collector.record_recovery_time(comp_result.duration_ms)
            if comp_result.errors:
                warnings.extend(comp_result.errors)
        self.trace.record_recovery_report_stage(
            session_id=session_id, correlation_id=cid,
            success=True, recovery_type="compensation",
        )
        self._health.record_latency((datetime.now(UTC) - t20).total_seconds() * 1000)

        # Stage 21: Diagnostics collection (Phase 3.5)
        t21 = datetime.now(UTC)
        if failed_count > 0:
            for tid, result in task_results.items():
                if not result.get("success"):
                    self.diagnostics.record_event(
                        session_id=session_id,
                        category="task",
                        severity="ERROR",
                        message=result.get("error", "Task execution error"),
                        details={"task_id": tid},
                        correlation_id=cid,
                    )
            self.metrics_collector.record_diagnostics_event(failed_count)
        self.trace.record_diagnostics_stage(
            session_id=session_id, correlation_id=cid,
            diagnostics_count=failed_count,
        )
        self._health.record_latency((datetime.now(UTC) - t21).total_seconds() * 1000)

        # Stage 22: Recovery report generation (Phase 3.5)
        t22 = datetime.now(UTC)
        self.readiness_report.generate(
            session_id=session_id,
            resources_available=resources_available,
            dependencies_satisfied=deps_satisfied,
            schedule_feasible=schedule_feasible,
            policy_compliant=is_policy_compliant,
            risk_accepted=risk_accepted,
            correlation_id=cid,
        )
        self.trace.record_recovery_report_stage(
            session_id=session_id, correlation_id=cid,
            success=True, recovery_type="recovery",
        )
        self._health.record_latency((datetime.now(UTC) - t22).total_seconds() * 1000)

        # Complete session
        final_state = "COMPLETED" if failed_count == 0 else "FAILED"
        self.session_manager.update_status(session_id, final_state)
        self.session_manager.update_session(
            session_id,
            tasks_completed=completed_count,
            tasks_failed=failed_count,
            tasks_skipped=skipped_count,
        )

        # Stage 13: Review execution
        t13 = datetime.now(UTC)
        review_result = self.review.review(
            session_id=session_id,
            task_count=len(task_ids),
            has_dependencies=len(task_ids) > 1,
            has_resources=resources_available,
            has_compensation=True,
            correlation_id=cid,
        )
        if not review_result.passed:
            issues.extend(review_result.issues)
        self.trace.record_stage(
            "review_execution", session_id=session_id, correlation_id=cid,
            details=f"Score: {review_result.overall_score}, Passed: {review_result.passed}",
        )
        self._health.record_latency((datetime.now(UTC) - t13).total_seconds() * 1000)

        # Stage 19: Compliance validation (Phase 3.5)
        t19 = datetime.now(UTC)
        compliance_result = self.compliance.validate(
            session_id=session_id,
            domain=request.domain,
            has_compensation=True,
            has_audit=True,
            has_retry_policy=True,
            has_manifest=True,
            task_count=len(task_ids),
            correlation_id=cid,
        )
        if not compliance_result.is_compliant:
            warnings.extend(compliance_result.violations)
        self.metrics_collector.record_audit()
        self.trace.record_compliance_stage(
            session_id=session_id, correlation_id=cid,
            compliance_status=compliance_result.status,
        )
        self._health.record_latency((datetime.now(UTC) - t19).total_seconds() * 1000)

        # Stage 14: Assess quality
        t14 = datetime.now(UTC)
        quality_assessment = self.quality.assess(
            session_id=session_id,
            task_count=len(task_ids),
            tasks_completed=completed_count,
            tasks_failed=failed_count,
            tasks_skipped=skipped_count,
            has_retries=retry_count > 0,
            has_compensation=True,
            has_audit=True,
            has_telemetry=True,
            correlation_id=cid,
        )
        self.trace.record_stage(
            "assess_quality", session_id=session_id, correlation_id=cid,
            details=f"Quality: {quality_assessment.overall_quality}",
        )
        self._health.record_latency((datetime.now(UTC) - t14).total_seconds() * 1000)

        # Calculate confidence
        confidence = self.confidence_calculator.calculate(
            resource_confidence=0.8 if resources_available else 0.3,
            schedule_confidence=0.8 if schedule_feasible else 0.3,
            risk_confidence=0.8 if risk_accepted else 0.4,
            quality_confidence=quality_assessment.overall_quality,
            readiness_confidence=readiness_assessment.score,
            retry_confidence=0.8 if retry_count == 0 else 0.5,
            compensation_confidence=0.9 if True else 0.3,
        )

        # Create version
        self.version_manager.create_version(request_id, correlation_id=cid)

        # Stage 15: Create snapshot
        t15 = datetime.now(UTC)
        self.snapshot.create_snapshot(
            session_id=session_id,
            request_id=request_id,
            task_count=len(task_ids),
            tasks_completed=completed_count,
            tasks_failed=failed_count,
            readiness_score=readiness_assessment.score,
            quality_score=quality_assessment.overall_quality,
            confidence_score=confidence.overall_confidence,
            correlation_id=cid,
        )
        self.trace.record_stage("create_snapshot", session_id=session_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t15).total_seconds() * 1000)

        # Stage 16: Record lineage
        t16 = datetime.now(UTC)
        self.lineage.record(
            request_id=request_id,
            session_id=session_id,
            stage="execution_complete",
            summary=f"Tasks {completed_count}/{len(task_ids)} completed, readiness={readiness_assessment.status}",
            correlation_id=cid,
        )
        self.trace.record_stage("record_lineage", session_id=session_id, correlation_id=cid)
        self._health.record_latency((datetime.now(UTC) - t16).total_seconds() * 1000)

        # Explainability metadata
        explainability = ExecutionExplainabilityMetadata(
            why_session_created=(
                f"Session created for execution in domain {request.domain}"
            ),
            why_task_ordered=(
                f"Tasks ordered with {len(execution_graph.nodes)} nodes"
            ),
            why_retry_used=(
                f"Retry used: {retry_count} retries performed"
            ),
            why_compensation_triggered=(
                f"Compensation triggered: {compensation_done}"
            ),
            why_readiness_assessed=(
                f"Readiness: {readiness_assessment.status} "
                f"({readiness_assessment.score:.2f})"
            ),
            why_cancelled="",
        )

        # Stage 23: Export generation (Phase 3.5)
        t23 = datetime.now(UTC)
        total_time_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
        self.export_profiles.generate_rest(
            session_id=session_id,
            status=final_state,
            success=failed_count == 0,
            task_count=len(task_ids),
            completed=completed_count,
            failed=failed_count,
            duration_ms=int(total_time_ms),
            correlation_id=cid,
        )
        self.snapshot.create_export_snapshot(
            session_id=session_id,
            request_id=request_id,
            export_type="rest",
            task_count=len(task_ids),
            tasks_completed=completed_count,
            tasks_failed=failed_count,
            duration_ms=int(total_time_ms),
            quality_score=quality_assessment.overall_quality,
            confidence_score=confidence.overall_confidence,
            correlation_id=cid,
        )
        self.pipeline_version.create_version(correlation_id=cid)
        self.metrics_collector.record_pipeline_version()
        self.trace.record_export_stage(
            session_id=session_id, correlation_id=cid,
            export_type="rest",
        )
        self._health.record_latency((datetime.now(UTC) - t23).total_seconds() * 1000)

        # Record metrics
        self.metrics_collector.record_session()
        self._health.record_session()
        self._health.record_latency(total_time_ms)

        # Stage 17: Build decision
        overall_success = failed_count == 0
        compliance_status = compliance_result.status if compliance_result.is_compliant else "non_compliant"
        diagnostics_snapshot = self.diagnostics.get_summary(session_id)
        decision = ExecutionDecision(
            request_id=request.request_id,
            session_id=uuid.UUID(session_id),
            overall_success=overall_success,
            state=ExecutionState(final_state),
            tasks_total=len(task_ids),
            tasks_completed=completed_count,
            tasks_failed=failed_count,
            tasks_skipped=skipped_count,
            retries_performed=retry_count,
            compensations_performed=1 if compensation_done else 0,
            quality_score=round(quality_assessment.overall_quality, 4),
            compliance_status=compliance_status,
            compliance_report={
                "violations": compliance_result.violations,
                "checks_passed": compliance_result.checks_passed,
                "checks_failed": compliance_result.checks_failed,
                "total_checks": compliance_result.total_checks,
            },
            diagnostics={
                "total_events": diagnostics_snapshot.total_events,
                "task_failures": diagnostics_snapshot.task_failures,
                "policy_violations": diagnostics_snapshot.policy_violations,
            },
            issues=issues,
            warnings=warnings,
            confidence=confidence,
            explainability=explainability,
            correlation_id=cid,
        )
        self._decisions[str(decision.decision_id)] = decision

        # Build result
        result = ExecutionResult(
            request_id=request.request_id,
            session_id=uuid.UUID(session_id),
            overall_success=overall_success,
            started_at=start_time,
            completed_at=datetime.now(UTC),
            total_duration_ms=int(total_time_ms),
            metadata={
                "decision_id": str(decision.decision_id),
            },
        )

        log.info(
            "coordinator.execute.complete",
            request_id=request_id,
            session_id=session_id,
            success=overall_success,
            tasks=f"{completed_count}/{len(task_ids)}",
            latency_ms=round(total_time_ms, 2),
        )
        return result

    def get_session(self, session_id: str) -> ExecutionSession | None:
        return self.session_manager.get_session(session_id)

    def get_result(self, result_id: str) -> ExecutionResult | None:
        for decision in self._decisions.values():
            if str(decision.decision_id) == result_id or str(decision.session_id) == result_id:
                return ExecutionResult(
                    request_id=decision.request_id,
                    session_id=decision.session_id,
                    overall_success=decision.overall_success,
                    completed_at=decision.timestamp,
                    total_duration_ms=0,
                )
        return None

    def get_package(self, package_id: str) -> ExecutionPackage | None:
        return None

    def cancel(
        self,
        session_id: str,
        reason: str = "",
    ) -> bool:
        if self.session_manager.update_status(session_id, "CANCELLED"):
            self.session_manager.update_session(
                session_id,
                error_message=reason or "Cancelled by user",
            )
            log.info("coordinator.cancelled", session_id=session_id, reason=reason)
            return True
        return False

    def health(self) -> ExecutionHealth:
        return self._health.get_health()

    def metrics(self) -> ExecutionMetrics:
        m_snapshot = self.metrics_collector.snapshot()
        confidences = self.confidence_calculator.get_history()
        avg_conf = (
            sum(c.overall_confidence for c in confidences) / len(confidences)
            if confidences else 0.0
        )
        qualities = self.quality.get_all_assessments()
        avg_qual = (
            sum(a.overall_quality for a in qualities) / len(qualities)
            if qualities else 0.0
        )

        total_sessions = self.session_manager.count()
        sessions_by_state = self.session_manager.count_by_state()

        return ExecutionMetrics(
            sessions_total=total_sessions,
            sessions_completed=sessions_by_state.get("COMPLETED", 0),
            sessions_failed=sessions_by_state.get("FAILED", 0),
            tasks_total=m_snapshot.tasks_total,
            tasks_completed=m_snapshot.tasks_completed,
            tasks_failed=m_snapshot.tasks_failed,
            tasks_skipped=0,
            retries_total=m_snapshot.retries_total,
            compensations_total=m_snapshot.compensations_total,
            rollbacks_total=m_snapshot.rollbacks_total,
            diagnostics_total=m_snapshot.diagnostics_total,
            sla_violations=m_snapshot.sla_violations,
            completion_rate=round(
                (sessions_by_state.get("COMPLETED", 0) / total_sessions)
                if total_sessions > 0 else 0.0, 4,
            ),
            average_task_duration_ms=m_snapshot.average_task_duration_ms,
            average_session_duration_ms=0.0,
            average_recovery_time_ms=round(
                self.metrics_collector.get_average_recovery_time_ms(), 2,
            ),
            success_rate=(
                (sessions_by_state.get("COMPLETED", 0) / total_sessions)
                if total_sessions > 0 else 0.0
            ),
        )

    def get_decision(self, decision_id: str) -> ExecutionDecision | None:
        return self._decisions.get(decision_id)
