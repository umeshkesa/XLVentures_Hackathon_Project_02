"""System endpoint tests.

These tests exercise the REST API system_router (which supersedes the
legacy health_router).  The system_router returns richer response bodies
than the old health_router so we check for expected keys rather than full
equality.
"""

from fastapi.testclient import TestClient

from adip.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_version_endpoint() -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert "version" in response.json()

