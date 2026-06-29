"""Tests for REST API routers — health endpoints and router structure."""

from __future__ import annotations

from fastapi.testclient import TestClient

from adip.api.rest.routers import router


class TestHealthEndpoints:
    def test_health_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_ready_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/v1/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "version" in data

    def test_live_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/v1/live")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True

    def test_version_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/v1/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data


class TestRouterStructure:
    def test_router_has_correct_prefix(self) -> None:
        assert router.prefix == "/api/v1"

    def test_all_domain_routers_included(self) -> None:
        route_paths = {route.path for route in router.routes}
        expected_health_routes = {
            "/api/v1/health",
            "/api/v1/ready",
            "/api/v1/live",
            "/api/v1/version",
        }
        for path in expected_health_routes:
            assert path in route_paths, f"Expected route {path} not found"

    def test_system_router_health_endpoints(self, client) -> None:
        for endpoint in ["/api/v1/health", "/api/v1/ready", "/api/v1/live", "/api/v1/version"]:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Expected 200 for {endpoint}"

    def test_domain_routers_accessible(self, client) -> None:
        """Phase 2 domain routers are accessible via their prefixes."""
        reachable_endpoints: dict[str, int] = {
            # System endpoints
            "/api/v1/health": 200,
            "/api/v1/ready": 200,
            "/api/v1/live": 200,
            "/api/v1/version": 200,
            # Domain routers with list endpoints
            "/api/v1/planner/plans": 200,
            "/api/v1/workflow/workflows": 200,
            "/api/v1/rules/list-rules": 404,
            "/api/v1/rules/rules-list": 200,
            "/api/v1/plugins": 200,
            "/api/v1/reasoning": 200,
            "/api/v1/recommendation": 200,
            "/api/v1/explainability": 200,
            "/api/v1/decision-review/reviews": 200,
            "/api/v1/action-manager/actions": 200,
            "/api/v1/action-engine/executions": 200,
            "/api/v1/energy/assets": 200,
            # Interaction module
            "/api/v1/interactions": 200,
            "/api/v1/interactions/timeline": 200,
            "/api/v1/interactions/INT-001": 200,
            # Evidence module
            "/api/v1/evidence/query": 200,
            "/api/v1/evidence/traceability?evidenceId=EV-001": 200,
            "/api/v1/evidence/EV-001": 200,
            # Knowledge module
            "/api/v1/knowledge/query": 200,
            "/api/v1/knowledge/documents/DOC-001": 200,
        }
        for endpoint, expected_status in reachable_endpoints.items():
            response = client.get(endpoint)
            assert response.status_code == expected_status, f"Expected {expected_status} for {endpoint}, got {response.status_code}"
