"""FastAPI dependency-injection helpers for authentication and authorisation.

Usage::

    from adip.security.dependencies import (
        require_authentication, require_permissions, require_role, optional_authentication,
    )
    from adip.security.permissions import Permission
    from adip.core.constants import Role
    from fastapi import Depends

    @router.get("/reports")
    async def list_reports(
        user: AuthenticatedUser = Depends(require_authentication),
    ):
        ...

    @router.post("/reports")
    async def create_report(
        user: AuthenticatedUser = Depends(
            require_permissions(Permission.REPORT_CREATE)
        ),
    ):
        ...

    @router.delete("/reports")
    async def delete_report(
        user: AuthenticatedUser = Depends(require_role(Role.ADMIN)),
    ):
        ...
"""

from __future__ import annotations

from collections.abc import Set as AbstractSet

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from adip.core.constants import Role as RoleEnum
from adip.core.exceptions import AuthenticationException, AuthorizationException
from adip.security.auth import AnonymousUser, AuthenticatedUser
from adip.security.jwt import decode_token, token_from_header
from adip.security.permissions import Permission
from adip.security.roles import resolve_permissions

# Re-usable scheme so that /docs shows a padlock button.
_bearer = HTTPBearer(auto_error=False)


async def require_authentication(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),  # noqa: B008
) -> AuthenticatedUser:
    """Resolve and return the current authenticated user.

    Raises :class:`AuthenticationException` (401) when no valid token
    is provided.  Parses the Bearer token and builds an
    :class:`AuthenticatedUser` from the JWT claims.
    """
    if credentials is None:
        raise AuthenticationException("Authentication is required.")

    token_str = token_from_header(f"Bearer {credentials.credentials}")
    if token_str is None:
        raise AuthenticationException("Invalid authorization header.")

    try:
        payload = decode_token(token_str)
    except Exception as exc:
        raise AuthenticationException("Invalid or expired token.") from exc

    if payload.token_type != "access":
        raise AuthenticationException("Token is not an access token.")

    roles = [RoleEnum(r) for r in payload.roles]
    permissions = {
        Permission(p) for p in payload.permissions
    } if payload.permissions else set()

    if not permissions:
        for role in roles:
            permissions |= resolve_permissions(role)

    return AuthenticatedUser(
        sub=payload.sub,
        roles=roles,
        permissions=permissions,
        extra=payload.extra,
    )


async def require_role(role: RoleEnum) -> AuthenticatedUser:
    """Return a dependency callable that requires a specific role.

    The returned dependency first authenticates the user then checks
    that at least one of the user's roles matches *role*.

    Raises :class:`AuthorizationException` (403) on mismatch.
    """

    async def _dependency(
        user: AuthenticatedUser = Depends(require_authentication),  # noqa: B008
    ) -> AuthenticatedUser:
        if role not in user.roles:
            raise AuthorizationException(
                f"Required role '{role.value}' not assigned."
            )
        return user

    return _dependency


async def require_permissions(
    *permissions: Permission,
) -> AuthenticatedUser:
    """Return a dependency callable that requires *all* given permissions.

    The returned dependency first authenticates the user (via
    :func:`require_authentication`) then verifies that each requested
    permission is present in the user's resolved permission set.

    Raises :class:`AuthorizationException` (403) if any permission is missing.
    """

    async def _dependency(
        user: AuthenticatedUser = Depends(require_authentication),  # noqa: B008
    ) -> AuthenticatedUser:
        missing = _missing_permissions(user.permissions, permissions)
        if missing:
            raise AuthorizationException(
                f"Missing required permissions: {', '.join(sorted(missing))}"
            )
        return user

    return _dependency


async def optional_authentication(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),  # noqa: B008
) -> AuthenticatedUser:
    """Return the current user or an :class:`AnonymousUser` if no token is sent.

    Never raises — useful for public endpoints that optionally customise
    behaviour based on the caller's identity.
    """
    if credentials is None:
        return AnonymousUser()
    try:
        return await require_authentication(credentials=credentials)
    except (AuthenticationException, AuthorizationException):
        return AnonymousUser()


# ── Internal helpers ─────────────────────────────────────────────────────


def _missing_permissions(
    have: AbstractSet[Permission],
    need: tuple[Permission, ...],
) -> list[str]:
    return [p.value for p in need if p not in have]
