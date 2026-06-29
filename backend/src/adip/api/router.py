"""Top-level API router.

Aggregates versioned REST API routers (15 domain + system) and the legacy
auth router.  The REST API routers carry their own ``/api/v1`` prefix so
they are mounted directly in the factory alongside this router.
"""

from fastapi import APIRouter

from adip.api.auth.router import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router)
