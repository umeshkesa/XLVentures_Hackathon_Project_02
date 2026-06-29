"""Authentication context and permission-model types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adip.security.permissions import Permission
    from adip.security.roles import Role


@dataclass
class AuthenticatedUser:
    """Represents an authenticated actor and their effective permissions.

    This is the canonical "who is this person and what can they do" object
    that flows through the middleware stack and into endpoint dependencies.

    An empty ``sub`` with no roles/permissions is considered unauthenticated.
    For a dedicated marker type see :class:`AnonymousUser`.
    """

    sub: str = ""
    """Subject identifier — typically the user's UUID or email."""

    roles: list[Role] = field(default_factory=list)
    """Roles assigned to this user."""

    permissions: set[Permission] = field(default_factory=set)
    """Effective (resolved) permission set for the current request."""

    extra: dict[str, object] = field(default_factory=dict)
    """Arbitrary claims or metadata bag (tenant id, scopes, …)."""

    @property
    def is_authenticated(self) -> bool:
        return bool(self.sub)


class AnonymousUser(AuthenticatedUser):
    """Represents an unauthenticated actor with no permissions.

    This is a distinct subtype so that type-narrowing checks like
    ``isinstance(user, AnonymousUser)`` work at runtime.
    """

    @property
    def is_authenticated(self) -> bool:
        return False
