"""Tests for MemoryHealth model."""

from __future__ import annotations

from adip.memory.orchestration.health import MemoryHealth


class TestMemoryHealth:
    def test_default_healthy(self) -> None:
        health = MemoryHealth()
        assert health.overall_status == "HEALTHY"
        assert health.router_status == "HEALTHY"
        assert health.coordinator_status == "HEALTHY"
        assert health.lifecycle_status == "HEALTHY"
        assert health.policy_status == "HEALTHY"
        assert health.cache_status == "HEALTHY"
        assert health.is_healthy() is True

    def test_storage_health_defaults(self) -> None:
        health = MemoryHealth()
        assert health.storage_status == {"HOT": "HEALTHY", "WARM": "HEALTHY", "COLD": "HEALTHY"}

    def test_tier_health_defaults(self) -> None:
        health = MemoryHealth()
        assert health.tier_health == {"HOT": "HEALTHY", "WARM": "HEALTHY", "COLD": "HEALTHY"}

    def test_is_healthy_true(self) -> None:
        health = MemoryHealth()
        assert health.is_healthy() is True
        health.overall_status = "HEALTHY"
        assert health.is_healthy() is True

    def test_is_healthy_false(self) -> None:
        health = MemoryHealth(overall_status="UNHEALTHY")
        assert health.is_healthy() is False

    def test_custom_values(self) -> None:
        health = MemoryHealth(
            overall_status="DEGRADED",
            error_count=5,
            average_latency_ms=150.5,
            last_successful_operation="Read record abc-123",
        )
        assert health.overall_status == "DEGRADED"
        assert health.error_count == 5
        assert health.average_latency_ms == 150.5
        assert health.last_successful_operation == "Read record abc-123"

    def test_last_checked_at(self) -> None:
        health = MemoryHealth()
        assert health.last_checked_at != ""

    def test_serialization(self) -> None:
        health = MemoryHealth(overall_status="HEALTHY")
        data = health.model_dump()
        assert data["overall_status"] == "HEALTHY"

    def test_operations_per_minute_default(self) -> None:
        health = MemoryHealth()
        assert health.operations_per_minute == 0.0

    def test_operations_per_minute_custom(self) -> None:
        health = MemoryHealth(operations_per_minute=120.5)
        assert health.operations_per_minute == 120.5

    def test_error_rate_default(self) -> None:
        health = MemoryHealth()
        assert health.error_rate == 0.0

    def test_error_rate_custom(self) -> None:
        health = MemoryHealth(error_rate=0.05)
        assert health.error_rate == 0.05

    def test_error_rate_validation(self) -> None:
        health = MemoryHealth(error_rate=1.0)
        assert health.error_rate == 1.0

    def test_error_rate_zero(self) -> None:
        health = MemoryHealth(error_rate=0.0)
        assert health.error_rate == 0.0

    def test_serialization_includes_new_fields(self) -> None:
        health = MemoryHealth(
            operations_per_minute=60.0,
            error_rate=0.01,
        )
        data = health.model_dump()
        assert data["operations_per_minute"] == 60.0
        assert data["error_rate"] == 0.01
