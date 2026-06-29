"""PlannerService — enterprise facade over the planning pipeline.

Architecture::

    API
     ↓
    PlannerService   ← validation, auth, audit, metrics, logging
     ↓
    PlannerAgent     ← pipeline orchestration
     ↓
    Planning Pipeline
"""

from __future__ import annotations

import time
import uuid

import structlog

from adip.planner.contracts.models import (
    PlanningRequest,
    PlanningResult,
)
from adip.planner.contracts.policy import PlanningPolicy
from adip.planner.interfaces.pipeline import PlannerInterface

log = structlog.get_logger(__name__)


class PlannerService:
    """Enterprise facade for plan creation.

    Wraps a ``PlannerInterface`` (e.g. ``PlannerAgent``) with validation,
    authorisation, audit, and metrics collection.
    """

    def __init__(
        self,
        planner: PlannerInterface,
        policy: PlanningPolicy | None = None,
    ) -> None:
        self._planner = planner
        self._policy = policy or PlanningPolicy()

    # ── Public API ─────────────────────────────────────────────────────

    async def create_plan(self, request: PlanningRequest) -> PlanningResult:
        """Validate, authorise, audit, and delegate to the planner."""
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(
            correlation_id=correlation_id,
            goal=request.goal.objective[:60],
        )
        start_time = time.monotonic()

        bound_log.info("planner_service.request_received")

        # 1. Validate request
        self._validate_request(request, bound_log)

        # 2. Authentication hook (placeholder)
        self._authenticate(request, bound_log)

        # 3. Authorisation hook (placeholder)
        self._authorize(request, bound_log)

        # 4. Audit hook
        self._audit(request, bound_log)

        # 5. Execute planning
        result = await self._planner.plan(request)

        # 6. Post-processing
        elapsed = (time.monotonic() - start_time) * 1000
        result.metrics.total_planning_time = elapsed
        result.metrics.execution_time_ms = elapsed
        result.metrics.planning_duration_ms = elapsed

        # Collect resource estimates (placeholder)
        result.metrics.cpu_time = elapsed * 0.8
        result.metrics.memory_usage = 128.0
        result.metrics.llm_latency = elapsed * 0.3

        # 7. Post-audit
        self._post_audit(result, bound_log)

        bound_log.info(
            "planner_service.completed",
            status=result.execution_status.value,
            duration_ms=round(elapsed, 2),
        )
        return result

    async def replan(self, *args, **kwargs) -> ...:
        """Delegate replanning to the underlying planner."""
        return await self._planner.replan(*args, **kwargs)

    # ── Internal hooks (overridable) ───────────────────────────────────

    def _validate_request(
        self, request: PlanningRequest, _log,
    ) -> None:
        """Validate the planning request.

        Raises ``ValidationError`` on failure (placeholder).
        """
        if not request.goal.objective.strip():
            msg = "Planning goal objective must not be empty."
            _log.warning("planner_service.validation_failed", reason=msg)
            raise ValueError(msg)

    def _authenticate(self, _request: PlanningRequest, _log) -> None:
        """Authentication placeholder."""
        _log.debug("planner_service.authenticate")

    def _authorize(self, _request: PlanningRequest, _log) -> None:
        """Authorisation placeholder."""
        _log.debug("planner_service.authorize")

    def _audit(self, _request: PlanningRequest, _log) -> None:
        """Audit logging placeholder."""
        _log.info("planner_service.audit")

    def _post_audit(self, _result: PlanningResult, _log) -> None:
        """Post-execution audit placeholder."""
        _log.debug("planner_service.post_audit")
