"""Auth & Authorization Data Transfer Objects (DTOs).

DTOs provide stable, versioned contracts for external API consumers.
They decouple the public API surface from internal domain models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.auth.enums import AuthDomain, AuthenticationMethod, PermissionType


class LoginRequestDTO(BaseModel):
    """DTO for login/authentication requests.

    Provides a clean API contract for authentication that is
    independent of the internal AuthenticationContext model.
    """

    username: str = Field(
        default="",
        description="Username or email for authentication",
    )
    password: str = Field(
        default="",
        description="Password credential (never logged)",
    )
    method: AuthenticationMethod = Field(
        default=AuthenticationMethod.PASSWORD,
        description="The authentication method to use",
    )
    organization_id: UUID4 | None = Field(
        default=None,
        description="Optional organisation context",
    )
    ip_address: str = Field(
        default="",
        description="IP address of the requesting client",
    )
    user_agent: str = Field(
        default="",
        description="User agent of the requesting client",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional login metadata",
    )


class LoginResponseDTO(BaseModel):
    """DTO for login/authentication responses.

    Provides a stable API response contract for authentication
    results.
    """

    success: bool = Field(
        default=False,
        description="Whether authentication was successful",
    )
    session_id: UUID4 | None = Field(
        default=None,
        description="The session ID if authentication succeeded",
    )
    token_id: UUID4 | None = Field(
        default=None,
        description="The token ID if authentication succeeded",
    )
    principal_id: UUID4 | None = Field(
        default=None,
        description="The authenticated principal ID",
    )
    message: str = Field(
        default="",
        description="Human-readable response message",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata",
    )


class TokenDTO(BaseModel):
    """DTO for token operations.

    Provides a clean API contract for token issuance and
    refresh operations.
    """

    token_id: UUID4 = Field(
        description="Unique token identifier",
    )
    token_type: str = Field(
        default="",
        description="The type of token (JWT, API_KEY, SERVICE_TOKEN)",
    )
    principal_id: UUID4 = Field(
        description="The principal the token belongs to",
    )
    issued_at: datetime = Field(
        description="When the token was issued",
    )
    expires_at: datetime = Field(
        description="When the token expires",
    )
    is_revoked: bool = Field(
        default=False,
        description="Whether the token has been revoked",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional token metadata",
    )


class PermissionDTO(BaseModel):
    """DTO for permission operations.

    Provides a clean API contract for permission checks and
    assignments.
    """

    permission_id: UUID4 = Field(
        description="Unique permission identifier",
    )
    resource: str = Field(
        default="",
        description="The resource or action this permission applies to",
    )
    permission_type: PermissionType = Field(
        default=PermissionType.READ,
        description="The type of permission",
    )
    domain: AuthDomain = Field(
        default=AuthDomain.SYSTEM,
        description="The domain this permission belongs to",
    )
    granted: bool = Field(
        default=True,
        description="Whether the permission is granted",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional permission metadata",
    )
