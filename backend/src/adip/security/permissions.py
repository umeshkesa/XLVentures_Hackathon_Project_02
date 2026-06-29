"""Granular permission identifiers for role-based access control.

Permissions use a ``resource:action`` naming convention that maps naturally
to string claims in a JWT access token.
"""

from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    """Every discrete action a user may (or may not) be allowed to perform."""

    # ── User management ──────────────────────────────────────────────
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # ── Role management ──────────────────────────────────────────────
    ROLE_CREATE = "role:create"
    ROLE_READ = "role:read"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"

    # ── Reports ──────────────────────────────────────────────────────
    REPORT_CREATE = "report:create"
    REPORT_READ = "report:read"
    REPORT_UPDATE = "report:update"
    REPORT_DELETE = "report:delete"

    # ── Application settings ─────────────────────────────────────────
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"

    # ── System / cluster administration ──────────────────────────────
    SYSTEM_READ = "system:read"
    SYSTEM_UPDATE = "system:update"
