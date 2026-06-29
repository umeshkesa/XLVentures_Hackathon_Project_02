"""REST API routers package — aggregates all domain routers under /api/v1."""

from __future__ import annotations

from fastapi import APIRouter

from adip.api.rest.enums import ApiVersion
from adip.api.rest.versioning import get_api_prefix

router = APIRouter(prefix=get_api_prefix(ApiVersion.V1))

from adip.api.rest.routers.action_engine import router as action_engine_router
from adip.api.rest.routers.action_manager import router as action_manager_router
from adip.api.rest.routers.decision_review import router as decision_review_router
from adip.api.rest.routers.energy import router as energy_router
from adip.api.rest.routers.evidence import router as evidence_router
from adip.api.rest.routers.import_upload import router as import_upload_router
from adip.api.rest.routers.interaction import router as interaction_router
from adip.api.rest.routers.llm import router as llm_router
from adip.api.rest.routers.explainability import router as explainability_router
from adip.api.rest.routers.knowledge import router as knowledge_router
from adip.api.rest.routers.memory import router as memory_router
from adip.api.rest.routers.planner import router as planner_router
from adip.api.rest.routers.plugins import router as plugins_router
from adip.api.rest.routers.reasoning import router as reasoning_router
from adip.api.rest.routers.recommendation import router as recommendation_router
from adip.api.rest.routers.registry import router as registry_router
from adip.api.rest.routers.rules import router as rules_router
from adip.api.rest.routers.system import router as system_router
from adip.api.rest.routers.workflow import router as workflow_router

router.include_router(planner_router)
router.include_router(workflow_router)
router.include_router(memory_router)
router.include_router(knowledge_router)
router.include_router(rules_router)
router.include_router(plugins_router)
router.include_router(registry_router)
router.include_router(evidence_router)
router.include_router(reasoning_router)
router.include_router(recommendation_router)
router.include_router(explainability_router)
router.include_router(decision_review_router)
router.include_router(action_manager_router)
router.include_router(action_engine_router)
router.include_router(energy_router)
router.include_router(interaction_router)
router.include_router(llm_router)
router.include_router(import_upload_router)
router.include_router(system_router)

__all__ = ["router"]
