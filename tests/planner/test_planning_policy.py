"""Tests for the PlanningPolicy model."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from adip.planner.contracts.policy import PlanningPolicy


class TestPlanningPolicyDefaults:
    def test_default_values(self) -> None:
        policy = PlanningPolicy()
        assert policy.auto_execute_threshold == 70.0
        assert policy.confirmation_threshold == 50.0
        assert policy.clarification_threshold == 30.0
        assert policy.max_replans == 3
        assert policy.max_parallel_tasks == 10
        assert policy.optimization_enabled is True
        assert policy.confidence_strategy == "weighted_average"

    def test_custom_values(self) -> None:
        policy = PlanningPolicy(
            auto_execute_threshold=85.0,
            max_replans=5,
            optimization_enabled=False,
            confidence_strategy="minimum",
        )
        assert policy.auto_execute_threshold == 85.0
        assert policy.max_replans == 5
        assert policy.optimization_enabled is False
        assert policy.confidence_strategy == "minimum"

    def test_auto_execute_threshold_bounds(self) -> None:
        PlanningPolicy(auto_execute_threshold=0.0)
        PlanningPolicy(auto_execute_threshold=100.0)
        with pytest.raises(ValidationError):
            PlanningPolicy(auto_execute_threshold=-1.0)
        with pytest.raises(ValidationError):
            PlanningPolicy(auto_execute_threshold=101.0)

    def test_max_replans_ge_zero(self) -> None:
        PlanningPolicy(max_replans=0)
        with pytest.raises(ValidationError):
            PlanningPolicy(max_replans=-1)

    def test_max_parallel_tasks_ge_one(self) -> None:
        PlanningPolicy(max_parallel_tasks=1)
        with pytest.raises(ValidationError):
            PlanningPolicy(max_parallel_tasks=0)
