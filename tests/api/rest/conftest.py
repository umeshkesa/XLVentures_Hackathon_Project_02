"""Test fixtures for REST API Layer tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from adip.api.rest.middleware.registration import register_middleware
from adip.api.rest.openapi import configure_openapi
from adip.api.rest.routers import router


@pytest.fixture
def app() -> FastAPI:
    application = FastAPI(title="Test API", version="0.1.0")
    application.include_router(router)
    register_middleware(application)
    configure_openapi(application)
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
