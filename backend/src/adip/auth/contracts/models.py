"""Auth & Authorization domain models.

Defines the core data contracts for the enterprise authentication
and authorisation platform including users, roles, permissions,
sessions, tokens, and security contexts.

All models are Pydantic v2 BaseModel subclasses with full type
annotations, validation, and documentation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.auth.enums import (
    AuthDomain,
    AuthenticationMethod,
    GroupType,
    OrganizationType,
    PermissionType,
    SessionStatus,
    TokenType,
    UserStatus,
)


class Permission(BaseModel):
    """A permission granting access to a specific resource or action.

    Permissions are the atomic unit of authorisation and can be
    assigned to roles, users, or groups.
    """

    permission_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique permission identifier",
    )
    resource: str = Field(
        default="",
        description="The resource or action this permission applies to",
    )
    permission_type: PermissionType = Field(
        default=PermissionType.READ,
        description="The type of permission (READ, WRITE, EXECUTE, etc.)",
    )
    description: str = Field(
        default="",
        description="Human-readable description of the permission",
    )
    domain: AuthDomain = Field(
        default=AuthDomain.SYSTEM,
        description="The domain this permission belongs to",
    )
    conditions: dict[str, Any] = Field(
        default_factory=dict,
        description="Conditional constraints for this permission",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional permission metadata",
    )


class Role(BaseModel):
    """A role defines a collection of permissions.

    Roles provide a logical grouping of permissions that can be
    assigned to users, groups, or service accounts.
    """

    role_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique role identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable role name",
    )
    description: str = Field(
        default="",
        description="Role description and intent",
    )
    permissions: list[Permission] = Field(
        default_factory=list,
        description="Permissions granted by this role",
    )
    parent_role_id: UUID4 | None = Field(
        default=None,
        description="Optional parent role for hierarchical inheritance",
    )
    domain: AuthDomain = Field(
        default=AuthDomain.SYSTEM,
        description="The domain this role belongs to",
    )
    is_system_role: bool = Field(
        default=False,
        description="Whether this is a system-defined role",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional role metadata",
    )


class Group(BaseModel):
    """A group of users or service accounts for organisational management.

    Groups enable bulk assignment of roles and permissions to
    multiple principals.
    """

    group_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique group identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable group name",
    )
    description: str = Field(
        default="",
        description="Group description",
    )
    group_type: GroupType = Field(
        default=GroupType.TEAM,
        description="The type of group",
    )
    member_ids: list[UUID4] = Field(
        default_factory=list,
        description="UUIDs of users or service accounts in this group",
    )
    role_ids: list[UUID4] = Field(
        default_factory=list,
        description="UUIDs of roles assigned to this group",
    )
    parent_group_id: UUID4 | None = Field(
        default=None,
        description="Optional parent group for hierarchy",
    )
    domain: AuthDomain = Field(
        default=AuthDomain.SYSTEM,
        description="The domain this group belongs to",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional group metadata",
    )


class Organization(BaseModel):
    """An organisation represents a tenant in the multi-tenant platform.

    Organisations provide top-level isolation for users, roles,
    permissions, groups, and authentication policies.
    """

    organization_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique organisation identifier",
    )
    name: str = Field(
        default="",
        description="Organisation name",
    )
    description: str = Field(
        default="",
        description="Organisation description",
    )
    org_type: OrganizationType = Field(
        default=OrganizationType.ENTERPRISE,
        description="The type of organisation",
    )
    domains: list[AuthDomain] = Field(
        default_factory=list,
        description="Domains this organisation has access to",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the organisation is active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional organisation metadata",
    )


class User(BaseModel):
    """A user represents a human operator in the ADIP platform.

    Users can authenticate, be assigned roles and permissions,
    and belong to groups and organisations.
    """

    user_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique user identifier",
    )
    username: str = Field(
        default="",
        description="Unique username for authentication",
    )
    email: str = Field(
        default="",
        description="User email address",
    )
    display_name: str = Field(
        default="",
        description="Human-readable display name",
    )
    status: UserStatus = Field(
        default=UserStatus.PENDING_ACTIVATION,
        description="Current user account status",
    )
    roles: list[UUID4] = Field(
        default_factory=list,
        description="UUIDs of roles assigned to this user",
    )
    groups: list[UUID4] = Field(
        default_factory=list,
        description="UUIDs of groups this user belongs to",
    )
    organization_id: UUID4 | None = Field(
        default=None,
        description="The organisation this user belongs to",
    )
    permissions: list[Permission] = Field(
        default_factory=list,
        description="Direct permissions assigned to this user",
    )
    domains: list[AuthDomain] = Field(
        default_factory=list,
        description="Domains this user has access to",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional user metadata",
    )


class ServiceAccount(BaseModel):
    """A service account represents a non-human principal.

    Service accounts are used for automated processes and
    service-to-service communication.
    """

    account_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique service account identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable service account name",
    )
    description: str = Field(
        default="",
        description="Service account description",
    )
    status: UserStatus = Field(
        default=UserStatus.ACTIVE,
        description="Current service account status",
    )
    roles: list[UUID4] = Field(
        default_factory=list,
        description="UUIDs of roles assigned to this service account",
    )
    organization_id: UUID4 | None = Field(
        default=None,
        description="The organisation this service account belongs to",
    )
    permissions: list[Permission] = Field(
        default_factory=list,
        description="Direct permissions assigned to this account",
    )
    domains: list[AuthDomain] = Field(
        default_factory=list,
        description="Domains this account has access to",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional service account metadata",
    )


class Token(BaseModel):
    """A token represents an authentication credential.

    Base model for all token types including JWT, refresh tokens,
    API keys, and service tokens.
    """

    token_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique token identifier",
    )
    token_type: TokenType = Field(
        description="The type of token",
    )
    principal_id: UUID4 = Field(
        description="The user or service account this token belongs to",
    )
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
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


class RefreshToken(BaseModel):
    """A refresh token used to obtain new access tokens.

    Refresh tokens have a longer lifetime than access tokens and
    can be rotated for security.
    """

    refresh_token_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique refresh token identifier",
    )
    token_id: UUID4 = Field(
        description="The access token this refresh token is associated with",
    )
    principal_id: UUID4 = Field(
        description="The user or service account this refresh token belongs to",
    )
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the refresh token was issued",
    )
    expires_at: datetime = Field(
        description="When the refresh token expires",
    )
    is_revoked: bool = Field(
        default=False,
        description="Whether the refresh token has been revoked",
    )
    rotation_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this refresh token has been rotated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional refresh token metadata",
    )


class ApiKey(BaseModel):
    """An API key for programmatic access to the platform.

    API keys provide a simple authentication mechanism for
    automated clients and integrations.
    """

    api_key_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique API key identifier",
    )
    key_prefix: str = Field(
        default="",
        description="Prefix of the API key for identification (not the full key)",
    )
    principal_id: UUID4 = Field(
        description="The user or service account this API key belongs to",
    )
    name: str = Field(
        default="",
        description="Human-readable name for this API key",
    )
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the API key was issued",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="When the API key expires (None = never)",
    )
    is_revoked: bool = Field(
        default=False,
        description="Whether the API key has been revoked",
    )
    last_used_at: datetime | None = Field(
        default=None,
        description="When the API key was last used",
    )
    permissions: list[Permission] = Field(
        default_factory=list,
        description="Permissions scoped to this API key",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional API key metadata",
    )


class Session(BaseModel):
    """An authentication session for a user or service account.

    Sessions track authenticated interactions with the platform
    and enforce session lifecycle policies.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    principal_id: UUID4 = Field(
        description="The user or service account this session belongs to",
    )
    principal_type: str = Field(
        default="user",
        description="Type of principal (user, service_account)",
    )
    status: SessionStatus = Field(
        default=SessionStatus.ACTIVE,
        description="Current session status",
    )
    token_id: UUID4 | None = Field(
        default=None,
        description="The current token associated with this session",
    )
    auth_method: AuthenticationMethod = Field(
        default=AuthenticationMethod.TOKEN,
        description="The method used to authenticate",
    )
    ip_address: str = Field(
        default="",
        description="IP address from which the session was created",
    )
    user_agent: str = Field(
        default="",
        description="User agent string from the client",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session was created",
    )
    last_activity_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session was last active",
    )
    expires_at: datetime = Field(
        description="When the session expires",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )


class SecurityContext(BaseModel):
    """Security context for an authenticated request.

    Carries identity, session, and token information through the
    request processing pipeline.
    """

    principal_id: UUID4 = Field(
        description="The authenticated user or service account ID",
    )
    principal_type: str = Field(
        default="user",
        description="Type of principal (user, service_account)",
    )
    session_id: UUID4 | None = Field(
        default=None,
        description="The session ID if applicable",
    )
    token_id: UUID4 | None = Field(
        default=None,
        description="The token ID used for authentication",
    )
    organization_id: UUID4 | None = Field(
        default=None,
        description="The organisation context",
    )
    roles: list[str] = Field(
        default_factory=list,
        description="Role names assigned to the principal",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Permission strings (resource:type) granted",
    )
    domains: list[AuthDomain] = Field(
        default_factory=list,
        description="Domains the principal has access to",
    )
    is_authenticated: bool = Field(
        default=False,
        description="Whether the principal is authenticated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional security context metadata",
    )


class AuthenticationContext(BaseModel):
    """Context for an authentication operation.

    Carries credentials, method, and metadata for authentication
    processing.
    """

    principal_id: UUID4 | None = Field(
        default=None,
        description="The principal attempting to authenticate",
    )
    method: AuthenticationMethod = Field(
        default=AuthenticationMethod.TOKEN,
        description="The authentication method being used",
    )
    credentials: dict[str, Any] = Field(
        default_factory=dict,
        description="Authentication credentials (never stored in logs)",
    )
    ip_address: str = Field(
        default="",
        description="IP address of the authentication request",
    )
    user_agent: str = Field(
        default="",
        description="User agent of the authentication request",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the authentication was attempted",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional authentication context metadata",
    )


class AuthorizationContext(BaseModel):
    """Context for an authorization check.

    Carries the principal, resource, action, and environment
    information for making authorization decisions.
    """

    principal_id: UUID4 = Field(
        description="The principal requesting access",
    )
    principal_type: str = Field(
        default="user",
        description="Type of principal (user, service_account)",
    )
    resource: str = Field(
        default="",
        description="The resource being accessed",
    )
    action: PermissionType = Field(
        default=PermissionType.READ,
        description="The action being performed",
    )
    domain: AuthDomain = Field(
        default=AuthDomain.SYSTEM,
        description="The domain context",
    )
    organization_id: UUID4 | None = Field(
        default=None,
        description="The organisation context",
    )
    environment: dict[str, Any] = Field(
        default_factory=dict,
        description="Environment attributes for context-aware authorization",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the authorization check was performed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional authorization context metadata",
    )


class AuthMetrics(BaseModel):
    """Metrics for the authentication and authorization system.

    Tracks key performance and usage indicators for auth operations.
    """

    authentications_total: int = Field(
        default=0,
        ge=0,
        description="Total number of authentication attempts",
    )
    authentications_success: int = Field(
        default=0,
        ge=0,
        description="Number of successful authentications",
    )
    authentications_failed: int = Field(
        default=0,
        ge=0,
        description="Number of failed authentications",
    )
    authorizations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of authorization checks",
    )
    authorizations_granted: int = Field(
        default=0,
        ge=0,
        description="Number of authorized requests",
    )
    authorizations_denied: int = Field(
        default=0,
        ge=0,
        description="Number of denied authorization requests",
    )
    tokens_issued: int = Field(
        default=0,
        ge=0,
        description="Total number of tokens issued",
    )
    tokens_revoked: int = Field(
        default=0,
        ge=0,
        description="Total number of tokens revoked",
    )
    sessions_active: int = Field(
        default=0,
        ge=0,
        description="Number of currently active sessions",
    )
    sessions_expired: int = Field(
        default=0,
        ge=0,
        description="Number of expired sessions",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metrics metadata",
    )


class AuthMetadata(BaseModel):
    """Metadata for an authentication or authorization operation.

    Provides standard enterprise metadata fields for tracing,
    auditing, and observability.
    """

    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    request_id: str = Field(
        default="",
        description="Unique request identifier",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the operation occurred",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Duration of the operation in milliseconds",
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
        description="Additional operation metadata",
    )
