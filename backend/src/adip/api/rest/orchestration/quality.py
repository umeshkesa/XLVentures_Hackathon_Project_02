"""APIQualityManager — evaluates API quality across validation, contract compliance, response completeness, processing time, request completeness, and performance.

Phase 3.5 adds request_completeness and performance dimensions.
"""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class QualityScore:
    """Quality score for a single dimension."""

    def __init__(self, dimension: str, score: float = 1.0, details: str = "") -> None:
        self.dimension = dimension
        self.score = max(0.0, min(1.0, score))
        self.details = details


class APIQualityManager:
    """Evaluates API quality across multiple dimensions.

    Dimensions:
    - Validation Quality
    - Contract Compliance
    - Response Completeness
    - Processing Time
    - Request Completeness (Phase 3.5)
    - Performance (Phase 3.5)
    """

    def __init__(self) -> None:
        self._scores: dict[str, QualityScore] = {}

    def evaluate_validation_quality(self, passed: bool, total_checks: int = 1, failed_checks: int = 0) -> QualityScore:
        score = 1.0 if passed else max(0.0, 1.0 - (failed_checks / max(total_checks, 1)))
        qs = QualityScore("validation", score, f"{'Passed' if passed else 'Failed'} ({failed_checks}/{total_checks} checks failed)")
        self._scores["validation"] = qs
        return qs

    def evaluate_contract_compliance(self, is_compliant: bool) -> QualityScore:
        score = 1.0 if is_compliant else 0.0
        qs = QualityScore("contract_compliance", score, "Compliant" if is_compliant else "Non-compliant")
        self._scores["contract_compliance"] = qs
        return qs

    def evaluate_response_completeness(self, has_data: bool, has_errors: bool = False) -> QualityScore:
        if has_errors:
            score = 0.5
        elif has_data:
            score = 1.0
        else:
            score = 0.0
        qs = QualityScore("response_completeness", score, f"Data: {has_data}, Errors: {has_errors}")
        self._scores["response_completeness"] = qs
        return qs

    def evaluate_processing_time(self, processing_time_ms: float, threshold_ms: float = 1000.0) -> QualityScore:
        score = max(0.0, 1.0 - (processing_time_ms / threshold_ms))
        score = min(1.0, score)
        qs = QualityScore("processing_time", score, f"{processing_time_ms:.1f}ms (threshold: {threshold_ms}ms)")
        self._scores["processing_time"] = qs
        return qs

    def evaluate_request_completeness(self, has_body: bool, has_headers: bool = True, has_query: bool = True) -> QualityScore:
        present = sum([has_body, has_headers, has_query])
        score = present / 3.0
        qs = QualityScore("request_completeness", score, f"Body: {has_body}, Headers: {has_headers}, Query: {has_query}")
        self._scores["request_completeness"] = qs
        return qs

    def evaluate_performance(self, p95_latency_ms: float, error_rate: float, threshold_p95_ms: float = 2000.0) -> QualityScore:
        latency_score = max(0.0, 1.0 - (p95_latency_ms / threshold_p95_ms))
        error_score = 1.0 - error_rate
        score = (latency_score * 0.6) + (error_score * 0.4)
        score = max(0.0, min(1.0, score))
        qs = QualityScore("performance", score, f"P95: {p95_latency_ms:.1f}ms, error_rate: {error_rate:.4f}")
        self._scores["performance"] = qs
        return qs

    def get_overall_quality(self) -> float:
        if not self._scores:
            return 1.0
        return sum(s.score for s in self._scores.values()) / len(self._scores)

    def get_quality_report(self) -> dict[str, Any]:
        return {
            "overall_score": round(self.get_overall_quality(), 4),
            "dimensions": {
                name: {"score": qs.score, "details": qs.details}
                for name, qs in self._scores.items()
            },
            "dimension_count": len(self._scores),
        }

    def reset(self) -> None:
        self._scores.clear()
