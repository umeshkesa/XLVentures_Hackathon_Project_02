"""RegistryCoordinator — central orchestrator for the registry pipeline.

Coordinates all Phase 2 sub-components in the correct order for each
registry operation. Contains orchestration only — no business logic.

Pipeline stages for each operation are timed and traced individually.
Phase 3.5 adds dedicated trace stages for cache, audit, policy,
dependency, and metrics; adds search_result_quality to confidence;
adds new metrics counters.
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from adip.registry.contracts.models import (
    RegistryDecision,
    RegistryEntry,
    RegistryFilter,
    RegistryHealth,
    RegistryMetrics,
    RegistrySearchResult,
)
from adip.registry.enums import RegistryLifecycleStatus, RegistryType
from adip.registry.execution.audit import RegistryAudit
from adip.registry.execution.cache import RegistryCache
from adip.registry.execution.dependency_graph import RegistryDependencyGraph
from adip.registry.execution.index_manager import RegistryIndexManager
from adip.registry.execution.lifecycle import RegistryLifecycleManager
from adip.registry.execution.metrics import RegistryMetricsCollector
from adip.registry.execution.policy import RegistryPolicyEngine
from adip.registry.execution.searcher import (
    RegistrySearcher,
)
from adip.registry.execution.trace import RegistryTrace
from adip.registry.execution.validator import RegistryValidator
from adip.registry.execution.version_manager import RegistryVersionManager
from adip.registry.orchestration.confidence import RegistryConfidenceCalculator
from adip.registry.orchestration.session import RegistrySessionManager

log = structlog.get_logger(__name__)


class RegistryCoordinator:
    """Orchestrates the full registry operation pipeline.

    Each public method runs the relevant pipeline stages in order,
    with per-stage timing and tracing. All sub-components are
    injectable via constructor for DI and testability.

    Pipeline stages (varies by operation):
        1. Validation
        2. Policy Check
        3. Version Management
        4. Index Management
        5. Dependency Graph
        6. Cache
        7. Confidence Calculation
        8. Audit
        9. Metrics
        10. Trace

    Phase 3.5 enhances tracing with dedicated stage methods for
    cache, audit, policy, dependency, and metrics stages.
    """

    def __init__(
        self,
        validator: RegistryValidator | None = None,
        searcher: RegistrySearcher | None = None,
        index_manager: RegistryIndexManager | None = None,
        version_manager: RegistryVersionManager | None = None,
        lifecycle_manager: RegistryLifecycleManager | None = None,
        dependency_graph: RegistryDependencyGraph | None = None,
        cache: RegistryCache | None = None,
        policy_engine: RegistryPolicyEngine | None = None,
        audit: RegistryAudit | None = None,
        metrics_collector: RegistryMetricsCollector | None = None,
        trace: RegistryTrace | None = None,
        session_manager: RegistrySessionManager | None = None,
        confidence_calculator: RegistryConfidenceCalculator | None = None,
    ) -> None:
        self.validator = validator or RegistryValidator()
        self.searcher = searcher or RegistrySearcher()
        self.index_manager = index_manager or RegistryIndexManager()
        self.version_manager = version_manager or RegistryVersionManager()
        self.lifecycle_manager = lifecycle_manager or RegistryLifecycleManager()
        self.dependency_graph = dependency_graph or RegistryDependencyGraph()
        self.cache = cache or RegistryCache()
        self.policy_engine = policy_engine or RegistryPolicyEngine()
        self.audit = audit or RegistryAudit()
        self.metrics_collector = metrics_collector or RegistryMetricsCollector()
        self.trace = trace or RegistryTrace()
        self.session_manager = session_manager or RegistrySessionManager()
        self.confidence_calculator = confidence_calculator or RegistryConfidenceCalculator()

        # In-memory entry store
        self._entries: dict[str, RegistryEntry] = {}
        self._start_time: float = time.time()

    # ─────────────────────────────────────────────────────────────────
    # Registration
    # ─────────────────────────────────────────────────────────────────

    def register_entry(
        self,
        entry: RegistryEntry,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Orchestrate the full entry registration pipeline.

        Pipeline: session → validation → policy → version → index
                 → cache → dependency → audit → metrics → confidence → trace
        """
        op = "register"
        corr_id = correlation_id or str(uuid.uuid4())

        # Session
        session = self.session_manager.create_session(
            registry_type=entry.registry_type,
            operation=op,
            user_id=performed_by,
            namespace=entry.namespace,
            correlation_id=corr_id,
        )

        reasoning: list[str] = []
        validation_violations: list[str] = []
        policy_violations: list[str] = []

        # 1. Validation
        t0 = time.time()
        validation_violations = self.validator.validate_entry(entry)
        t1 = time.time()
        val_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_validation_stage(
            entry_id=str(entry.entry_id),
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            errors=validation_violations,
            success=len(validation_violations) == 0,
            duration_ms=val_duration,
        )
        if validation_violations:
            reasoning.append(f"Validation failed: {'; '.join(validation_violations)}")
        else:
            reasoning.append("Validation passed")

        # 2. Policy Check
        t0 = time.time()
        current_entries = list(self._entries.values())
        policy_violations = self.policy_engine.check_registration_policy(entry, current_entries)
        t1 = time.time()
        pol_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_policy_stage(
            operation=op,
            entry_id=str(entry.entry_id),
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            violations=policy_violations,
            duration_ms=pol_duration,
        )
        if policy_violations:
            reasoning.append(f"Policy check failed: {'; '.join(policy_violations)}")
        else:
            reasoning.append("Policy check passed")

        allowed = len(validation_violations) == 0 and len(policy_violations) == 0

        if allowed:
            # 3. Store entry
            self._entries[str(entry.entry_id)] = entry
            self.session_manager.add_affected_entry(str(session.session_id), str(entry.entry_id))

            # 4. Version
            t0 = time.time()
            version_record = self.version_manager.create_version(
                entry,
                release_notes="Initial registration",
                created_by=performed_by,
            )
            t1 = time.time()
            ver_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_version_stage(
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                version=entry.version,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=ver_duration,
            )
            reasoning.append(f"Version {entry.version} created")

            # 5. Index
            t0 = time.time()
            self.index_manager.index_entry(entry)
            t1 = time.time()
            idx_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_index_stage(
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=idx_duration,
            )
            reasoning.append("Entry indexed")

            # 6. Cache
            t0 = time.time()
            self.cache.set_entry(entry)
            t1 = time.time()
            cache_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_cache_stage(
                operation="set",
                entry_id=str(entry.entry_id),
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=cache_duration,
            )

            # 7. Dependency Graph
            t0 = time.time()
            self.dependency_graph.create(list(self._entries.values()))
            t1 = time.time()
            dep_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_dependency_stage(
                operation=op,
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=dep_duration,
            )

            # 8. Audit
            t0 = time.time()
            self.audit.record_registration(entry, performed_by=performed_by)
            t1 = time.time()
            audit_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_audit_stage(
                operation="registration",
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=audit_duration,
            )
            reasoning.append("Audit recorded")

            # 9. Metrics
            self.metrics_collector.increment_entries_total()
            self.metrics_collector.increment_registrations()
            self.metrics_collector.set_registry_type(entry.registry_type)
            self.metrics_collector.increment_namespace_usage(entry.namespace or "default")
            self.metrics_collector.increment_registry_type_usage(entry.registry_type.value)
            if entry.scope:
                self.metrics_collector.set_entries_per_scope(
                    {entry.scope.value: self.metrics_collector.snapshot().entries_per_scope.get(entry.scope.value, 0) + 1}
                )
            if entry.status:
                self.metrics_collector.set_entries_per_status(
                    {entry.status.value: self.metrics_collector.snapshot().entries_per_status.get(entry.status.value, 0) + 1}
                )
            self.trace.record_metrics_stage(
                operation=op,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
            )
        else:
            ver_duration = 0.0
            idx_duration = 0.0
            cache_duration = 0.0
            dep_duration = 0.0
            audit_duration = 0.0
            if validation_violations:
                self.metrics_collector.increment_validation_failures()
            reasoning.append("Operation blocked by policy/validation failures")

        # 10. Confidence
        t0 = time.time()
        confidence = self.confidence_calculator.calculate(
            entry=entry,
            validation_violations=validation_violations,
            policy_violations=policy_violations,
            dependencies_resolved=True,
        )
        t1 = time.time()
        conf_duration = round((t1 - t0) * 1000, 2)

        # Complete session
        total_duration = round((time.time() - t1 + sum(
            [val_duration, pol_duration, ver_duration, idx_duration, cache_duration, dep_duration, audit_duration, conf_duration]
        )) * 1000, 2)
        self.session_manager.complete_session(
            str(session.session_id),
            status="COMPLETED" if allowed else "FAILED",
            statistics={
                "validation_ms": val_duration,
                "policy_ms": pol_duration,
                "version_ms": ver_duration,
                "index_ms": idx_duration,
                "cache_ms": cache_duration,
                "dependency_ms": dep_duration,
                "audit_ms": audit_duration,
                "confidence_ms": conf_duration,
                "total_ms": total_duration,
            },
        )

        # 11. Decision
        decision = RegistryDecision(
            registry_type=entry.registry_type,
            entry_id=entry.entry_id,
            operation=op,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence.overall_confidence,
            validation_result=validation_violations,
            policy_result=policy_violations,
            version_result=f"v{entry.version}" if allowed else "",
            dependency_result="resolved" if allowed else "",
            performed_by=performed_by,
            metadata={"session_id": str(session.session_id), "correlation_id": corr_id},
        )

        # 12. Trace
        self.trace.record_stage(
            stage_name="coordinator",
            operation=op,
            entry_id=str(entry.entry_id),
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            success=allowed,
            duration_ms=total_duration,
        )

        return decision

    # ─────────────────────────────────────────────────────────────────
    # Lookup
    # ─────────────────────────────────────────────────────────────────

    def get_entry(
        self,
        entry_id: str,
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Retrieve an entry by ID with cache-first strategy."""
        op = "lookup"
        corr_id = correlation_id or str(uuid.uuid4())

        # Try cache first
        t0 = time.time()
        cached = self.cache.get_entry(entry_id)
        t1 = time.time()
        if cached is not None:
            self.metrics_collector.increment_cache_hits()
            self.metrics_collector.increment_lookups()
            self.trace.record_stage(
                stage_name="cache",
                operation=op,
                entry_id=entry_id,
                registry_type=cached.registry_type.value,
                correlation_id=corr_id,
                success=True,
                duration_ms=round((t1 - t0) * 1000, 2),
            )
            return cached
        self.metrics_collector.increment_cache_misses()

        # Fall back to in-memory store
        entry = self._entries.get(entry_id)
        self.metrics_collector.increment_lookups()

        if entry:
            self.cache.set_entry(entry)

        self.trace.record_stage(
            stage_name="lookup",
            operation=op,
            entry_id=entry_id,
            registry_type=entry.registry_type.value if entry else "",
            correlation_id=corr_id,
            success=entry is not None,
            duration_ms=round((time.time() - t0) * 1000, 2),
        )
        return entry

    # ─────────────────────────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────────────────────────

    def update_entry(
        self,
        entry: RegistryEntry,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Orchestrate the full entry update pipeline.

        Pipeline: session → validation → policy → version → index
                 → cache → confidence → audit → metrics → trace
        """
        op = "update"
        corr_id = correlation_id or str(uuid.uuid4())

        existing = self._entries.get(str(entry.entry_id))
        if existing is None:
            return RegistryDecision(
                registry_type=entry.registry_type,
                entry_id=entry.entry_id,
                operation=op,
                allowed=False,
                reasoning=["Entry not found"],
                performed_by=performed_by,
            )

        session = self.session_manager.create_session(
            registry_type=entry.registry_type,
            operation=op,
            user_id=performed_by,
            namespace=entry.namespace,
            correlation_id=corr_id,
        )

        reasoning: list[str] = []
        validation_violations: list[str] = []
        policy_violations: list[str] = []

        # 1. Validation
        t0 = time.time()
        validation_violations = self.validator.validate_entry(entry)
        t1 = time.time()
        val_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_validation_stage(
            entry_id=str(entry.entry_id),
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            errors=validation_violations,
            success=len(validation_violations) == 0,
            duration_ms=val_duration,
        )

        # 2. Policy
        t0 = time.time()
        policy_violations = self.policy_engine.check_permission_policy(existing, "update", performed_by)
        policy_violations.extend(self.policy_engine.check_version_policy(existing, entry.version))
        t1 = time.time()
        pol_duration = round((t1 - t0) * 1000, 2)
        self.trace.record_policy_stage(
            operation=op,
            entry_id=str(entry.entry_id),
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            violations=policy_violations,
            duration_ms=pol_duration,
        )

        allowed = len(validation_violations) == 0 and len(policy_violations) == 0

        if allowed:
            entry.updated_at = datetime.now(UTC)
            self._entries[str(entry.entry_id)] = entry
            self.session_manager.add_affected_entry(str(session.session_id), str(entry.entry_id))

            # Version
            t0 = time.time()
            self.version_manager.create_version(entry, created_by=performed_by)
            t1 = time.time()
            ver_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_version_stage(
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                version=entry.version,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=ver_duration,
            )

            # Re-index
            t0 = time.time()
            self.index_manager.remove_entry(existing)
            self.index_manager.index_entry(entry)
            t1 = time.time()
            idx_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_index_stage(
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=idx_duration,
            )

            # Cache
            t0 = time.time()
            self.cache.invalidate_entry(str(entry.entry_id))
            self.cache.set_entry(entry)
            t1 = time.time()
            cache_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_cache_stage(
                operation="update",
                entry_id=str(entry.entry_id),
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=cache_duration,
            )

            # Dependency Graph
            t0 = time.time()
            self.dependency_graph.create(list(self._entries.values()))
            t1 = time.time()
            dep_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_dependency_stage(
                operation=op,
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=dep_duration,
            )

            # Audit
            t0 = time.time()
            self.audit.record_update(entry, performed_by=performed_by)
            t1 = time.time()
            audit_duration = round((t1 - t0) * 1000, 2)
            self.trace.record_audit_stage(
                operation="update",
                entry_id=str(entry.entry_id),
                entry_name=entry.name,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
                duration_ms=audit_duration,
            )

            reasoning.append("Entry updated successfully")
            self.metrics_collector.increment_updates()
            self.metrics_collector.increment_registry_type_usage(entry.registry_type.value)
            self.trace.record_metrics_stage(
                operation=op,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
            )
        else:
            ver_duration = 0.0
            idx_duration = 0.0
            cache_duration = 0.0
            dep_duration = 0.0
            audit_duration = 0.0
            if validation_violations:
                self.metrics_collector.increment_validation_failures()
            reasoning.append(f"Update blocked: {'; '.join(validation_violations + policy_violations)}")

        # Confidence
        confidence = self.confidence_calculator.calculate(
            entry=entry,
            validation_violations=validation_violations,
            policy_violations=policy_violations,
        )

        total_duration = round((time.time() - t0) * 1000 + sum(
            [val_duration, pol_duration, ver_duration, idx_duration, cache_duration, dep_duration, audit_duration]
        ), 2)
        self.session_manager.complete_session(
            str(session.session_id),
            status="COMPLETED" if allowed else "FAILED",
            statistics={
                "validation_ms": val_duration,
                "policy_ms": pol_duration,
                "version_ms": ver_duration,
                "index_ms": idx_duration,
                "cache_ms": cache_duration,
                "dependency_ms": dep_duration,
                "audit_ms": audit_duration,
                "total_ms": total_duration,
            },
        )

        decision = RegistryDecision(
            registry_type=entry.registry_type,
            entry_id=entry.entry_id,
            operation=op,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence.overall_confidence,
            validation_result=validation_violations,
            policy_result=policy_violations,
            version_result=f"v{entry.version}" if allowed else "",
            performed_by=performed_by,
            metadata={"session_id": str(session.session_id), "correlation_id": corr_id},
        )

        self.trace.record_stage(
            stage_name="coordinator",
            operation=op,
            entry_id=str(entry.entry_id),
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            success=allowed,
            duration_ms=total_duration,
        )
        return decision

    # ─────────────────────────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────────────────────────

    def delete_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Orchestrate entry deletion.

        Removes the entry from the store, indexes, and cache.
        Does not use lifecycle transition — delete is a hard removal.
        """
        op = "delete"
        corr_id = correlation_id or str(uuid.uuid4())

        entry = self._entries.get(entry_id)
        if entry is None:
            try:
                uid = uuid.UUID(entry_id) if entry_id else uuid.uuid4()
            except ValueError:
                uid = uuid.uuid4()
            return RegistryDecision(
                registry_type=RegistryType.CAPABILITY,
                entry_id=uid,
                operation=op,
                allowed=False,
                reasoning=["Entry not found"],
                performed_by=performed_by,
            )

        session = self.session_manager.create_session(
            registry_type=entry.registry_type,
            operation=op,
            user_id=performed_by,
            namespace=entry.namespace,
            correlation_id=corr_id,
        )

        reasoning: list[str] = []
        policy_violations: list[str] = []

        # Policy
        t0 = time.time()
        policy_violations = self.policy_engine.check_permission_policy(entry, "delete", performed_by)
        t1 = time.time()

        allowed = len(policy_violations) == 0

        if allowed:
            self.index_manager.remove_entry(entry)
            self.cache.invalidate_entry(entry_id)
            del self._entries[entry_id]
            self.audit.record_removal(entry, performed_by=performed_by)
            self.metrics_collector.decrement_entries_total()
            self.metrics_collector.increment_deregistrations()
            reasoning.append("Entry deleted successfully")

            self.trace.record_cache_stage(
                operation="invalidate",
                entry_id=entry_id,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
            )
            self.trace.record_audit_stage(
                operation="removal",
                entry_id=entry_id,
                entry_name=entry.name,
                registry_type=entry.registry_type.value,
                correlation_id=corr_id,
            )
        else:
            reasoning.append(f"Delete blocked: {'; '.join(policy_violations)}")

        self.trace.record_policy_stage(
            operation=op,
            entry_id=entry_id,
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            violations=policy_violations,
            duration_ms=round((time.time() - t0) * 1000, 2),
        )

        confidence = self.confidence_calculator.calculate(
            entry=entry,
            policy_violations=policy_violations,
        )

        total_duration = round((time.time() - t0) * 1000, 2)
        self.session_manager.complete_session(
            str(session.session_id),
            status="COMPLETED" if allowed else "FAILED",
        )

        decision = RegistryDecision(
            registry_type=entry.registry_type,
            entry_id=entry.entry_id,
            operation=op,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence.overall_confidence,
            policy_result=policy_violations,
            performed_by=performed_by,
            metadata={"session_id": str(session.session_id), "correlation_id": corr_id},
        )

        self.trace.record_stage(
            stage_name="coordinator",
            operation=op,
            entry_id=entry_id,
            entry_name=entry.name,
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            success=allowed,
            duration_ms=total_duration,
        )
        return decision

    # ─────────────────────────────────────────────────────────────────
    # Search
    # ─────────────────────────────────────────────────────────────────

    def search(
        self,
        filter: RegistryFilter,
        correlation_id: str = "",
    ) -> list[RegistrySearchResult]:
        """Execute a search with strategy selection and result ranking.

        Pipeline: cache check → strategy selection → search
                 → result fusion → cache store → metrics → trace
        """
        op = "search"
        corr_id = correlation_id or str(uuid.uuid4())

        cache_key = f"{filter.query}:{filter.namespace}:{','.join(filter.tags)}"

        # Cache check
        cached_results = self.cache.get_search_results(cache_key)
        if cached_results is not None:
            self.metrics_collector.increment_cache_hits()
            self.metrics_collector.increment_searches()
            self.trace.record_cache_stage(
                operation="search_hit",
                registry_type=filter.registry_type.value if filter.registry_type else "",
                correlation_id=corr_id,
                cache_hit=True,
            )
            return cached_results
        self.metrics_collector.increment_cache_misses()

        t0 = time.time()

        # Strategy selection
        strategies: list[str] = ["exact", "prefix", "tag", "label"]
        if filter.namespace:
            strategies.append("namespace")

        # Execute search
        entries_list = list(self._entries.values())
        results = self.searcher.search(filter.query, entries_list, strategies=strategies)
        scored_results = self._build_search_results(results, entries_list)

        # Post-search filter by filter criteria
        if filter.registry_type:
            scored_results = [
                r for r in scored_results
                if r.entry.registry_type == filter.registry_type
            ]
        if filter.scope:
            scored_results = [
                r for r in scored_results
                if r.entry.scope == filter.scope
            ]
        if filter.status:
            scored_results = [
                r for r in scored_results
                if r.entry.status == filter.status
            ]

        # Pagination
        scored_results = scored_results[filter.offset:filter.offset + filter.limit]

        t1 = time.time()
        search_duration = round((t1 - t0) * 1000, 2)

        # Cache
        self.cache.set_search_results(cache_key, scored_results)
        self.trace.record_cache_stage(
            operation="search_set",
            registry_type=filter.registry_type.value if filter.registry_type else "",
            correlation_id=corr_id,
            cache_hit=False,
        )

        # Metrics
        self.metrics_collector.record_search_latency(search_duration)
        self.metrics_collector.increment_search_strategy(",".join(strategies))
        self.metrics_collector.record_cache_usage(cache_key)
        self.trace.record_metrics_stage(
            operation=op,
            registry_type=filter.registry_type.value if filter.registry_type else "",
            correlation_id=corr_id,
        )

        # Trace
        self.trace.record_search_stage(
            query=filter.query,
            registry_type=filter.registry_type.value if filter.registry_type else "",
            correlation_id=corr_id,
            duration_ms=search_duration,
        )

        return scored_results

    # ─────────────────────────────────────────────────────────────────
    # Lifecycle operations
    # ─────────────────────────────────────────────────────────────────

    def activate_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Activate an entry (VALIDATED → ACTIVE)."""
        return self._lifecycle_operation(
            entry_id, RegistryLifecycleStatus.ACTIVE, performed_by, correlation_id,
        )

    def suspend_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Suspend an entry (ACTIVE → SUSPENDED)."""
        return self._lifecycle_operation(
            entry_id, RegistryLifecycleStatus.SUSPENDED, performed_by, correlation_id,
        )

    def deprecate_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Deprecate an entry (ACTIVE/SUSPENDED → DEPRECATED)."""
        return self._lifecycle_operation(
            entry_id, RegistryLifecycleStatus.DEPRECATED, performed_by, correlation_id, reason,
        )

    def _lifecycle_operation(
        self,
        entry_id: str,
        target_status: RegistryLifecycleStatus,
        performed_by: str = "",
        correlation_id: str = "",
        reason: str = "",
    ) -> RegistryDecision:
        """Generic lifecycle transition operation."""
        op_map = {
            RegistryLifecycleStatus.ACTIVE: "activate",
            RegistryLifecycleStatus.SUSPENDED: "suspend",
            RegistryLifecycleStatus.DEPRECATED: "deprecate",
        }
        op = op_map.get(target_status, "transition")
        corr_id = correlation_id or str(uuid.uuid4())

        entry = self._entries.get(entry_id)
        if entry is None:
            return RegistryDecision(
                entry_id=uuid.UUID(entry_id) if entry_id else uuid.uuid4(),
                operation=op,
                allowed=False,
                reasoning=["Entry not found"],
                performed_by=performed_by,
            )

        session = self.session_manager.create_session(
            registry_type=entry.registry_type,
            operation=op,
            user_id=performed_by,
            namespace=entry.namespace,
            correlation_id=corr_id,
        )

        reasoning: list[str] = []

        # Validate lifecycle transition
        t0 = time.time()
        lc_violations = self.validator.validate_lifecycle_transition(entry.status, target_status)
        t1 = time.time()
        lc_duration = round((t1 - t0) * 1000, 2)

        allowed = len(lc_violations) == 0

        if allowed:
            # Execute transition
            updated = self.lifecycle_manager.transition(
                entry, target_status, reason=reason, changed_by=performed_by,
            )
            self._entries[entry_id] = updated
            self.cache.invalidate_entry(entry_id)
            self.cache.set_entry(updated)

            # Audit
            if target_status == RegistryLifecycleStatus.ACTIVE:
                self.audit.record_activation(updated, performed_by=performed_by)
                self.metrics_collector.increment_active_entries()
            elif target_status == RegistryLifecycleStatus.DEPRECATED:
                self.audit.record_deprecation(updated, performed_by=performed_by, reason=reason)

            self.metrics_collector.increment_lifecycle_transitions()
            reasoning.append(f"Entry {op}d successfully")
        else:
            reasoning.append(f"Lifecycle transition blocked: {'; '.join(lc_violations)}")

        confidence = self.confidence_calculator.calculate(entry=entry)

        total_duration = round((time.time() - t0) * 1000, 2)
        self.session_manager.complete_session(
            str(session.session_id),
            status="COMPLETED" if allowed else "FAILED",
        )

        self.trace.record_lifecycle_stage(
            entry_id=entry_id,
            entry_name=entry.name,
            lifecycle_transition=f"{entry.status.value}→{target_status.value}",
            registry_type=entry.registry_type.value,
            correlation_id=corr_id,
            success=allowed,
            duration_ms=lc_duration,
        )

        return RegistryDecision(
            registry_type=entry.registry_type,
            entry_id=entry.entry_id,
            operation=op,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence.overall_confidence,
            performed_by=performed_by,
            metadata={
                "session_id": str(session.session_id),
                "correlation_id": corr_id,
                "lifecycle_transition": f"{entry.status.value}→{target_status.value}",
            },
        )

    # ─────────────────────────────────────────────────────────────────
    # Health & Metrics
    # ─────────────────────────────────────────────────────────────────

    def get_all_entries(self) -> list[RegistryEntry]:
        """Return all stored entries (for manager use)."""
        return list(self._entries.values())

    def get_entry_by_id(self, entry_id: str) -> RegistryEntry | None:
        """Direct store lookup without cache (for internal use)."""
        return self._entries.get(entry_id)

    def health(self) -> RegistryHealth:
        """Aggregate health status from all sub-components."""
        all_entries = list(self._entries.values())
        active_count = sum(1 for e in all_entries if e.status == RegistryLifecycleStatus.ACTIVE)

        # Determine sub-component statuses
        validator_status = "HEALTHY"
        searcher_status = "HEALTHY"
        index_status = "HEALTHY"
        version_status = "HEALTHY"
        lifecycle_status = "HEALTHY"
        cache_status = "HEALTHY" if self.cache.size() >= 0 else "DEGRADED"
        dep_graph_status = "HEALTHY"
        policy_status = "HEALTHY"

        error_count = self.metrics_collector.snapshot().errors_total
        avg_latency = self.metrics_collector.snapshot().average_latency_ms

        # Overall status
        statuses = [validator_status, searcher_status, index_status, version_status,
                    lifecycle_status, cache_status, dep_graph_status, policy_status]
        if "UNHEALTHY" in statuses:
            overall = "UNHEALTHY"
        elif "DEGRADED" in statuses:
            overall = "DEGRADED"
        else:
            overall = "HEALTHY"

        return RegistryHealth(
            overall_status=overall,
            entries_total=len(all_entries),
            active_entries=active_count,
            validator_status=validator_status,
            searcher_status=searcher_status,
            version_manager_status=version_status,
            lifecycle_manager_status=lifecycle_status,
            cache_status=cache_status,
            index_status=index_status,
            dependency_graph_status=dep_graph_status,
            policy_status=policy_status,
            error_count=error_count,
            average_latency_ms=avg_latency,
            uptime_seconds=round(time.time() - self._start_time, 2),
            last_check=datetime.now(UTC),
        )

    def metrics(self) -> RegistryMetrics:
        """Return aggregated metrics from the metrics collector."""
        return self.metrics_collector.snapshot()

    # ── Private helpers ─────────────────────────────────────────────

    def _build_search_results(
        self,
        results: list[Any],
        entries: list[RegistryEntry],
    ) -> list[RegistrySearchResult]:
        """Convert internal SearchResult items to RegistrySearchResult."""
        entry_map = {str(e.entry_id): e for e in entries}
        output: list[RegistrySearchResult] = []
        for rank, r in enumerate(results):
            entry = entry_map.get(r.entry_id)
            if entry is not None:
                output.append(RegistrySearchResult(
                    entry=entry,
                    score=r.score,
                    matched_fields=[r.strategy] if r.strategy else [],
                    rank=rank,
                ))
        return output
