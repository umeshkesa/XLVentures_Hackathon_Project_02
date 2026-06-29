"""System API router — health checks, readiness probes, and version info.

This router provides infrastructure endpoints for monitoring, orchestration,
and CI/CD pipelines. No business logic is contained here.
"""

from __future__ import annotations

import time

from fastapi import APIRouter

from adip import __version__
from adip.api.rest.models.health import HealthResponse, LiveResponse, ReadyResponse, VersionResponse

router = APIRouter(tags=["System"])

_start_time: float = time.monotonic()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the overall health status of the API.",
)
async def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=__version__,
        uptime_seconds=time.monotonic() - _start_time,
    )


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness probe",
    description="Indicates whether the API is ready to accept traffic.",
)
async def ready() -> ReadyResponse:
    return ReadyResponse(
        ready=True,
        version=__version__,
    )


@router.get(
    "/live",
    response_model=LiveResponse,
    summary="Liveness probe",
    description="Indicates whether the API process is alive.",
)
async def live() -> LiveResponse:
    return LiveResponse(alive=True)


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Version information",
    description="Returns the current API version.",
)
async def version() -> VersionResponse:
    return VersionResponse(version=__version__)
