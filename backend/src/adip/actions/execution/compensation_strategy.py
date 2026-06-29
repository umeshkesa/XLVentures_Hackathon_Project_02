"""CompensationStrategyManager — rollback, compensation and recovery strategies.

Defines and manages compensation strategies for handling action
step failures, including rollback, compensation actions, retry
logic, manual recovery, and alternative actions.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import CompensationStrategy

log = structlog.get_logger(__name__)


class CompensationStrategyManager:
    """Manages compensation strategies for action step failures."""

    STRATEGY_TYPES = ["rollback", "compensation", "retry", "manual_recovery", "alternative"]

    def create_strategy(
        self,
        step_id: str = "",
        strategy_type: str = "rollback",
        parameters: dict | None = None,
        correlation_id: str = "",
    ) -> CompensationStrategy:
        """Create a compensation strategy for a step.

        Args:
            step_id: The step ID this strategy applies to.
            strategy_type: Type of strategy (rollback, compensation, retry, manual_recovery, alternative).
            parameters: Strategy parameters.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A CompensationStrategy with default parameters for the type.
        """
        parameters = parameters or {}

        if strategy_type == "rollback":
            desc = "Rollback step execution and restore previous state"
            params = {"rollback_priority": "CRITICAL", "restore_state": True, **(parameters or {})}
        elif strategy_type == "compensation":
            desc = "Execute compensating action to mitigate failure"
            params = {"compensation_action": "default_compensation", "async": True, **(parameters or {})}
        elif strategy_type == "retry":
            desc = "Retry the failed step"
            params = {"max_retries": 3, "retry_delay_seconds": 30, "backoff_multiplier": 2.0, **(parameters or {})}
        elif strategy_type == "manual_recovery":
            desc = "Manual intervention required for recovery"
            params = {"notify_role": "supervisor", "manual_steps": ["assess", "repair", "verify"], **(parameters or {})}
        elif strategy_type == "alternative":
            desc = "Execute alternative action instead of the failed step"
            params = {"alternative_action": "default_alternative", "fallback": True, **(parameters or {})}
        else:
            desc = "Unknown compensation strategy"
            params = dict(parameters or {})

        strategy = CompensationStrategy(
            step_id=step_id,
            strategy_type=strategy_type,
            description=desc,
            parameters=params,
        )
        log.info(
            "compensation_strategy.created",
            step_id=step_id,
            strategy_type=strategy_type,
            correlation_id=correlation_id,
        )
        return strategy

    def get_default_strategies(
        self,
        step_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> list[CompensationStrategy]:
        """Get default compensation strategies for a list of steps.

        Args:
            step_ids: List of step IDs.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of CompensationStrategies (one per step, rollback by default).
        """
        step_ids = step_ids or []
        strategies = [
            self.create_strategy(step_id=sid, strategy_type="rollback")
            for sid in step_ids
        ]
        return strategies

    def validate_strategy(
        self,
        strategy: CompensationStrategy,
    ) -> list[str]:
        """Validate a compensation strategy.

        Returns:
            List of validation violations (empty if valid).
        """
        violations: list[str] = []
        if strategy.strategy_type not in self.STRATEGY_TYPES:
            violations.append(f"Invalid strategy type: {strategy.strategy_type}")
        if not strategy.step_id:
            violations.append("Strategy must have a step ID")
        return violations
