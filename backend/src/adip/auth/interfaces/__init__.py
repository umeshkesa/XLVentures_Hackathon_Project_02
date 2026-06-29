"""Abstract interfaces for the Auth & Authorization module.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

Architecture:
    AuthService  →  AuthManager  →  AuthCoordinator
                                        ├── AuthenticationProvider
                                        ├── AuthorizationProvider
                                        ├── TokenProvider
                                        ├── SessionProvider
                                        └── PermissionProvider

AuthService is the enterprise facade for external callers.
AuthManager is the internal orchestrator.
AuthCoordinator coordinates all sub-components.
"""

from __future__ import annotations

import abc

from adip.auth.contracts.models import (
    AuthenticationContext,
    AuthMetadata,
    AuthMetrics,
    AuthorizationContext,
    Permission,
    Role,
    SecurityContext,
    Session,
    Token,
    User,
)
from adip.auth.enums import (
    AuthDomain,
    AuthenticationMethod,
    PermissionType,
    SessionStatus,
    TokenType,
)


class AuthService(abc.ABC):
    """Enterprise facade for authentication & authorization operations.

    Provides validation, authorisation, audit, and observability
    wrapping around the AuthManager. External modules interact
    with this facade rather than with AuthManager directly.
    """

    @abc.abstractmethod
    async def authenticate(self, context: AuthenticationContext) -> SecurityContext:
        """Authenticate a principal and return a security context."""
        ...

    @abc.abstractmethod
    async def authorize(self, context: AuthorizationContext) -> bool:
        """Check whether a principal is authorised for an action."""
        ...

    @abc.abstractmethod
    async def create_session(self, principal_id: str) -> Session:
        """Create a new authentication session."""
        ...

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        """Retrieve a session by its identifier."""
        ...

    @abc.abstractmethod
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke an active session."""
        ...

    @abc.abstractmethod
    async def issue_token(
        self,
        principal_id: str,
        token_type: TokenType = TokenType.JWT,
    ) -> Token:
        """Issue a new token for a principal."""
        ...

    @abc.abstractmethod
    async def revoke_token(self, token_id: str) -> bool:
        """Revoke an issued token."""
        ...

    @abc.abstractmethod
    async def check_permission(
        self,
        principal_id: str,
        resource: str,
        action: PermissionType,
        domain: AuthDomain = AuthDomain.SYSTEM,
    ) -> bool:
        """Check whether a principal has a specific permission."""
        ...

    @abc.abstractmethod
    async def get_user(self, user_id: str) -> User | None:
        """Retrieve a user by their identifier."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> AuthMetrics:
        """Retrieve auth system metrics."""
        ...


class AuthManager(abc.ABC):
    """Internal orchestrator for auth operations.

    Coordinates the AuthCoordinator and enforces platform policies
    before delegating to the coordinator.
    """

    @abc.abstractmethod
    async def authenticate(self, context: AuthenticationContext) -> SecurityContext:
        """Authenticate a principal and return a security context."""
        ...

    @abc.abstractmethod
    async def authorize(self, context: AuthorizationContext) -> bool:
        """Check whether a principal is authorised for an action."""
        ...

    @abc.abstractmethod
    async def create_session(self, principal_id: str, auth_method: AuthenticationMethod) -> Session:
        """Create a new authentication session."""
        ...

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        """Retrieve a session by its identifier."""
        ...

    @abc.abstractmethod
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke an active session."""
        ...

    @abc.abstractmethod
    async def issue_token(
        self,
        principal_id: str,
        token_type: TokenType,
    ) -> Token:
        """Issue a new token for a principal."""
        ...

    @abc.abstractmethod
    async def revoke_token(self, token_id: str) -> bool:
        """Revoke an issued token."""
        ...

    @abc.abstractmethod
    async def check_permission(
        self,
        principal_id: str,
        resource: str,
        action: PermissionType,
        domain: AuthDomain,
    ) -> bool:
        """Check whether a principal has a specific permission."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> AuthMetrics:
        """Retrieve auth system metrics."""
        ...


class AuthCoordinator(abc.ABC):
    """Coordinates all auth sub-components.

    Delegates to AuthenticationProvider, AuthorizationProvider,
    TokenProvider, SessionProvider, and PermissionProvider.
    """

    @abc.abstractmethod
    async def authenticate(self, context: AuthenticationContext) -> SecurityContext:
        """Coordinate authentication across providers."""
        ...

    @abc.abstractmethod
    async def authorize(self, context: AuthorizationContext) -> bool:
        """Coordinate authorization checks."""
        ...

    @abc.abstractmethod
    async def create_session(self, principal_id: str, auth_method: AuthenticationMethod) -> Session:
        """Coordinate session creation."""
        ...

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        """Retrieve a session."""
        ...

    @abc.abstractmethod
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a session."""
        ...

    @abc.abstractmethod
    async def issue_token(
        self,
        principal_id: str,
        token_type: TokenType,
    ) -> Token:
        """Coordinate token issuance."""
        ...

    @abc.abstractmethod
    async def revoke_token(self, token_id: str) -> bool:
        """Revoke a token."""
        ...

    @abc.abstractmethod
    async def check_permission(
        self,
        principal_id: str,
        resource: str,
        action: PermissionType,
        domain: AuthDomain,
    ) -> bool:
        """Coordinate permission checking."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> AuthMetrics:
        """Retrieve aggregated metrics from all providers."""
        ...


class AuthenticationProvider(abc.ABC):
    """Abstract provider for authentication logic.

    Implementations handle credential validation, MFA challenges,
    and identity verification.
    """

    @abc.abstractmethod
    async def authenticate(self, context: AuthenticationContext) -> SecurityContext:
        """Validate credentials and return a security context."""
        ...

    @abc.abstractmethod
    async def validate_credentials(self, credentials: dict) -> bool:
        """Validate raw credentials."""
        ...

    @abc.abstractmethod
    async def get_provider_name(self) -> str:
        """Return the name of this authentication provider."""
        ...


class AuthorizationProvider(abc.ABC):
    """Abstract provider for authorization logic.

    Implementations handle policy evaluation, role-based access
    control, and attribute-based access control.
    """

    @abc.abstractmethod
    async def is_authorized(self, context: AuthorizationContext) -> bool:
        """Determine whether a request is authorised."""
        ...

    @abc.abstractmethod
    async def get_effective_permissions(
        self,
        principal_id: str,
        domain: AuthDomain,
    ) -> list[str]:
        """Return all effective permission strings for a principal."""
        ...


class TokenProvider(abc.ABC):
    """Abstract provider for token management.

    Implementations handle token creation, validation, and
    lifecycle management for all token types.
    """

    @abc.abstractmethod
    async def issue_token(
        self,
        principal_id: str,
        token_type: TokenType,
    ) -> Token:
        """Issue a new token."""
        ...

    @abc.abstractmethod
    async def validate_token(self, token_id: str) -> bool:
        """Check whether a token is still valid."""
        ...

    @abc.abstractmethod
    async def revoke_token(self, token_id: str) -> bool:
        """Revoke an existing token."""
        ...

    @abc.abstractmethod
    async def get_token(self, token_id: str) -> Token | None:
        """Retrieve a token by its identifier."""
        ...


class SessionProvider(abc.ABC):
    """Abstract provider for session management.

    Implementations handle session creation, validation, and
    lifecycle management.
    """

    @abc.abstractmethod
    async def create_session(
        self,
        principal_id: str,
        auth_method: AuthenticationMethod,
    ) -> Session:
        """Create a new authentication session."""
        ...

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        """Retrieve a session by its identifier."""
        ...

    @abc.abstractmethod
    async def update_session_status(
        self,
        session_id: str,
        status: SessionStatus,
    ) -> bool:
        """Update the status of a session."""
        ...

    @abc.abstractmethod
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke an active session."""
        ...


class PermissionProvider(abc.ABC):
    """Abstract provider for permission management.

    Implementations handle permission definitions, role-permission
    mappings, and user-role assignments.
    """

    @abc.abstractmethod
    async def get_permissions(
        self,
        principal_id: str,
        domain: AuthDomain = AuthDomain.SYSTEM,
    ) -> list[Permission]:
        """Retrieve all permissions for a principal."""
        ...

    @abc.abstractmethod
    async def check_permission(
        self,
        principal_id: str,
        resource: str,
        action: PermissionType,
        domain: AuthDomain,
    ) -> bool:
        """Check whether a principal has a specific permission."""
        ...

    @abc.abstractmethod
    async def assign_role(self, principal_id: str, role_id: str) -> bool:
        """Assign a role to a principal."""
        ...

    @abc.abstractmethod
    async def revoke_role(self, principal_id: str, role_id: str) -> bool:
        """Revoke a role from a principal."""
        ...
