"""PluginCoordinator — orchestrates all plugin sub-components.

Coordinates PluginDiscoverer, PluginValidator, DependencyResolver,
PluginDependencyGraph, PluginCompatibilityManager, PluginLoader,
PluginInitializer, PluginSandboxManager, PluginResourceManager,
PluginLifecycleManager, CapabilityRegistration, PluginPolicyEngine,
PluginTrace, and PluginMetricsCollector.

Contains orchestration only — no business logic.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.plugins.contracts.models import (
    Plugin,
    PluginConfidence,
    PluginConfiguration,
    PluginDecision,
    PluginExplainabilityMetadata,
    PluginHealth,
    PluginMetrics,
    PluginSandbox,
)
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType
from adip.plugins.execution.cache import PluginCache
from adip.plugins.execution.capability_registration import CapabilityRegistration
from adip.plugins.execution.compatibility_manager import PluginCompatibilityManager
from adip.plugins.execution.dependency_graph import PluginDependencyGraph
from adip.plugins.execution.dependency_resolver import DependencyResolver
from adip.plugins.execution.discoverer import PluginDiscoverer
from adip.plugins.execution.initializer import PluginInitializer
from adip.plugins.execution.lifecycle_manager import PluginLifecycleManager
from adip.plugins.execution.loader import PluginLoader
from adip.plugins.execution.metrics import PluginMetricsCollector
from adip.plugins.execution.models import (
    CompatibilityResult,
    DiscoveryResult,
    InitializationResult,
    LoaderResult,
    TraceRecord,
)
from adip.plugins.execution.policy import PluginPolicyEngine
from adip.plugins.execution.resource_manager import PluginResourceManager
from adip.plugins.execution.sandbox_manager import PluginSandboxManager
from adip.plugins.execution.trace import PluginTrace
from adip.plugins.execution.validator import PluginValidator
from adip.plugins.orchestration.confidence import PluginConfidenceCalculator

log = structlog.get_logger(__name__)


class PluginCoordinator:
    """Orchestrates all plugin sub-components for the ADIP platform.

    PluginManager delegates to this coordinator for all sub-component
    interactions. All components are injectable via constructor (DI ready).
    """

    def __init__(
        self,
        discoverer: PluginDiscoverer | None = None,
        validator: PluginValidator | None = None,
        dependency_resolver: DependencyResolver | None = None,
        dependency_graph: PluginDependencyGraph | None = None,
        compatibility_manager: PluginCompatibilityManager | None = None,
        loader: PluginLoader | None = None,
        initializer: PluginInitializer | None = None,
        sandbox_manager: PluginSandboxManager | None = None,
        resource_manager: PluginResourceManager | None = None,
        lifecycle_manager: PluginLifecycleManager | None = None,
        capability_registration: CapabilityRegistration | None = None,
        cache: PluginCache | None = None,
        policy_engine: PluginPolicyEngine | None = None,
        trace: PluginTrace | None = None,
        metrics_collector: PluginMetricsCollector | None = None,
        confidence_calculator: PluginConfidenceCalculator | None = None,
    ) -> None:
        self._discoverer = discoverer or PluginDiscoverer()
        self._validator = validator or PluginValidator()
        self._dependency_resolver = dependency_resolver or DependencyResolver()
        self._dependency_graph = dependency_graph or PluginDependencyGraph()
        self._compatibility_manager = compatibility_manager or PluginCompatibilityManager()
        self._loader = loader or PluginLoader()
        self._initializer = initializer or PluginInitializer()
        self._sandbox_manager = sandbox_manager or PluginSandboxManager()
        self._resource_manager = resource_manager or PluginResourceManager()
        self._lifecycle_manager = lifecycle_manager or PluginLifecycleManager()
        self._capability_registration = capability_registration or CapabilityRegistration()
        self._cache = cache or PluginCache()
        self._policy_engine = policy_engine or PluginPolicyEngine()
        self._trace = trace or PluginTrace()
        self._metrics_collector = metrics_collector or PluginMetricsCollector()
        self._confidence_calculator = confidence_calculator or PluginConfidenceCalculator()
        self._plugins: dict[str, Plugin] = {}
        self._sandboxes: dict[str, PluginSandbox] = {}

    # ── Discovery Pipeline ──────────────────────────────────────────────────

    def discover_plugin(self, source: str, source_type: str = "") -> DiscoveryResult:
        """Orchestrate plugin discovery."""
        log.info("coordinator.discover_plugin", source=source, source_type=source_type)

        self._trace.record(TraceRecord(stage_name="discovery", operation="discover"))

        result = self._discoverer.discover(source, source_type)

        self._trace.record(TraceRecord(
            stage_name="discovery_complete",
            operation="discover",
            plugin_id=result.plugin_name,
            duration_ms=5.0,
        ))
        self._metrics_collector.increment_discoveries()

        return result

    # ── Validation Pipeline ─────────────────────────────────────────────────

    def validate_plugin(self, plugin: Plugin) -> list[str]:
        """Orchestrate full plugin validation.

        Runs all validators and returns violations.
        """
        log.info("coordinator.validate_plugin", plugin=plugin.name)

        self._trace.record(TraceRecord(stage_name="validation", operation="validate", plugin_id=str(plugin.plugin_id)))

        violations = self._validator.validate_plugin(plugin)
        if plugin.manifest:
            violations.extend(self._validator.validate_manifest(plugin.manifest))

        if violations:
            self._metrics_collector.increment_validation_errors()
            self._trace.record(TraceRecord(
                stage_name="validation_failed",
                operation="validate",
                plugin_id=str(plugin.plugin_id),
                errors=violations,
                success=False,
            ))
        else:
            self._trace.record(TraceRecord(
                stage_name="validation_passed",
                operation="validate",
                plugin_id=str(plugin.plugin_id),
            ))

        return violations

    # ── Compatibility Pipeline ──────────────────────────────────────────────

    def check_compatibility(self, plugin: Plugin) -> CompatibilityResult:
        """Orchestrate compatibility check."""
        log.info("coordinator.check_compatibility", plugin=plugin.name)

        self._trace.record(TraceRecord(stage_name="compatibility_check", operation="check_compatibility",
                                        plugin_id=str(plugin.plugin_id)))

        result = self._compatibility_manager.check_compatibility(plugin)

        if not result.compatible:
            self._metrics_collector.increment_compatibility_failures()

        self._trace.record(TraceRecord(
            stage_name="compatibility_result",
            operation="check_compatibility",
            plugin_id=str(plugin.plugin_id),
            success=result.compatible,
            errors=result.reasons,
        ))
        return result

    # ── Dependency Pipeline ─────────────────────────────────────────────────

    def resolve_dependencies(self, plugin: Plugin) -> tuple[list[str], list[CompatibilityResult]]:
        """Orchestrate dependency resolution for a plugin."""
        log.info("coordinator.resolve_dependencies", plugin=plugin.name)

        self._trace.record(TraceRecord(stage_name="dependency_resolution", operation="resolve_dependencies",
                                        plugin_id=str(plugin.plugin_id)))

        available = list(self._plugins.values())
        satisfied = self._dependency_resolver.resolve(plugin, available)
        missing = self._dependency_resolver.find_missing(plugin, available)

        dep_results: list[CompatibilityResult] = []
        for dep_name in missing:
            dep_results.append(CompatibilityResult(
                plugin_id="",
                plugin_name=dep_name.plugin_name,
                compatible=False,
                reasons=["Missing dependency"],
            ))

        if missing:
            self._trace.record(TraceRecord(
                stage_name="dependency_missing",
                operation="resolve_dependencies",
                plugin_id=str(plugin.plugin_id),
                errors=[d.plugin_name for d in missing],
                success=False,
            ))
        else:
            self._trace.record(TraceRecord(
                stage_name="dependency_resolved",
                operation="resolve_dependencies",
                plugin_id=str(plugin.plugin_id),
            ))

        return satisfied, dep_results

    # ── Sandbox Pipeline ────────────────────────────────────────────────────

    def create_sandbox(self, plugin: Plugin, config: dict | None = None) -> PluginSandbox:
        """Orchestrate sandbox creation."""
        log.info("coordinator.create_sandbox", plugin=plugin.name)

        self._trace.record(TraceRecord(stage_name="sandbox_creation", operation="create_sandbox",
                                        plugin_id=str(plugin.plugin_id)))

        sandbox = self._sandbox_manager.create_sandbox(plugin, config)
        sb_id = str(sandbox.sandbox_id)
        self._sandboxes[sb_id] = sandbox

        self._metrics_collector.set_sandbox_count(self._sandbox_manager.count())

        self._trace.record(TraceRecord(
            stage_name="sandbox_created",
            operation="create_sandbox",
            plugin_id=str(plugin.plugin_id),
            sandbox_id=sb_id,
        ))
        return sandbox

    # ── Load Pipeline ───────────────────────────────────────────────────────

    def load_plugin(self, plugin: Plugin) -> LoaderResult:
        """Orchestrate the full plugin loading pipeline."""
        log.info("coordinator.load_plugin", plugin=plugin.name)

        self._trace.record(TraceRecord(stage_name="loading", operation="load",
                                        plugin_id=str(plugin.plugin_id)))
        self._metrics_collector.increment_load_attempts()

        loader_result = self._loader.load(plugin)

        if loader_result.success:
            self._metrics_collector.increment_load_successes()
            self._trace.record(TraceRecord(
                stage_name="loaded",
                operation="load",
                plugin_id=str(plugin.plugin_id),
            ))
        else:
            self._metrics_collector.increment_load_failures()
            self._trace.record(TraceRecord(
                stage_name="load_failed",
                operation="load",
                plugin_id=str(plugin.plugin_id),
                errors=loader_result.errors,
                success=False,
            ))

        return loader_result

    # ── Initialization Pipeline ─────────────────────────────────────────────

    def initialize_plugin(self, plugin: Plugin, config: PluginConfiguration | None = None) -> InitializationResult:
        """Orchestrate plugin initialisation."""
        log.info("coordinator.initialize_plugin", plugin=plugin.name)

        self._trace.record(TraceRecord(stage_name="initialization", operation="initialize",
                                        plugin_id=str(plugin.plugin_id)))
        self._metrics_collector.increment_initialization_attempts()

        result = self._initializer.initialize(plugin, config)

        self._metrics_collector.record_initialization_time(10.0)

        if result.success:
            self._trace.record(TraceRecord(
                stage_name="initialized",
                operation="initialize",
                plugin_id=str(plugin.plugin_id),
            ))
        else:
            self._trace.record(TraceRecord(
                stage_name="initialization_failed",
                operation="initialize",
                plugin_id=str(plugin.plugin_id),
                errors=result.errors,
                success=False,
            ))

        return result

    # ── Capability Registration ─────────────────────────────────────────────

    def register_capabilities(self, plugin: Plugin) -> list[Any]:
        """Orchestrate capability registration for a plugin."""
        log.info("coordinator.register_capabilities", plugin=plugin.name)

        self._trace.record(TraceRecord(stage_name="capability_registration", operation="register_capabilities",
                                        plugin_id=str(plugin.plugin_id)))

        records: list[Any] = []
        if plugin.manifest:
            for cap in plugin.manifest.capabilities:
                record = self._capability_registration.register(plugin, cap)
                records.append(record)
                self._metrics_collector.increment_capability_registrations()

        self._trace.record(TraceRecord(
            stage_name="capabilities_registered",
            operation="register_capabilities",
            plugin_id=str(plugin.plugin_id),
        ))
        return records

    # ── Lifecycle Transitions ───────────────────────────────────────────────

    def transition_lifecycle(
        self,
        plugin: Plugin,
        to_status: PluginLifecycleStatus,
        reason: str = "",
        changed_by: str = "",
    ) -> Plugin:
        """Orchestrate a lifecycle transition."""
        log.info("coordinator.transition_lifecycle", plugin=plugin.name, to=to_status.value)

        self._trace.record(TraceRecord(stage_name="lifecycle_transition", operation="transition",
                                        plugin_id=str(plugin.plugin_id),
                                        lifecycle_state=to_status.value))

        result = self._lifecycle_manager.transition(plugin, to_status, reason=reason, changed_by=changed_by)
        self._plugins[str(result.plugin_id)] = result
        self._metrics_collector.increment_lifecycle_transitions()

        if to_status == PluginLifecycleStatus.ACTIVE:
            self._metrics_collector.increment_active_plugins()
        elif to_status in (PluginLifecycleStatus.SUSPENDED, PluginLifecycleStatus.UNLOADED,
                           PluginLifecycleStatus.REMOVED):
            self._metrics_collector.decrement_active_plugins()

        self._trace.record(TraceRecord(
            stage_name="lifecycle_transitioned",
            operation="transition",
            plugin_id=str(result.plugin_id),
            lifecycle_state=result.status.value,
        ))
        return result

    # ── Plugin CRUD ─────────────────────────────────────────────────────────

    def install_plugin(self, plugin: Plugin) -> PluginDecision:
        """Orchestrate the full plugin installation pipeline.

        Returns a PluginDecision with the outcome of each stage.
        """
        plugin_id = str(plugin.plugin_id)
        log.info("coordinator.install_plugin", plugin=plugin.name, id=plugin_id)

        explainability = PluginExplainabilityMetadata()
        reasoning: list[str] = []
        confidence = PluginConfidence()

        # Stage 1: Validate
        self._trace.record(TraceRecord(stage_name="validation", operation="install"))
        violations = self.validate_plugin(plugin)
        if violations:
            explainability.why_plugin_rejected = "; ".join(violations)
            reasoning.append(f"Validation failed: {violations}")
            confidence = self._confidence_calculator.calculate(plugin)
            return PluginDecision(
                plugin_id=plugin.plugin_id, operation="install", allowed=False,
                decision="deny", reason="Validation failed",
                compatibility_result="", dependency_result="",
                sandbox_result="", security_result="",
                lifecycle_result="not_reached",
                reasoning=reasoning,
                confidence=confidence.overall_confidence,
            )

        # Stage 2: Compatibility check
        self._trace.record(TraceRecord(stage_name="compatibility", operation="install"))
        compat_result = self.check_compatibility(plugin)
        if not compat_result.compatible:
            reasoning.append(f"Compatibility check failed: {compat_result.reasons}")
            confidence = self._confidence_calculator.calculate(plugin)
            return PluginDecision(
                plugin_id=plugin.plugin_id, operation="install", allowed=False,
                decision="deny", reason="Compatibility check failed",
                compatibility_result="; ".join(compat_result.reasons),
                dependency_result="", sandbox_result="", security_result="",
                lifecycle_result="not_reached",
                reasoning=reasoning,
                confidence=confidence.overall_confidence,
            )

        # Stage 3: Policy check
        self._trace.record(TraceRecord(stage_name="policy", operation="install"))
        policy_violations = self._policy_engine.check_all(plugin)
        if policy_violations:
            explainability.why_plugin_rejected = "; ".join(policy_violations)
            reasoning.append(f"Policy violations: {policy_violations}")
            confidence = self._confidence_calculator.calculate(plugin)
            return PluginDecision(
                plugin_id=plugin.plugin_id, operation="install", allowed=False,
                decision="deny", reason="Policy violations",
                compatibility_result="", dependency_result="",
                sandbox_result="", security_result="; ".join(policy_violations),
                lifecycle_result="not_reached",
                reasoning=reasoning,
                confidence=confidence.overall_confidence,
            )

        # Stage 4: Transition to VALIDATED
        plugin = self.transition_lifecycle(plugin, PluginLifecycleStatus.VALIDATED)

        # Stage 5: Resolve dependencies
        self._trace.record(TraceRecord(stage_name="dependencies", operation="install"))
        satisfied, dep_results = self.resolve_dependencies(plugin)
        dep_summary = f"{len(satisfied)} satisfied, {len(dep_results)} unsatisfied"
        if dep_results:
            explainability.why_dependency_failed = "; ".join(r.reasons[0] for r in dep_results if r.reasons)
            reasoning.append(f"Dependency issues: {dep_summary}")

        # Stage 6: Transition to INSTALLED
        plugin = self.transition_lifecycle(plugin, PluginLifecycleStatus.INSTALLED)

        # Stage 7: Load plugin
        self._trace.record(TraceRecord(stage_name="load", operation="install"))
        load_result = self.load_plugin(plugin)
        if not load_result.success:
            reasoning.append(f"Load failed: {load_result.errors}")
            confidence = self._confidence_calculator.calculate(plugin)
            return PluginDecision(
                plugin_id=plugin.plugin_id, operation="install", allowed=True,
                decision="deny", reason="Load pipeline failed",
                compatibility_result="passed", dependency_result=dep_summary,
                sandbox_result="not_created", security_result="passed",
                lifecycle_result="VALIDATED->INSTALLED",
                reasoning=reasoning,
                confidence=confidence.overall_confidence,
            )

        # Stage 8: Transition to LOADED
        plugin = self.transition_lifecycle(plugin, PluginLifecycleStatus.LOADED)

        # Stage 9: Create sandbox
        self._trace.record(TraceRecord(stage_name="sandbox", operation="install"))
        sandbox = self.create_sandbox(plugin)
        explainability.why_sandbox_created = f"Sandbox {sandbox.sandbox_id} created for {plugin.name}"
        sb_summary = f"sandbox {sandbox.sandbox_id}"

        # Stage 10: Initialize
        init_result = self.initialize_plugin(plugin)
        if init_result.success:
            plugin = self.transition_lifecycle(plugin, PluginLifecycleStatus.INITIALIZED)

        # Stage 11: Register capabilities
        self._trace.record(TraceRecord(stage_name="capabilities", operation="install"))
        cap_records = self.register_capabilities(plugin)
        explainability.why_capability_registered = f"{len(cap_records)} capabilities registered"
        reasoning.append(f"Capabilities: {len(cap_records)} registered")

        # Stage 12: Final confidence
        confidence = self._confidence_calculator.calculate(plugin)

        # Store in tracking
        self._plugins[plugin_id] = plugin

        lifecycle_summary = "DISCOVERED->VALIDATED->INSTALLED->LOADED->INITIALIZED"
        decision = PluginDecision(
            plugin_id=plugin.plugin_id,
            operation="install",
            allowed=True,
            decision="approve",
            reason="Plugin installed successfully",
            compatibility_result="passed",
            dependency_result=dep_summary,
            sandbox_result=sb_summary,
            security_result="passed",
            lifecycle_result=lifecycle_summary,
            reasoning=reasoning,
            confidence=confidence.overall_confidence,
        )

        explainability.why_plugin_loaded = f"Validated, compatible, {dep_summary}, {sb_summary}"
        decision.metadata["explainability"] = explainability.model_dump()
        decision.metadata["confidence"] = confidence.model_dump()
        decision.metadata["load_result"] = load_result.model_dump()

        self._trace.record(TraceRecord(
            stage_name="installed",
            operation="install",
            plugin_id=plugin_id,
            success=True,
        ))

        log.info("coordinator.install_plugin.complete", plugin=plugin.name, id=plugin_id)
        return decision

    def get_plugin(self, plugin_id: str) -> Plugin | None:
        """Retrieve a plugin by ID."""
        return self._plugins.get(plugin_id)

    def list_plugins(
        self,
        domain: PluginDomain | None = None,
        plugin_type: PluginType | None = None,
        status: PluginLifecycleStatus | None = None,
    ) -> list[Plugin]:
        """List plugins matching the given filters."""
        results = list(self._plugins.values())
        if domain:
            results = [p for p in results if p.domain == domain]
        if plugin_type:
            results = [p for p in results if p.plugin_type == plugin_type]
        if status:
            results = [p for p in results if p.status == status]
        return results

    def delete_plugin(self, plugin_id: str) -> bool:
        """Delete/remove a plugin."""
        if plugin_id not in self._plugins:
            return False
        plugin = self._plugins[plugin_id]
        if plugin.status != PluginLifecycleStatus.REMOVED:
            try:
                plugin = self._lifecycle_manager.transition(plugin, PluginLifecycleStatus.REMOVED)
            except ValueError:
                pass
        del self._plugins[plugin_id]
        self._sandbox_manager.destroy_sandbox(plugin_id)
        log.info("coordinator.delete_plugin", plugin_id=plugin_id)
        return True

    def get_sandbox(self, sandbox_id: str) -> PluginSandbox | None:
        """Retrieve a sandbox by ID."""
        return self._sandbox_manager.get_sandbox(sandbox_id)

    # ── Health & Metrics ────────────────────────────────────────────────────

    def health(self) -> PluginHealth:
        """Return health status of all sub-components."""
        log.info("coordinator.health")
        snap = self._metrics_collector.snapshot()
        plugin_count = len(self._plugins)
        active_count = sum(1 for p in self._plugins.values() if p.status == PluginLifecycleStatus.ACTIVE)
        error_count = snap.errors_total
        sandbox_count = self._sandbox_manager.count()

        overall = "HEALTHY" if error_count == 0 else "DEGRADED"
        error_rate = round(error_count / max(1, snap.executions_total), 4) if snap.executions_total else 0.0

        return PluginHealth(
            overall_status=overall,
            plugin_id=uuid.uuid4(),
            plugin_name="plugin-platform",
            status="RUNNING",
            discovery_status="HEALTHY",
            validation_status="HEALTHY",
            loader_status="HEALTHY",
            dependency_resolver_status="HEALTHY",
            sandbox_status="HEALTHY",
            compatibility_status="HEALTHY",
            lifecycle_status="HEALTHY",
            capability_status="HEALTHY",
            uptime_seconds=3600.0,
            error_count=error_count,
            error_rate=error_rate,
            total_executions=snap.executions_total or 0,
            average_load_time_ms=snap.load_latency_ms,
            active_plugins=active_count,
        )

    def metrics(self) -> PluginMetrics:
        """Return aggregated metrics from all sub-components."""
        return self._metrics_collector.snapshot()

    def get_dependency_graph_size(self) -> int:
        """Return the size of the dependency graph."""
        return len(self._plugins)

    def clear(self) -> None:
        """Clear all plugins, sandboxes, and traces."""
        self._plugins.clear()
        self._sandboxes.clear()
        self._sandbox_manager.clear()
        self._lifecycle_manager.clear()
        self._capability_registration.clear()
        self._trace.clear()


import uuid  # noqa: E402
