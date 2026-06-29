"""JWT encoding and decoding backed by PyJWT.

Requires ``PyJWT`` (already declared in project dependencies).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from adip.config.settings import get_settings
from adip.security.auth import AuthenticatedUser


@dataclass
class TokenPayload:
    """Decoded, validated contents of a JWT."""

    sub: str
    """Subject — user identifier."""

    exp: datetime
    """Expiration timestamp (UTC)."""

    iat: datetime
    """Issued-at timestamp (UTC)."""

    token_type: str = "access"
    """Token type (``access`` or ``refresh``)."""

    roles: list[str] = field(default_factory=list)
    """Role names carried in the token."""

    permissions: list[str] = field(default_factory=list)
    """Permission strings carried in the token."""

    extra: dict[str, Any] = field(default_factory=dict)
    """All other claims not explicitly parsed."""


def _get_secret() -> str:
    return get_settings().security.secret_key.get_secret_value()


def _get_algorithm() -> str:
    return get_settings().security.algorithm


def create_access_token(
    user: AuthenticatedUser,
    *,
    expires_in: timedelta | None = None,
    **extra_claims: Any,
) -> str:
    """Produce a signed JWT access token for *user*."""
    settings = get_settings().security
    if expires_in is None:
        expires_in = timedelta(minutes=settings.access_token_expire_minutes)
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": user.sub,
        "exp": now + expires_in,
        "iat": now,
        "token_type": "access",
        "roles": [r.value for r in user.roles],
        "permissions": [p.value for p in user.permissions],
    }
    payload.update(extra_claims)
    return jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())


def create_refresh_token(
    user: AuthenticatedUser,
    *,
    expires_in: timedelta | None = None,
    **extra_claims: Any,
) -> str:
    """Produce a signed JWT refresh token for *user*."""
    settings = get_settings().security
    if expires_in is None:
        expires_in = timedelta(days=settings.refresh_token_expire_days)
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": user.sub,
        "exp": now + expires_in,
        "iat": now,
        "token_type": "refresh",
        "roles": [r.value for r in user.roles],
        "permissions": [],
    }
    payload.update(extra_claims)
    return jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())


_TOKEN_KEYS = frozenset({"sub", "exp", "iat", "token_type", "roles", "permissions"})


def decode_token(token: str) -> TokenPayload:
    """Decode and validate *token*, returning the parsed payload.

    Raises
    ------
    jwt.PyJWTError
        If the token is expired, malformed, or has an invalid signature.
    """
    settings = get_settings().security
    data = jwt.decode(
        token,
        _get_secret(),
        algorithms=[settings.algorithm],
        options={"require": ["sub", "exp", "iat"]},
    )
    return TokenPayload(
        sub=data["sub"],
        exp=datetime.fromtimestamp(data["exp"], tz=UTC),
        iat=datetime.fromtimestamp(data["iat"], tz=UTC),
        token_type=data.get("token_type", "access"),
        roles=data.get("roles", []),
        permissions=data.get("permissions", []),
        extra={k: v for k, v in data.items() if k not in _TOKEN_KEYS},
    )


def token_from_header(header: str | None) -> str | None:
    """Extract a Bearer token from an ``Authorization`` header value."""
    if not header:
        return None
    scheme, _, token = header.partition(" ")
    return token if scheme.lower() == "bearer" else None
