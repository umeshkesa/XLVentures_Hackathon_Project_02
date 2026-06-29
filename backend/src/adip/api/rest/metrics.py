"""API Metrics — tracks API calls, errors, latency, and success rate."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class APIMetricsCollector:
    """Collects and exposes API-level metrics.

    Tracks:
    - Total API calls per route and method
    - Error counts per route and status code
    - Latency distribution (min, max, avg, p50, p95, p99)
    - Success rate per route
    - Compliance metrics (Phase 3.5)
    - Diagnostics metrics (Phase 3.5)
    """

    def __init__(self) -> None:
        self._call_counts: dict[str, int] = defaultdict(int)
        self._error_counts: dict[str, int] = defaultdict(int)
        self._latencies: dict[str, list[float]] = defaultdict(list)
        self._status_counts: dict[str, int] = defaultdict(int)
        self._success_counts: dict[str, int] = defaultdict(int)
        # Phase 3.5
        self._compliance_counts: dict[str, int] = defaultdict(int)
        self._diagnostics_counts: dict[str, int] = defaultdict(int)
        self._governance_counts: dict[str, int] = defaultdict(int)
        self._performance_count: int = 0
        self._performance_total_latency: float = 0.0

    def record_call(self, route_key: str, method: str, status_code: int, latency_ms: float) -> None:
        full_key = f"{method}:{route_key}"
        self._call_counts[full_key] += 1
        self._latencies[full_key].append(latency_ms)
        self._status_counts[f"{status_code}"] += 1
        if 200 <= status_code < 400:
            self._success_counts[full_key] += 1
        else:
            self._error_counts[full_key] += 1

    def record_compliance(self, check_name: str, is_compliant: bool) -> None:
        key = f"{'compliant' if is_compliant else 'non_compliant'}:{check_name}"
        self._compliance_counts[key] += 1

    def record_diagnostics(self, category: str) -> None:
        self._diagnostics_counts[category] += 1

    def record_governance(self, policy: str, is_compliant: bool) -> None:
        key = f"{'pass' if is_compliant else 'fail'}:{policy}"
        self._governance_counts[key] += 1

    def record_performance(self, latency_ms: float) -> None:
        self._performance_count += 1
        self._performance_total_latency += latency_ms

    def get_total_calls(self, route_key: str | None = None) -> int:
        if route_key:
            return self._call_counts.get(route_key, 0)
        return sum(self._call_counts.values())

    def get_total_errors(self, route_key: str | None = None) -> int:
        if route_key:
            return self._error_counts.get(route_key, 0)
        return sum(self._error_counts.values())

    def get_success_rate(self, route_key: str | None = None) -> float:
        if route_key:
            total = self._call_counts.get(route_key, 0)
            success = self._success_counts.get(route_key, 0)
        else:
            total = sum(self._call_counts.values())
            success = sum(self._success_counts.values())
        if total == 0:
            return 1.0
        return success / total

    def get_average_latency(self, route_key: str | None = None) -> float:
        if route_key:
            latencies = self._latencies.get(route_key, [])
        else:
            latencies = [l for vals in self._latencies.values() for l in vals]
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)

    def get_latency_percentile(self, percentile: float, route_key: str | None = None) -> float:
        if route_key:
            latencies = sorted(self._latencies.get(route_key, []))
        else:
            latencies = sorted(l for vals in self._latencies.values() for l in vals)
        if not latencies:
            return 0.0
        index = max(0, min(len(latencies) - 1, int(len(latencies) * percentile)))
        return latencies[index]

    def get_metrics_snapshot(self) -> dict[str, Any]:
        total_calls = self.get_total_calls()
        total_errors = self.get_total_errors()
        return {
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": total_errors / total_calls if total_calls > 0 else 0.0,
            "success_rate": self.get_success_rate(),
            "average_latency_ms": round(self.get_average_latency(), 2),
            "p50_latency_ms": round(self.get_latency_percentile(0.5), 2),
            "p95_latency_ms": round(self.get_latency_percentile(0.95), 2),
            "p99_latency_ms": round(self.get_latency_percentile(0.99), 2),
            "routes_monitored": len(self._call_counts),
            # Phase 3.5
            "compliance_checks": dict(self._compliance_counts),
            "diagnostics_by_category": dict(self._diagnostics_counts),
            "governance_checks": dict(self._governance_counts),
            "performance_samples": self._performance_count,
        }

    def reset(self) -> None:
        self._call_counts.clear()
        self._error_counts.clear()
        self._latencies.clear()
        self._status_counts.clear()
        self._success_counts.clear()
        self._compliance_counts.clear()
        self._diagnostics_counts.clear()
        self._governance_counts.clear()
        self._performance_count = 0
        self._performance_total_latency = 0.0
