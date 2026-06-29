"""Authentication, authorisation and RBAC foundation.

Use as::

    from adip.security import Role, Permission, AuthenticatedUser
    from adip.security.dependencies import require_authentication
"""

from adip.security.auth import AnonymousUser, AuthenticatedUser
from adip.security.permissions import Permission
from adip.security.roles import Role

__all__ = [
    "AnonymousUser",
    "AuthenticatedUser",
    "Permission",
    "Role",
]
