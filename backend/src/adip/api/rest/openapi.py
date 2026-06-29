"""OpenAPI / Swagger / Redoc configuration."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_openapi(application: FastAPI) -> None:
    title = "ADIP REST API"
    version = "1.0.0"
    description = (
        "Agentic Decision Intelligence Platform — REST API Layer.\n\n"
        "Exposes all platform capabilities through versioned HTTP endpoints. "
        "This layer contains no business logic; it acts only as a transport "
        "layer between clients and platform services."
    )

    def custom_openapi() -> dict:
        if application.openapi_schema:
            return application.openapi_schema

        openapi_schema = get_openapi(
            title=title,
            version=version,
            description=description,
            routes=application.routes,
        )

        openapi_schema["info"]["x-logo"] = {
            "url": "https://adip.ai/logo.png",
            "altText": "ADIP Platform",
        }

        openapi_schema["tags"] = [
            {"name": "System", "description": "Health checks and system information"},
            {"name": "Planner", "description": "Planning and goal management"},
            {"name": "Workflow", "description": "Workflow orchestration"},
            {"name": "Memory", "description": "Memory management"},
            {"name": "Knowledge", "description": "Knowledge management"},
            {"name": "Rules", "description": "Rule management and evaluation"},
            {"name": "Plugins", "description": "Plugin lifecycle management"},
            {"name": "Registry", "description": "Service and component registry"},
            {"name": "Evidence", "description": "Evidence fusion and management"},
            {"name": "Reasoning", "description": "Reasoning engine"},
            {"name": "Recommendation", "description": "Recommendation engine"},
            {"name": "Explainability", "description": "Explainability engine"},
            {"name": "Interactions", "description": "Customer interaction management"},
            {"name": "Decision Review", "description": "Decision review layer"},
            {"name": "Action Manager", "description": "Action planning and management"},
            {"name": "Action Engine", "description": "Action execution engine"},
            {"name": "Energy", "description": "Energy domain operations"},
        ]

        application.openapi_schema = openapi_schema
        return application.openapi_schema

    application.openapi = custom_openapi
