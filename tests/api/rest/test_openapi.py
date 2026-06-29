"""Tests for OpenAPI configuration — Swagger, Redoc, OpenAPI schema."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestOpenAPIEndpoint:
    def test_openapi_json_endpoint(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["openapi"].startswith("3.")
        assert "info" in schema
        assert "paths" in schema
        assert "tags" in schema

    def test_openapi_info_title(self, app: FastAPI) -> None:
        schema = app.openapi()
        assert "ADIP REST API" in schema["info"]["title"]

    def test_openapi_info_version(self, app: FastAPI) -> None:
        schema = app.openapi()
        assert schema["info"]["version"] == "1.0.0"

    def test_openapi_tags_defined(self, app: FastAPI) -> None:
        schema = app.openapi()
        tag_names = {tag["name"] for tag in schema["tags"]}
        expected_tags = {
            "System",
            "Planner",
            "Workflow",
            "Memory",
            "Knowledge",
            "Rules",
            "Plugins",
            "Registry",
            "Evidence",
            "Reasoning",
            "Recommendation",
            "Explainability",
            "Decision Review",
            "Action Manager",
            "Action Engine",
            "Energy",
        }
        for tag in expected_tags:
            assert tag in tag_names, f"Expected tag '{tag}' not found in OpenAPI schema"

    def test_openapi_paths(self, app: FastAPI) -> None:
        schema = app.openapi()
        paths = schema["paths"]
        expected_paths = [
            "/api/v1/health",
            "/api/v1/ready",
            "/api/v1/live",
            "/api/v1/version",
        ]
        for path in expected_paths:
            assert path in paths, f"Expected path '{path}' not found in OpenAPI schema"

    def test_swagger_ui_endpoint(self, client: TestClient) -> None:
        response = client.get("/docs")
        assert response.status_code in (200, 302)

    def test_redoc_ui_endpoint(self, client: TestClient) -> None:
        response = client.get("/redoc")
        assert response.status_code in (200, 302)


class TestOpenAPISchemaContent:
    def test_system_health_endpoint_schema(self, app: FastAPI) -> None:
        schema = app.openapi()
        health_path = schema["paths"].get("/api/v1/health", {})
        assert "get" in health_path
        get_op = health_path["get"]
        assert "summary" in get_op
        assert "description" in get_op

    def test_all_tags_have_description(self, app: FastAPI) -> None:
        schema = app.openapi()
        for tag in schema["tags"]:
            assert "description" in tag, f"Tag '{tag['name']}' missing description"
