"""Enumerations for the Auth module.

Defines all enum types used across auth domain models, events,
interfaces, and DTOs.
"""

from __future__ import annotations

from enum import StrEnum


class TokenType(StrEnum):
    """Supported token types for the authentication platform.

    JWT — JSON Web Token for standard authentication.
    REFRESH_TOKEN — long-lived token for refreshing expired JWTs.
    API_KEY — API key for programmatic access.
    SERVICE_TOKEN — token for service-to-service communication.
    """

    JWT = "JWT"
    REFRESH_TOKEN = "REFRESH_TOKEN"
    API_KEY = "API_KEY"
    SERVICE_TOKEN = "SERVICE_TOKEN"


class SessionStatus(StrEnum):
    """Lifecycle status of an authentication session.

    ACTIVE — session is active and valid.
    EXPIRED — session has reached its maximum lifetime.
    REVOKED — session has been explicitly revoked.
    LOCKED — session has been locked due to security policy.
    """

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    LOCKED = "LOCKED"


class PermissionType(StrEnum):
    """Supported permission types for the authorization system.

    READ — read-only access to a resource.
    WRITE — write/modify access to a resource.
    EXECUTE — execute/run access to an operation.
    REVIEW — review/audit access to a resource.
    APPROVE — approve/authorise an operation.
    MANAGE — full management access (create, read, update, delete).
    """

    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    REVIEW = "REVIEW"
    APPROVE = "APPROVE"
    MANAGE = "MANAGE"


class AuthDomain(StrEnum):
    """Enterprise domains for the authentication platform.

    Values represent the ADIP platform domains that auth rules
    can be defined for.
    """

    SYSTEM = "SYSTEM"
    PLANNER = "PLANNER"
    WORKFLOW = "WORKFLOW"
    MEMORY = "MEMORY"
    KNOWLEDGE = "KNOWLEDGE"
    REASONING = "REASONING"
    EVIDENCE = "EVIDENCE"
    ACTION = "ACTION"
    ENERGY = "ENERGY"
    CUSTOMER = "CUSTOMER"
    PLUGIN = "PLUGIN"
    AUTH = "AUTH"
    API = "API"


class AuthenticationMethod(StrEnum):
    """Supported authentication methods.

    PASSWORD — username/password based authentication.
    TOKEN — token-based authentication (JWT, Bearer).
    API_KEY — API key based authentication.
    SERVICE_ACCOUNT — service account based authentication.
    MULTI_FACTOR — multi-factor authentication.
    """

    PASSWORD = "PASSWORD"
    TOKEN = "TOKEN"
    API_KEY = "API_KEY"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    MULTI_FACTOR = "MULTI_FACTOR"


class UserStatus(StrEnum):
    """Lifecycle status of a user account.

    ACTIVE — user account is active and can authenticate.
    INACTIVE — user account exists but is temporarily disabled.
    LOCKED — user account is locked due to security policy.
    SUSPENDED — user account is suspended pending review.
    DEACTIVATED — user account has been permanently deactivated.
    PENDING_ACTIVATION — user account has been created but not activated.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"


class GroupType(StrEnum):
    """Supported group types.

    DEPARTMENT — organisational department group.
    TEAM — project or functional team group.
    ROLE_BASED — group defined by role membership.
    PROJECT — project-based group.
    CUSTOM — user-defined custom group.
    """

    DEPARTMENT = "DEPARTMENT"
    TEAM = "TEAM"
    ROLE_BASED = "ROLE_BASED"
    PROJECT = "PROJECT"
    CUSTOM = "CUSTOM"


class OrganizationType(StrEnum):
    """Supported organisation types.

    ENTERPRISE — large-scale enterprise organisation.
    TEAM — small team or department organisation.
    INDIVIDUAL — individual user organisation.
    PARTNER — partner or vendor organisation.
    """

    ENTERPRISE = "ENTERPRISE"
    TEAM = "TEAM"
    INDIVIDUAL = "INDIVIDUAL"
    PARTNER = "PARTNER"
