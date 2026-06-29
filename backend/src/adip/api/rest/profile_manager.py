"""API Profile Manager — controls response detail level per profile."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ProfileType(StrEnum):
    SUMMARY = "summary"
    DETAILED = "detailed"
    AUDIT = "audit"
    DEBUG = "debug"


class APIProfileManager:
    """Manages API response profiles controlling detail level.

    Supports four profiles:
    - ``summary``: minimal response data, no metadata
    - ``detailed``: full response data with metadata
    - ``audit``: full response with audit trail information
    - ``debug``: full response with debug information, stack traces
    """

    def __init__(self, default_profile: ProfileType = ProfileType.DETAILED) -> None:
        self._default_profile = default_profile
        self._profiles: dict[str, dict[str, Any]] = {
            ProfileType.SUMMARY.value: {
                "include_metadata": False,
                "include_debug": False,
                "include_audit": False,
                "max_detail_depth": 1,
            },
            ProfileType.DETAILED.value: {
                "include_metadata": True,
                "include_debug": False,
                "include_audit": False,
                "max_detail_depth": 5,
            },
            ProfileType.AUDIT.value: {
                "include_metadata": True,
                "include_debug": False,
                "include_audit": True,
                "max_detail_depth": 10,
            },
            ProfileType.DEBUG.value: {
                "include_metadata": True,
                "include_debug": True,
                "include_audit": True,
                "max_detail_depth": 100,
            },
        }

    def get_profile(self, profile_name: str | None = None) -> dict[str, Any]:
        if profile_name is None:
            profile_name = self._default_profile.value
        profile = self._profiles.get(profile_name)
        if profile is None:
            logger.warning("profile.not_found", profile=profile_name, fallback=self._default_profile.value)
            profile = self._profiles[self._default_profile.value]
        return dict(profile)

    def set_default_profile(self, profile: ProfileType) -> None:
        self._default_profile = profile

    def apply_profile(self, data: Any, profile_name: str | None = None) -> Any:
        profile = self.get_profile(profile_name)
        if not profile["include_metadata"] and isinstance(data, dict):
            data = {k: v for k, v in data.items() if k != "metadata"}
        return data

    def list_profiles(self) -> list[str]:
        return list(self._profiles.keys())

    def get_profile_names(self) -> list[str]:
        return list(self._profiles.keys())
