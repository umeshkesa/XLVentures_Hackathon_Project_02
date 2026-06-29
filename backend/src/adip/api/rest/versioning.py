"""API versioning support."""

from __future__ import annotations

from fastapi import APIRouter

from adip.api.rest.enums import ApiVersion

API_V1_PREFIX = "/api/v1"
API_V2_PREFIX = "/api/v2"


def create_versioned_router(version: ApiVersion = ApiVersion.V1) -> APIRouter:
    prefix = API_V1_PREFIX if version == ApiVersion.V1 else API_V2_PREFIX
    return APIRouter(prefix=prefix)


def get_api_prefix(version: ApiVersion = ApiVersion.V1) -> str:
    return API_V1_PREFIX if version == ApiVersion.V1 else API_V2_PREFIX
