"""Role-to-permission resolution.

The :class:`Role` enum itself lives in :mod:`adip.core.constants`; this
module only provides the logic that maps each role to its effective set
of granular permissions.
"""

from __future__ import annotations

from adip.core.constants import Role
from adip.security.permissions import Permission


def resolve_permissions(role: Role) -> set[Permission]:
    """Return the full set of permissions granted to *role*."""

    if role == Role.SUPER_ADMIN:
        return {
            Permission.USER_CREATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.USER_DELETE,
            Permission.ROLE_CREATE,
            Permission.ROLE_READ,
            Permission.ROLE_UPDATE,
            Permission.ROLE_DELETE,
            Permission.REPORT_CREATE,
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            Permission.REPORT_DELETE,
            Permission.SETTINGS_READ,
            Permission.SETTINGS_UPDATE,
            Permission.SYSTEM_READ,
            Permission.SYSTEM_UPDATE,
        }

    if role == Role.ADMIN:
        return {
            Permission.USER_CREATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.ROLE_READ,
            Permission.REPORT_CREATE,
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            Permission.REPORT_DELETE,
            Permission.SETTINGS_READ,
            Permission.SETTINGS_UPDATE,
            Permission.SYSTEM_READ,
        }

    if role == Role.OPERATOR:
        return {
            Permission.USER_READ,
            Permission.ROLE_READ,
            Permission.REPORT_CREATE,
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            Permission.SETTINGS_READ,
            Permission.SYSTEM_READ,
        }

    if role == Role.ANALYST:
        return {
            Permission.REPORT_CREATE,
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            Permission.SYSTEM_READ,
        }

    if role == Role.REVIEWER:
        return {
            Permission.REPORT_READ,
            Permission.REPORT_UPDATE,
            Permission.SYSTEM_READ,
        }

    return set()
