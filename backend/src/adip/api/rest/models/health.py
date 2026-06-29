"""Health endpoint response models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from adip import __version__


class HealthResponse(BaseModel):
    status: str = Field(default="healthy")
    version: str = Field(default=__version__)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    uptime_seconds: float | None = Field(default=None)
    checks: dict[str, Any] | None = Field(default=None)


class ReadyResponse(BaseModel):
    ready: bool = Field(default=True)
    version: str = Field(default=__version__)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dependencies: dict[str, bool] | None = Field(default=None)


class LiveResponse(BaseModel):
    alive: bool = Field(default=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VersionResponse(BaseModel):
    version: str = Field(default=__version__)
    build: str | None = Field(default=None)
    commit: str | None = Field(default=None)
