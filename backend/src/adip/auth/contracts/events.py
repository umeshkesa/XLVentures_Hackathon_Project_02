"""Auth & Authorization event models.

Events follow the standard ADIP eventing contract with a base
AuthEvent and concrete event types for each auth operation. All
events carry enterprise fields (event_id, timestamp, correlation_id,
payload) for tracing and audit.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.auth.enums import AuthDomain, AuthenticationMethod, PermissionType

EventVersion: str = "1.0.0"


class AuthEvent(BaseModel):
    """Base event for all auth operations.

    Provides standard enterprise event fields shared by every
    concrete auth event.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    principal_id: UUID4 = Field(
        description="The principal this event relates to",
    )
    domain: AuthDomain = Field(
        default=AuthDomain.AUTH,
        description="The auth domain",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event was emitted",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary event payload data",
    )


class UserAuthenticated(AuthEvent):
    """Emitted when a user successfully authenticates."""

    method: AuthenticationMethod = Field(
        default=AuthenticationMethod.TOKEN,
        description="The method used for authentication",
    )
    session_id: UUID4 | None = Field(
        default=None,
        description="The session created for this authentication",
    )


class UserLoggedOut(AuthEvent):
    """Emitted when a user logs out of the platform."""

    session_id: UUID4 = Field(
        description="The session that was terminated",
    )
    reason: str = Field(
        default="user_initiated",
        description="Reason for logout",
    )


class TokenIssued(AuthEvent):
    """Emitted when a new token is issued."""

    token_id: UUID4 = Field(
        description="The token that was issued",
    )
    token_type: str = Field(
        default="",
        description="The type of token issued",
    )
    expires_at: datetime = Field(
        description="When the token expires",
    )


class TokenRefreshed(AuthEvent):
    """Emitted when an access token is refreshed."""

    old_token_id: UUID4 = Field(
        description="The previous token that was refreshed",
    )
    new_token_id: UUID4 = Field(
        description="The new token issued after refresh",
    )


class PermissionChecked(AuthEvent):
    """Emitted when a permission check is performed."""

    resource: str = Field(
        default="",
        description="The resource being checked",
    )
    action: PermissionType = Field(
        default=PermissionType.READ,
        description="The action being checked",
    )
    granted: bool = Field(
        default=False,
        description="Whether the permission was granted",
    )


class AccessDenied(AuthEvent):
    """Emitted when an access request is denied."""

    resource: str = Field(
        default="",
        description="The resource that was denied",
    )
    action: PermissionType = Field(
        default=PermissionType.READ,
        description="The action that was denied",
    )
    reason: str = Field(
        default="",
        description="Reason for the access denial",
    )
