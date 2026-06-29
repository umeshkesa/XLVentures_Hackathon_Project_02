"""Structured entity model — replaces simple entity strings."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import UUID4, BaseModel, Field


class DetectedEntity(BaseModel):
    """A named entity detected during goal analysis."""
    entity_id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str
    entity_type: str = "unknown"
    confidence: float = 0.0
    source: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
