"""APIPerformanceProfile — tracks API latency, throughput, P95, P99, and error rate.

Phase 3.5 performance profiling for production readiness.
"""

from __future__ import annotations

import time
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class PerformanceProfile:
    """Performance profile snapshot for a route or component."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.latencies_ms: list[float] = []
        self.timestamps: list[float] = []
        self.error_count: int = 0
        self.success_count: int = 0

    def record(self, latency_ms: float, is_error: bool = False) -> None:
        self.latencies_ms.append(latency_ms)
        self.timestamps.append(time.monotonic())
        if is_error:
            self.error_count += 1
        else:
            self.success_count += 1

    @property
    def total_requests(self) -> int:
        return self.success_count + self.error_count

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.error_count / self.total_requests

    @property
    def throughput(self) -> float:
        if len(self.timestamps) < 2:
            return 0.0
        duration = self.timestamps[-1] - self.timestamps[0]
        if duration <= 0:
            return 0.0
        return self.total_requests / duration

    def get_percentile(self, percentile: float) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_lats = sorted(self.latencies_ms)
        index = max(0, min(len(sorted_lats) - 1, int(len(sorted_lats) * percentile)))
        return sorted_lats[index]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "total_requests": self.total_requests,
            "average_latency_ms": round(sum(self.latencies_ms) / len(self.latencies_ms), 2) if self.latencies_ms else 0.0,
            "p50_ms": round(self.get_percentile(0.5), 2),
            "p95_ms": round(self.get_percentile(0.95), 2),
            "p99_ms": round(self.get_percentile(0.99), 2),
            "min_ms": round(min(self.latencies_ms), 2) if self.latencies_ms else 0.0,
            "max_ms": round(max(self.latencies_ms), 2) if self.latencies_ms else 0.0,
            "error_rate": round(self.error_rate, 4),
            "throughput_rps": round(self.throughput, 2),
            "success_count": self.success_count,
            "error_count": self.error_count,
        }


class APIPerformanceProfile:
    """Tracks performance profiles for named routes and components."""

    def __init__(self) -> None:
        self._profiles: dict[str, PerformanceProfile] = {}

    def record(self, name: str, latency_ms: float, is_error: bool = False) -> PerformanceProfile:
        if name not in self._profiles:
            self._profiles[name] = PerformanceProfile(name)
        self._profiles[name].record(latency_ms, is_error)
        return self._profiles[name]

    def get_profile(self, name: str) -> PerformanceProfile | None:
        return self._profiles.get(name)

    def get_all_profiles(self) -> dict[str, dict[str, Any]]:
        return {name: profile.to_dict() for name, profile in self._profiles.items()}

    def get_summary(self) -> dict[str, Any]:
        if not self._profiles:
            return {
                "total_routes": 0,
                "total_requests": 0,
                "overall_error_rate": 0.0,
                "overall_throughput_rps": 0.0,
            }
        total_requests = sum(p.total_requests for p in self._profiles.values())
        total_errors = sum(p.error_count for p in self._profiles.values())
        all_latencies = [l for p in self._profiles.values() for l in p.latencies_ms]
        overall_error_rate = total_errors / total_requests if total_requests > 0 else 0.0
        return {
            "total_routes": len(self._profiles),
            "total_requests": total_requests,
            "overall_error_rate": round(overall_error_rate, 4),
            "overall_average_latency_ms": round(sum(all_latencies) / len(all_latencies), 2) if all_latencies else 0.0,
            "overall_p95_ms": round(sorted(all_latencies)[int(len(all_latencies) * 0.95)], 2) if all_latencies else 0.0,
            "overall_p99_ms": round(sorted(all_latencies)[int(len(all_latencies) * 0.99)], 2) if all_latencies else 0.0,
        }

    def reset(self) -> None:
        self._profiles.clear()
