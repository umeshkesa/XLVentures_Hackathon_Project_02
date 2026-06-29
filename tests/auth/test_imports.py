"""Tests for Auth module imports.

Verifies that all public API components are importable from their
expected locations.
"""

from __future__ import annotations


class TestImports:
    def test_import_enums(self) -> None:
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
        assert AuthDomain
        assert AuthenticationMethod
        assert GroupType
        assert OrganizationType
        assert PermissionType
        assert SessionStatus
        assert TokenType
        assert UserStatus

    def test_import_models(self) -> None:
        from adip.auth.contracts.models import (
            ApiKey,
            AuthenticationContext,
            AuthMetadata,
            AuthMetrics,
            AuthorizationContext,
            Group,
            Organization,
            Permission,
            RefreshToken,
            Role,
            SecurityContext,
            ServiceAccount,
            Session,
            Token,
            User,
        )
        assert User
        assert Role
        assert Permission
        assert Group
        assert Organization
        assert ServiceAccount
        assert Session
        assert Token
        assert RefreshToken
        assert ApiKey
        assert SecurityContext
        assert AuthenticationContext
        assert AuthorizationContext
        assert AuthMetadata
        assert AuthMetrics

    def test_import_events(self) -> None:
        from adip.auth.contracts.events import (
            AccessDenied,
            AuthEvent,
            EventVersion,
            PermissionChecked,
            TokenIssued,
            TokenRefreshed,
            UserAuthenticated,
            UserLoggedOut,
        )
        assert AuthEvent
        assert UserAuthenticated
        assert UserLoggedOut
        assert TokenIssued
        assert TokenRefreshed
        assert PermissionChecked
        assert AccessDenied
        assert EventVersion

    def test_import_exceptions(self) -> None:
        from adip.auth.contracts.exceptions import (
            AuthenticationException,
            AuthException,
            AuthorizationException,
            SessionException,
            TokenException,
        )
        assert AuthException
        assert AuthenticationException
        assert AuthorizationException
        assert TokenException
        assert SessionException

    def test_import_interfaces(self) -> None:
        from adip.auth.interfaces import (
            AuthCoordinator,
            AuthenticationProvider,
            AuthManager,
            AuthorizationProvider,
            AuthService,
            PermissionProvider,
            SessionProvider,
            TokenProvider,
        )
        assert AuthService
        assert AuthManager
        assert AuthCoordinator
        assert AuthenticationProvider
        assert AuthorizationProvider
        assert TokenProvider
        assert SessionProvider
        assert PermissionProvider

    def test_import_dtos(self) -> None:
        from adip.auth.dtos import LoginRequestDTO, LoginResponseDTO, PermissionDTO, TokenDTO
        assert LoginRequestDTO
        assert LoginResponseDTO
        assert TokenDTO
        assert PermissionDTO

    def test_import_root_module(self) -> None:
        import adip.auth
        assert adip.auth.__doc__ is not None
