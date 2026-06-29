"""Authentication service: login, token management, user resolution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import jwt as pyjwt

from adip.core.exceptions import AuthenticationException
from adip.security.auth import AuthenticatedUser
from adip.security.jwt import create_access_token, create_refresh_token, decode_token
from adip.security.password import verify_password
from adip.security.roles import resolve_permissions

if TYPE_CHECKING:
    from adip.models.user import User

_UserLoader = Callable[[str], "User | None"]


@dataclass
class TokenResponse:
    """Returned on successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    """High-level authentication operations.

    This service depends on a **callable** that returns a ``User``
    (or ``None``) from an email address — typically the
    :class:`UserRepository.find_by_email` method.
    """

    def __init__(self, user_loader: _UserLoader) -> None:
        self._user_loader = user_loader

    async def authenticate(self, email: str, password: str) -> TokenResponse:
        """Validate credentials and return a token pair.

        Raises :class:`AuthenticationException` on failure.
        """
        user = await self._user_loader(email)
        if user is None:
            raise AuthenticationException("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationException("Account is inactive.")
        if not verify_password(password, user.hashed_password):
            raise AuthenticationException("Invalid email or password.")

        auth_user = _build_authenticated_user(user)
        return TokenResponse(
            access_token=create_access_token(auth_user),
            refresh_token=create_refresh_token(auth_user),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token from a valid refresh token.

        Raises :class:`AuthenticationException` on failure.
        """
        try:
            payload = decode_token(refresh_token)
        except pyjwt.PyJWTError as exc:
            raise AuthenticationException("Invalid or expired refresh token.") from exc

        if payload.token_type != "refresh":
            raise AuthenticationException("Token is not a refresh token.")

        user = await self._user_loader(payload.sub)
        if user is None:
            raise AuthenticationException("User not found.")
        if not user.is_active:
            raise AuthenticationException("Account is inactive.")

        auth_user = _build_authenticated_user(user)
        return TokenResponse(
            access_token=create_access_token(auth_user),
            refresh_token=refresh_token,
        )

    async def get_current_user(self, token: str) -> AuthenticatedUser:
        """Decode an access token and return the authenticated user context.

        Raises :class:`AuthenticationException` on failure.
        """
        try:
            payload = decode_token(token)
        except pyjwt.PyJWTError as exc:
            raise AuthenticationException("Invalid or expired token.") from exc

        if payload.token_type != "access":
            raise AuthenticationException("Token is not an access token.")

        user = await self._user_loader(payload.sub)
        if user is None:
            raise AuthenticationException("User not found.")
        if not user.is_active:
            raise AuthenticationException("Account is inactive.")

        return AuthenticatedUser(
            sub=str(user.id),
            roles=[user.role],
            permissions=resolve_permissions(user.role),
        )


# ── Internal helpers ─────────────────────────────────────────────────────


def _build_authenticated_user(user: User) -> AuthenticatedUser:
    return AuthenticatedUser(
        sub=str(user.id),
        roles=[user.role],
        permissions=resolve_permissions(user.role),
    )
