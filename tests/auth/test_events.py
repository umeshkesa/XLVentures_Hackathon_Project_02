"""Tests for Auth & Authorization events."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from adip.auth.contracts.events import (
    AccessDenied,
    EventVersion,
    PermissionChecked,
    TokenIssued,
    TokenRefreshed,
    UserAuthenticated,
    UserLoggedOut,
)
from adip.auth.enums import AuthDomain, AuthenticationMethod, PermissionType


class TestEventVersion:
    def test_version_string(self) -> None:
        assert EventVersion == "1.0.0"


class TestAuthEvent:
    def test_defaults(self) -> None:
        event = UserAuthenticated(
            principal_id=uuid.uuid4(),
            method=AuthenticationMethod.PASSWORD,
        )
        assert event.domain == AuthDomain.AUTH
        assert event.correlation_id == ""
        assert event.payload == {}
        assert isinstance(event.timestamp, datetime)

    def test_custom_values(self) -> None:
        event = UserAuthenticated(
            principal_id=uuid.uuid4(),
            method=AuthenticationMethod.MULTI_FACTOR,
            domain=AuthDomain.ENERGY,
            correlation_id="corr-789",
            payload={"source": "web"},
        )
        assert event.domain == AuthDomain.ENERGY
        assert event.correlation_id == "corr-789"
        assert event.payload["source"] == "web"

    def test_uuid_generated(self) -> None:
        event = UserAuthenticated(
            principal_id=uuid.uuid4(),
            method=AuthenticationMethod.PASSWORD,
        )
        assert isinstance(event.event_id, uuid.UUID)


class TestUserAuthenticated:
    def test_defaults(self) -> None:
        event = UserAuthenticated(
            principal_id=uuid.uuid4(),
            method=AuthenticationMethod.PASSWORD,
        )
        assert event.method == AuthenticationMethod.PASSWORD
        assert event.session_id is None

    def test_with_session(self) -> None:
        session_id = uuid.uuid4()
        event = UserAuthenticated(
            principal_id=uuid.uuid4(),
            method=AuthenticationMethod.PASSWORD,
            session_id=session_id,
        )
        assert event.session_id == session_id


class TestUserLoggedOut:
    def test_defaults(self) -> None:
        event = UserLoggedOut(
            principal_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
        )
        assert event.reason == "user_initiated"

    def test_custom_reason(self) -> None:
        event = UserLoggedOut(
            principal_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            reason="session_expired",
        )
        assert event.reason == "session_expired"


class TestTokenIssued:
    def test_defaults(self) -> None:
        now = datetime.now(UTC)
        event = TokenIssued(
            principal_id=uuid.uuid4(),
            token_id=uuid.uuid4(),
            expires_at=now,
        )
        assert event.token_type == ""

    def test_custom_values(self) -> None:
        now = datetime.now(UTC)
        token_id = uuid.uuid4()
        event = TokenIssued(
            principal_id=uuid.uuid4(),
            token_id=token_id,
            token_type="JWT",
            expires_at=now,
        )
        assert event.token_id == token_id
        assert event.token_type == "JWT"


class TestTokenRefreshed:
    def test_custom_values(self) -> None:
        old_id = uuid.uuid4()
        new_id = uuid.uuid4()
        event = TokenRefreshed(
            principal_id=uuid.uuid4(),
            old_token_id=old_id,
            new_token_id=new_id,
        )
        assert event.old_token_id == old_id
        assert event.new_token_id == new_id


class TestPermissionChecked:
    def test_defaults(self) -> None:
        event = PermissionChecked(
            principal_id=uuid.uuid4(),
        )
        assert event.resource == ""
        assert event.action == PermissionType.READ
        assert not event.granted

    def test_granted(self) -> None:
        event = PermissionChecked(
            principal_id=uuid.uuid4(),
            resource="energy:readings:read",
            action=PermissionType.READ,
            granted=True,
        )
        assert event.resource == "energy:readings:read"
        assert event.granted


class TestAccessDenied:
    def test_defaults(self) -> None:
        event = AccessDenied(
            principal_id=uuid.uuid4(),
        )
        assert event.resource == ""
        assert event.action == PermissionType.READ
        assert event.reason == ""

    def test_custom_values(self) -> None:
        event = AccessDenied(
            principal_id=uuid.uuid4(),
            resource="energy:readings:write",
            action=PermissionType.WRITE,
            reason="insufficient_permissions",
        )
        assert event.reason == "insufficient_permissions"
        assert event.action == PermissionType.WRITE
