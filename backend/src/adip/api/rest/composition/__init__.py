"""API Composition Layer — aggregates data from multiple domains."""

from __future__ import annotations

from adip.api.rest.composition.ai_overview import AIOverviewComposition
from adip.api.rest.composition.base import BaseCompositionService
from adip.api.rest.composition.cache import CompositionCache
from adip.api.rest.composition.dashboard import DashboardComposition
from adip.api.rest.composition.energy_overview import EnergyOverviewComposition
from adip.api.rest.composition.operations_overview import OperationsOverviewComposition
from adip.api.rest.composition.workflow_overview import WorkflowOverviewComposition

__all__ = [
    "BaseCompositionService",
    "DashboardComposition",
    "AIOverviewComposition",
    "EnergyOverviewComposition",
    "WorkflowOverviewComposition",
    "OperationsOverviewComposition",
    "CompositionCache",
]
