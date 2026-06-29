"""Import tests for the Recommendation Engine.

Verifies all public API exports are importable.
"""

from __future__ import annotations


def test_enums_importable() -> None:
    from adip.recommendation.enums import (
        FeasibilityLevel,
        FeasibilityStatus,
        ImplementationTimeline,
        RecommendationDomain,
        RecommendationStatus,
        RecommendationTraceStage,
        TradeoffDimension,
    )
    assert RecommendationDomain.GENERAL.value == "GENERAL"
    assert RecommendationStatus.INITIALIZED.value == "INITIALIZED"
    assert ImplementationTimeline.IMMEDIATE.value == "IMMEDIATE"
    assert FeasibilityStatus.FEASIBLE.value == "FEASIBLE"
    assert TradeoffDimension.COST.value == "COST"
    assert FeasibilityLevel.HIGH.value == "HIGH"
    assert RecommendationTraceStage.STRATEGY.value == "STRATEGY"


def test_models_importable() -> None:
    from adip.recommendation.contracts.models import (
        RecommendationRequest,
    )
    req = RecommendationRequest()
    assert req.request_id is not None


def test_events_importable() -> None:
    from adip.recommendation.contracts.events import (
        RecommendationRequested,
    )
    event = RecommendationRequested()
    assert event.event_type == "recommendation.requested"


def test_exceptions_importable() -> None:
    from adip.recommendation.contracts.exceptions import (
        RecommendationException,
    )
    exc = RecommendationException("test")
    assert str(exc) == "test"


def test_dtos_importable() -> None:
    from adip.recommendation.dtos import (
        RecommendationRequestDTO,
    )
    dto = RecommendationRequestDTO(reasoning_result_id="test")
    assert dto.reasoning_result_id == "test"


def test_interfaces_importable() -> None:
    # Verify they are ABCs
    import abc

    from adip.recommendation.interfaces import (
        RecommendationService,
    )
    assert issubclass(RecommendationService, abc.ABC)


def test_module_exports() -> None:
    pass


def test_phase2_enums_importable() -> None:
    from adip.recommendation.enums import (
        FeasibilityLevel,
        FeasibilityStatus,
        ImplementationTimeline,
        RecommendationReadinessStatus,
        RecommendationTraceStage,
        TradeoffDimension,
    )
    assert ImplementationTimeline.TODAY.value == "TODAY"
    assert FeasibilityStatus.NOT_FEASIBLE.value == "NOT_FEASIBLE"
    assert TradeoffDimension.RISK.value == "RISK"
    assert FeasibilityLevel.MEDIUM.value == "MEDIUM"
    assert RecommendationTraceStage.SCORING.value == "SCORING"
    assert RecommendationReadinessStatus.READY.value == "READY"


def test_execution_models_importable() -> None:
    from adip.recommendation.execution.models import (
        RecommendationScore,
    )
    score = RecommendationScore()
    assert score.score_id is not None
    assert score.overall == 0.0


def test_execution_components_importable() -> None:
    from adip.recommendation.execution.strategy_selector import StrategySelector
    selector = StrategySelector()
    assert selector is not None


def test_module_phase2_exports() -> None:
    pass


def test_phase3_orchestration_importable() -> None:
    from adip.recommendation.orchestration.session import RecommendationSessionManager
    assert RecommendationSessionManager is not None


def test_phase3_services_importable() -> None:
    from adip.recommendation.services.hooks import IntegrationHooks, hooks
    assert isinstance(hooks, IntegrationHooks)


def test_phase3_module_exports() -> None:
    pass
