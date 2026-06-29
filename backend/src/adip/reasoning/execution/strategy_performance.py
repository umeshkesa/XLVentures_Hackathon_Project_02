"""StrategyPerformance — tracks execution performance of reasoning strategies.

Records and analyses execution metrics for reasoning strategies
including success rates, latency, and confidence.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.reasoning.enums import ReasoningStrategyType
from adip.reasoning.execution.models import StrategyPerformanceRecord

log = structlog.get_logger(__name__)


class StrategyPerformance:
    """Tracks execution performance of reasoning strategies.

    Deterministic placeholder that records execution metrics for
    reasoning strategies and provides analytics on success rates,
    failure rates, average latency, and average confidence.
    """

    def __init__(self) -> None:
        self._records: dict[ReasoningStrategyType, StrategyPerformanceRecord] = {}

    def record_execution(
        self,
        strategy: ReasoningStrategyType,
        success: bool,
        latency_ms: float,
        confidence: float,
    ) -> StrategyPerformanceRecord:
        """Record an execution for a strategy.

        Args:
            strategy: The reasoning strategy type.
            success: Whether the execution was successful.
            latency_ms: Execution latency in milliseconds.
            confidence: Confidence score (0.0–1.0).

        Returns:
            The updated StrategyPerformanceRecord.
        """
        if strategy not in self._records:
            self._records[strategy] = StrategyPerformanceRecord(
                strategy=strategy,
                total_executions=0,
                successful=0,
                failed=0,
                total_latency_ms=0.0,
                total_confidence=0.0,
                last_executed=datetime.now(UTC),
            )

        record = self._records[strategy]
        record.total_executions += 1
        if success:
            record.successful += 1
        else:
            record.failed += 1
        record.total_latency_ms += latency_ms
        record.total_confidence += confidence
        record.last_executed = datetime.now(UTC)

        log.info(
            "strategy_performance.record",
            strategy=strategy.value,
            success=success,
            latency_ms=latency_ms,
            total_executions=record.total_executions,
        )
        return record

    def get_performance(
        self,
        strategy: ReasoningStrategyType,
    ) -> StrategyPerformanceRecord | None:
        """Get performance record for a specific strategy.

        Args:
            strategy: The reasoning strategy type.

        Returns:
            The StrategyPerformanceRecord if found, else None.
        """
        return self._records.get(strategy)

    def get_all_performance(self) -> dict[str, StrategyPerformanceRecord]:
        """Get performance records for all strategies.

        Returns:
            Dictionary mapping strategy name to StrategyPerformanceRecord.
        """
        return {k.value: v for k, v in self._records.items()}

    def get_success_rate(
        self,
        strategy: ReasoningStrategyType | None = None,
    ) -> float:
        """Get success rate for a strategy or all strategies.

        Args:
            strategy: Optional strategy to filter by.

        Returns:
            Success rate (0.0–1.0) or 0.0 if no executions.
        """
        if strategy:
            record = self._records.get(strategy)
            if not record or record.total_executions == 0:
                return 0.0
            return round(record.successful / record.total_executions, 4)

        total_execs = sum(r.total_executions for r in self._records.values())
        total_successes = sum(r.successful for r in self._records.values())
        if total_execs == 0:
            return 0.0
        return round(total_successes / total_execs, 4)

    def get_failure_rate(
        self,
        strategy: ReasoningStrategyType | None = None,
    ) -> float:
        """Get failure rate for a strategy or all strategies.

        Args:
            strategy: Optional strategy to filter by.

        Returns:
            Failure rate (0.0–1.0) or 0.0 if no executions.
        """
        if strategy:
            record = self._records.get(strategy)
            if not record or record.total_executions == 0:
                return 0.0
            return round(record.failed / record.total_executions, 4)

        total_execs = sum(r.total_executions for r in self._records.values())
        total_failures = sum(r.failed for r in self._records.values())
        if total_execs == 0:
            return 0.0
        return round(total_failures / total_execs, 4)

    def get_average_latency(
        self,
        strategy: ReasoningStrategyType | None = None,
    ) -> float:
        """Get average latency for a strategy or all strategies.

        Args:
            strategy: Optional strategy to filter by.

        Returns:
            Average latency in milliseconds, or 0.0 if no executions.
        """
        if strategy:
            record = self._records.get(strategy)
            if not record or record.total_executions == 0:
                return 0.0
            return round(record.total_latency_ms / record.total_executions, 2)

        total_execs = sum(r.total_executions for r in self._records.values())
        total_latency = sum(r.total_latency_ms for r in self._records.values())
        if total_execs == 0:
            return 0.0
        return round(total_latency / total_execs, 2)

    def get_average_confidence(
        self,
        strategy: ReasoningStrategyType | None = None,
    ) -> float:
        """Get average confidence for a strategy or all strategies.

        Args:
            strategy: Optional strategy to filter by.

        Returns:
            Average confidence (0.0–1.0), or 0.0 if no executions.
        """
        if strategy:
            record = self._records.get(strategy)
            if not record or record.total_executions == 0:
                return 0.0
            return round(record.total_confidence / record.total_executions, 4)

        total_execs = sum(r.total_executions for r in self._records.values())
        total_confidence = sum(r.total_confidence for r in self._records.values())
        if total_execs == 0:
            return 0.0
        return round(total_confidence / total_execs, 4)

    def clear(self) -> None:
        """Clear all performance records."""
        self._records.clear()

    def count(self) -> int:
        """Get the number of tracked strategy performance records.

        Returns:
            Strategy performance record count.
        """
        return len(self._records)
