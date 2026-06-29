"""Tests for REST API middleware — correlation, logging, exception handling, metrics."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from adip.api.rest.middleware.metrics import MetricsMiddleware


class TestCorrelationMiddleware:
    def test_correlation_id_in_response(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert "x-correlation-id" in response.headers
        assert response.headers["x-correlation-id"] is not None

    def test_correlation_id_passthrough(self, client: TestClient) -> None:
        response = client.get(
            "/api/v1/health",
            headers={"X-Correlation-ID": "custom-correlation-id"},
        )
        assert response.headers["x-correlation-id"] == "custom-correlation-id"


class TestValidationExceptionHandler:
    def test_handler_registered(self, app: FastAPI) -> None:
        assert len(app.exception_handlers) > 0


class TestMetricsMiddleware:
    def test_metrics_collected(self, client: TestClient) -> None:
        MetricsMiddleware.reset()
        assert MetricsMiddleware.get_request_count() == 0

        client.get("/api/v1/health")
        client.get("/api/v1/version")

        assert MetricsMiddleware.get_request_count() > 0

    def test_metrics_route_specific(self, client: TestClient) -> None:
        MetricsMiddleware.reset()
        client.get("/api/v1/health")
        count = MetricsMiddleware.get_request_count("GET:/api/v1/health")
        assert count >= 1

    def test_active_requests(self, client: TestClient) -> None:
        MetricsMiddleware.reset()
        assert MetricsMiddleware.get_active_requests() == 0
        client.get("/api/v1/health")
        assert MetricsMiddleware.get_active_requests() == 0


class TestResponseWrapperUsage:
    """Verify endpoint responses can be wrapped in ApiResponse format."""

    def test_system_endpoints_return_valid_json(self, client: TestClient) -> None:
        for endpoint in ["/api/v1/health", "/api/v1/ready", "/api/v1/live", "/api/v1/version"]:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"


class TestExceptionHandling:
    def test_not_found_returns_error(self, client: TestClient) -> None:
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_bad_request_returns_error(self, client: TestClient) -> None:
        response = client.post("/api/v1/health", json={"invalid": "data"})
        assert response.status_code in (405, 422)
