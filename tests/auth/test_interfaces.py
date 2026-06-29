"""Tests for Auth & Authorization interfaces."""

from __future__ import annotations

import abc

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


class TestInterfacesAreAbstract:
    def test_auth_service_is_abstract(self) -> None:
        assert issubclass(AuthService, abc.ABC)

    def test_auth_manager_is_abstract(self) -> None:
        assert issubclass(AuthManager, abc.ABC)

    def test_auth_coordinator_is_abstract(self) -> None:
        assert issubclass(AuthCoordinator, abc.ABC)

    def test_authentication_provider_is_abstract(self) -> None:
        assert issubclass(AuthenticationProvider, abc.ABC)

    def test_authorization_provider_is_abstract(self) -> None:
        assert issubclass(AuthorizationProvider, abc.ABC)

    def test_token_provider_is_abstract(self) -> None:
        assert issubclass(TokenProvider, abc.ABC)

    def test_session_provider_is_abstract(self) -> None:
        assert issubclass(SessionProvider, abc.ABC)

    def test_permission_provider_is_abstract(self) -> None:
        assert issubclass(PermissionProvider, abc.ABC)


class TestInterfaceMethods:
    def test_auth_service_has_authenticate(self) -> None:
        assert hasattr(AuthService, "authenticate")
        assert getattr(AuthService.authenticate, "__isabstractmethod__", False)

    def test_auth_service_has_authorize(self) -> None:
        assert hasattr(AuthService, "authorize")
        assert getattr(AuthService.authorize, "__isabstractmethod__", False)

    def test_auth_service_has_create_session(self) -> None:
        assert hasattr(AuthService, "create_session")
        assert getattr(AuthService.create_session, "__isabstractmethod__", False)

    def test_auth_service_has_get_session(self) -> None:
        assert hasattr(AuthService, "get_session")
        assert getattr(AuthService.get_session, "__isabstractmethod__", False)

    def test_auth_service_has_revoke_session(self) -> None:
        assert hasattr(AuthService, "revoke_session")
        assert getattr(AuthService.revoke_session, "__isabstractmethod__", False)

    def test_auth_service_has_issue_token(self) -> None:
        assert hasattr(AuthService, "issue_token")
        assert getattr(AuthService.issue_token, "__isabstractmethod__", False)

    def test_auth_service_has_revoke_token(self) -> None:
        assert hasattr(AuthService, "revoke_token")
        assert getattr(AuthService.revoke_token, "__isabstractmethod__", False)

    def test_auth_service_has_check_permission(self) -> None:
        assert hasattr(AuthService, "check_permission")
        assert getattr(AuthService.check_permission, "__isabstractmethod__", False)

    def test_auth_service_has_get_user(self) -> None:
        assert hasattr(AuthService, "get_user")
        assert getattr(AuthService.get_user, "__isabstractmethod__", False)

    def test_auth_service_has_get_metrics(self) -> None:
        assert hasattr(AuthService, "get_metrics")
        assert getattr(AuthService.get_metrics, "__isabstractmethod__", False)

    def test_auth_manager_has_authenticate(self) -> None:
        assert hasattr(AuthManager, "authenticate")
        assert getattr(AuthManager.authenticate, "__isabstractmethod__", False)

    def test_auth_manager_has_authorize(self) -> None:
        assert hasattr(AuthManager, "authorize")
        assert getattr(AuthManager.authorize, "__isabstractmethod__", False)

    def test_auth_manager_has_create_session(self) -> None:
        assert hasattr(AuthManager, "create_session")
        assert getattr(AuthManager.create_session, "__isabstractmethod__", False)

    def test_auth_manager_has_get_session(self) -> None:
        assert hasattr(AuthManager, "get_session")
        assert getattr(AuthManager.get_session, "__isabstractmethod__", False)

    def test_auth_manager_has_revoke_session(self) -> None:
        assert hasattr(AuthManager, "revoke_session")
        assert getattr(AuthManager.revoke_session, "__isabstractmethod__", False)

    def test_auth_manager_has_issue_token(self) -> None:
        assert hasattr(AuthManager, "issue_token")
        assert getattr(AuthManager.issue_token, "__isabstractmethod__", False)

    def test_auth_manager_has_revoke_token(self) -> None:
        assert hasattr(AuthManager, "revoke_token")
        assert getattr(AuthManager.revoke_token, "__isabstractmethod__", False)

    def test_auth_manager_has_check_permission(self) -> None:
        assert hasattr(AuthManager, "check_permission")
        assert getattr(AuthManager.check_permission, "__isabstractmethod__", False)

    def test_auth_manager_has_get_metrics(self) -> None:
        assert hasattr(AuthManager, "get_metrics")
        assert getattr(AuthManager.get_metrics, "__isabstractmethod__", False)

    def test_auth_coordinator_has_authenticate(self) -> None:
        assert hasattr(AuthCoordinator, "authenticate")
        assert getattr(AuthCoordinator.authenticate, "__isabstractmethod__", False)

    def test_auth_coordinator_has_authorize(self) -> None:
        assert hasattr(AuthCoordinator, "authorize")
        assert getattr(AuthCoordinator.authorize, "__isabstractmethod__", False)

    def test_authentication_provider_has_authenticate(self) -> None:
        assert hasattr(AuthenticationProvider, "authenticate")
        assert getattr(AuthenticationProvider.authenticate, "__isabstractmethod__", False)

    def test_authorization_provider_has_is_authorized(self) -> None:
        assert hasattr(AuthorizationProvider, "is_authorized")
        assert getattr(AuthorizationProvider.is_authorized, "__isabstractmethod__", False)

    def test_token_provider_has_issue_token(self) -> None:
        assert hasattr(TokenProvider, "issue_token")
        assert getattr(TokenProvider.issue_token, "__isabstractmethod__", False)

    def test_session_provider_has_create_session(self) -> None:
        assert hasattr(SessionProvider, "create_session")
        assert getattr(SessionProvider.create_session, "__isabstractmethod__", False)

    def test_permission_provider_has_get_permissions(self) -> None:
        assert hasattr(PermissionProvider, "get_permissions")
        assert getattr(PermissionProvider.get_permissions, "__isabstractmethod__", False)
