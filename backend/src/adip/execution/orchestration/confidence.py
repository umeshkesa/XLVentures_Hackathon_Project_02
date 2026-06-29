"""ExecutionConfidenceCalculator — multi-dimensional confidence for execution.

Deterministic placeholder implementing 7-dimension weighted
confidence scoring: resource, schedule, risk, quality, readiness,
retry, and compensation.
"""

from __future__ import annotations

import structlog

from adip.execution.contracts.models import ExecutionConfidence

log = structlog.get_logger(__name__)


class ExecutionConfidenceCalculator:
    """Calculates multi-dimensional confidence for execution operations.

    Combines 7 weighted dimensions into an overall confidence
    score between 0.0 and 1.0.
    """

    RESOURCE_WEIGHT = 0.15
    SCHEDULE_WEIGHT = 0.15
    RISK_WEIGHT = 0.15
    QUALITY_WEIGHT = 0.15
    READINESS_WEIGHT = 0.15
    RETRY_WEIGHT = 0.10
    COMPENSATION_WEIGHT = 0.15

    def __init__(self) -> None:
        self._history: list[ExecutionConfidence] = []

    def calculate(
        self,
        resource_confidence: float = 0.0,
        schedule_confidence: float = 0.0,
        risk_confidence: float = 0.0,
        quality_confidence: float = 0.0,
        readiness_confidence: float = 0.0,
        retry_confidence: float = 0.0,
        compensation_confidence: float = 0.0,
    ) -> ExecutionConfidence:
        """Calculate overall confidence from individual dimensions.

        All inputs are clamped to [0.0, 1.0]. The overall score
        is a weighted average of all 7 dimensions.

        Args:
            resource_confidence: Resource availability confidence.
            schedule_confidence: Schedule feasibility confidence.
            risk_confidence: Risk assessment confidence.
            quality_confidence: Execution quality confidence.
            readiness_confidence: Readiness assessment confidence.
            retry_confidence: Retry effectiveness confidence.
            compensation_confidence: Compensation readiness confidence.

        Returns:
            ExecutionConfidence with all dimension scores.
        """
        rc = max(0.0, min(1.0, resource_confidence))
        sc = max(0.0, min(1.0, schedule_confidence))
        rk = max(0.0, min(1.0, risk_confidence))
        qc = max(0.0, min(1.0, quality_confidence))
        rd = max(0.0, min(1.0, readiness_confidence))
        rt = max(0.0, min(1.0, retry_confidence))
        cm = max(0.0, min(1.0, compensation_confidence))

        overall = (
            rc * self.RESOURCE_WEIGHT
            + sc * self.SCHEDULE_WEIGHT
            + rk * self.RISK_WEIGHT
            + qc * self.QUALITY_WEIGHT
            + rd * self.READINESS_WEIGHT
            + rt * self.RETRY_WEIGHT
            + cm * self.COMPENSATION_WEIGHT
        )

        confidence = ExecutionConfidence(
            overall_confidence=round(overall, 4),
            resource_confidence=rc,
            schedule_confidence=sc,
            risk_confidence=rk,
            quality_confidence=qc,
            readiness_confidence=rd,
            retry_confidence=rt,
            compensation_confidence=cm,
        )
        self._history.append(confidence)
        log.info(
            "confidence.calculated",
            overall=round(overall, 4),
        )
        return confidence

    def get_history(self) -> list[ExecutionConfidence]:
        """Get all calculated confidence scores.

        Returns:
            List of ExecutionConfidence in calculation order.
        """
        return list(self._history)
