"""Service Adapter Layer — bridges REST routers to platform services."""

from __future__ import annotations

from adip.api.rest.adapters.action_engine import ActionEngineAdapter
from adip.api.rest.adapters.action_manager import ActionManagerAdapter
from adip.api.rest.adapters.base import BaseServiceAdapter
from adip.api.rest.adapters.decision_review import DecisionReviewAdapter
from adip.api.rest.adapters.energy import EnergyAdapter
from adip.api.rest.adapters.evidence import EvidenceAdapter
from adip.api.rest.adapters.explainability import ExplainabilityAdapter
from adip.api.rest.adapters.interaction import InteractionAdapter
from adip.api.rest.adapters.knowledge import KnowledgeAdapter
from adip.api.rest.adapters.llm import LLMAdapter
from adip.api.rest.adapters.memory import MemoryAdapter
from adip.api.rest.adapters.planner import PlannerAdapter
from adip.api.rest.adapters.plugins import PluginsAdapter
from adip.api.rest.adapters.reasoning import ReasoningAdapter
from adip.api.rest.adapters.recommendation import RecommendationAdapter
from adip.api.rest.adapters.registry_adapter import RegistryAdapter as RegistryAdapter
from adip.api.rest.adapters.router_registry import (
    clear_registry,
    get_adapter,
    get_all_adapters,
    get_all_routers,
    get_registered_domains,
    get_router,
    register_adapter,
    register_router,
)
from adip.api.rest.adapters.rules import RulesAdapter
from adip.api.rest.adapters.workflow import WorkflowAdapter

__all__ = [
    "BaseServiceAdapter",
    "PlannerAdapter",
    "WorkflowAdapter",
    "MemoryAdapter",
    "KnowledgeAdapter",
    "RulesAdapter",
    "PluginsAdapter",
    "RegistryAdapter",
    "EvidenceAdapter",
    "ReasoningAdapter",
    "RecommendationAdapter",
    "ExplainabilityAdapter",
    "InteractionAdapter",
    "LLMAdapter",
    "DecisionReviewAdapter",
    "ActionManagerAdapter",
    "ActionEngineAdapter",
    "EnergyAdapter",
    "register_adapter",
    "register_router",
    "get_adapter",
    "get_router",
    "get_all_adapters",
    "get_all_routers",
    "get_registered_domains",
    "clear_registry",
]
