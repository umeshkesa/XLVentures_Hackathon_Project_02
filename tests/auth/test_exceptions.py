"""Tests for Auth & Authorization exceptions."""

from __future__ import annotations

from adip.auth.contracts.exceptions import (
    AuthenticationException,
    AuthException,
    AuthorizationException,
    SessionException,
    TokenException,
)


class TestAuthException:
    def test_default_message(self) -> None:
        exc = AuthException()
        assert str(exc) == "Auth error"

    def test_custom_message(self) -> None:
        exc = AuthException("Custom auth error")
        assert str(exc) == "Custom auth error"

    def test_inheritance(self) -> None:
        assert issubclass(AuthException, Exception)


class TestAuthenticationException:
    def test_default_message(self) -> None:
        exc = AuthenticationException()
        assert str(exc) == "Authentication failed"

    def test_with_principal_id(self) -> None:
        exc = AuthenticationException(principal_id="user-123")
        assert "user-123" in str(exc)

    def test_with_method(self) -> None:
        exc = AuthenticationException(method="PASSWORD")
        assert "PASSWORD" in str(exc)

    def test_with_both(self) -> None:
        exc = AuthenticationException(principal_id="user-123", method="PASSWORD")
        assert "user-123" in str(exc)
        assert "PASSWORD" in str(exc)

    def test_with_custom_message(self) -> None:
        exc = AuthenticationException(message="Invalid credentials")
        assert str(exc) == "Invalid credentials"

    def test_inheritance(self) -> None:
        assert issubclass(AuthenticationException, AuthException)

    def test_attributes(self) -> None:
        exc = AuthenticationException(principal_id="user-123", method="PASSWORD")
        assert exc.principal_id == "user-123"
        assert exc.method == "PASSWORD"


class TestAuthorizationException:
    def test_default_message(self) -> None:
        exc = AuthorizationException()
        assert str(exc) == "Authorization denied"

    def test_with_principal_id(self) -> None:
        exc = AuthorizationException(principal_id="user-123")
        assert "user-123" in str(exc)

    def test_with_resource(self) -> None:
        exc = AuthorizationException(resource="energy:readings")
        assert "energy:readings" in str(exc)

    def test_with_action(self) -> None:
        exc = AuthorizationException(action="WRITE")
        assert "WRITE" in str(exc)

    def test_with_all(self) -> None:
        exc = AuthorizationException(
            principal_id="user-123",
            resource="energy:readings:write",
            action="WRITE",
        )
        assert "user-123" in str(exc)
        assert "energy:readings:write" in str(exc)
        assert "WRITE" in str(exc)

    def test_with_custom_message(self) -> None:
        exc = AuthorizationException(message="Insufficient permissions")
        assert str(exc) == "Insufficient permissions"

    def test_inheritance(self) -> None:
        assert issubclass(AuthorizationException, AuthException)

    def test_attributes(self) -> None:
        exc = AuthorizationException(
            principal_id="user-123",
            resource="energy:readings:write",
            action="WRITE",
        )
        assert exc.principal_id == "user-123"
        assert exc.resource == "energy:readings:write"
        assert exc.action == "WRITE"


class TestTokenException:
    def test_default_message(self) -> None:
        exc = TokenException()
        assert str(exc) == "Token error"

    def test_with_token_id(self) -> None:
        exc = TokenException(token_id="tok-123")
        assert "tok-123" in str(exc)

    def test_with_token_type(self) -> None:
        exc = TokenException(token_type="JWT")
        assert "JWT" in str(exc)

    def test_with_both(self) -> None:
        exc = TokenException(token_id="tok-123", token_type="JWT")
        assert "tok-123" in str(exc)
        assert "JWT" in str(exc)

    def test_with_custom_message(self) -> None:
        exc = TokenException(message="Token expired")
        assert str(exc) == "Token expired"

    def test_inheritance(self) -> None:
        assert issubclass(TokenException, AuthException)

    def test_attributes(self) -> None:
        exc = TokenException(token_id="tok-123", token_type="JWT")
        assert exc.token_id == "tok-123"
        assert exc.token_type == "JWT"


class TestSessionException:
    def test_default_message(self) -> None:
        exc = SessionException()
        assert str(exc) == "Session error"

    def test_with_session_id(self) -> None:
        exc = SessionException(session_id="sess-123")
        assert "sess-123" in str(exc)

    def test_with_principal_id(self) -> None:
        exc = SessionException(principal_id="user-123")
        assert "user-123" in str(exc)

    def test_with_both(self) -> None:
        exc = SessionException(session_id="sess-123", principal_id="user-123")
        assert "sess-123" in str(exc)
        assert "user-123" in str(exc)

    def test_with_custom_message(self) -> None:
        exc = SessionException(message="Session revoked")
        assert str(exc) == "Session revoked"

    def test_inheritance(self) -> None:
        assert issubclass(SessionException, AuthException)

    def test_attributes(self) -> None:
        exc = SessionException(session_id="sess-123", principal_id="user-123")
        assert exc.session_id == "sess-123"
        assert exc.principal_id == "user-123"
