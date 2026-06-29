"""Unit tests for authentication and authorisation layers."""

from __future__ import annotations

import uuid
from datetime import UTC
from unittest.mock import AsyncMock

import jwt as pyjwt
import pytest

from adip.core.constants import Role
from adip.core.exceptions import AuthenticationException
from adip.security.auth import AnonymousUser, AuthenticatedUser
from adip.security.dependencies import _missing_permissions
from adip.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    token_from_header,
)
from adip.security.password import hash_password, verify_password
from adip.security.permissions import Permission
from adip.security.roles import resolve_permissions
from adip.services.auth import AuthService

# ── Password hashing ─────────────────────────────────────────────────────


class TestPassword:
    def test_hash_and_verify(self) -> None:
        h = hash_password("secure-password")
        assert verify_password("secure-password", h)
        assert not verify_password("wrong-password", h)

    def test_hash_is_different_each_time(self) -> None:
        h1 = hash_password("p4ss")
        h2 = hash_password("p4ss")
        assert h1 != h2


# ── JWT tokens ───────────────────────────────────────────────────────────


class TestJWT:
    def test_create_and_decode_access_token(self) -> None:
        user = AuthenticatedUser(
            sub="user-1",
            roles=[Role.ADMIN],
            permissions={Permission.USER_READ, Permission.REPORT_CREATE},
        )
        token = create_access_token(user)
        payload = decode_token(token)
        assert payload.sub == "user-1"
        assert payload.token_type == "access"
        assert "admin" in payload.roles
        assert "user:read" in payload.permissions

    def test_create_and_decode_refresh_token(self) -> None:
        user = AuthenticatedUser(sub="user-1", roles=[Role.OPERATOR])
        token = create_refresh_token(user)
        payload = decode_token(token)
        assert payload.sub == "user-1"
        assert payload.token_type == "refresh"
        assert "operator" in payload.roles
        # Refresh tokens carry no permissions
        assert payload.permissions == []

    def test_decode_expired_token_raises(self) -> None:
        from datetime import datetime, timedelta

        # Manually create an expired token
        settings = __import__("adip.config.settings", fromlist=["get_settings"]).get_settings()
        secret = settings.security.secret_key.get_secret_value()
        payload = {
            "sub": "u1",
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "token_type": "access",
            "roles": [],
            "permissions": [],
        }
        token = pyjwt.encode(payload, secret, algorithm="HS256")
        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_token(token)

    def test_decode_malformed_token_raises(self) -> None:
        with pytest.raises(pyjwt.PyJWTError):
            decode_token("not.a.token")

    def test_token_from_header(self) -> None:
        assert token_from_header("Bearer abc123") == "abc123"
        assert token_from_header(None) is None
        assert token_from_header("Basic xyz") is None

    def test_token_roundtrip_with_permissions(self) -> None:
        user = AuthenticatedUser(
            sub="analyst-1",
            roles=[Role.ANALYST],
            permissions=resolve_permissions(Role.ANALYST),
        )
        token = create_access_token(user)
        payload = decode_token(token)
        assert payload.sub == "analyst-1"
        perms = {Permission(p) for p in payload.permissions}
        assert Permission.REPORT_CREATE in perms
        assert Permission.REPORT_READ in perms
        assert Permission.USER_CREATE not in perms


# ── Role / permission resolution ─────────────────────────────────────────


class TestRoles:
    def test_super_admin_has_all_permissions(self) -> None:
        perms = resolve_permissions(Role.SUPER_ADMIN)
        assert Permission.USER_CREATE in perms
        assert Permission.SYSTEM_UPDATE in perms
        assert len(perms) == 16

    def test_viewer_has_no_permissions(self) -> None:
        perms = resolve_permissions(Role.VIEWER)
        assert perms == set()

    def test_analyst_has_report_permissions(self) -> None:
        perms = resolve_permissions(Role.ANALYST)
        assert Permission.REPORT_CREATE in perms
        assert Permission.REPORT_READ in perms
        assert Permission.USER_CREATE not in perms
        assert Permission.USER_READ not in perms


# ── Auth service ─────────────────────────────────────────────────────────


class MockUser:
    """Minimal user stub for service tests."""

    def __init__(self, uid: str, email: str, role: Role, active: bool = True) -> None:
        self.id = uuid.uuid4()
        self.email = email
        self.hashed_password = hash_password("pass123")
        self.role = role
        self.is_active = active
        self.full_name = f"User {email}"


class TestAuthService:
    @pytest.mark.asyncio
    async def test_authenticate_success(self) -> None:
        mock_user = MockUser("u1", "a@b.com", Role.ADMIN)
        loader = AsyncMock(return_value=mock_user)
        service = AuthService(user_loader=loader)
        result = await service.authenticate("a@b.com", "pass123")
        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self) -> None:
        mock_user = MockUser("u1", "a@b.com", Role.ADMIN)
        loader = AsyncMock(return_value=mock_user)
        service = AuthService(user_loader=loader)
        with pytest.raises(AuthenticationException):
            await service.authenticate("a@b.com", "wrong")

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self) -> None:
        mock_user = MockUser("u1", "a@b.com", Role.ADMIN, active=False)
        loader = AsyncMock(return_value=mock_user)
        service = AuthService(user_loader=loader)
        with pytest.raises(AuthenticationException):
            await service.authenticate("a@b.com", "pass123")

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self) -> None:
        loader = AsyncMock(return_value=None)
        service = AuthService(user_loader=loader)
        with pytest.raises(AuthenticationException):
            await service.authenticate("unknown@b.com", "pass123")

    @pytest.mark.asyncio
    async def test_refresh_success(self) -> None:
        mock_user = MockUser("u1", "a@b.com", Role.ADMIN)
        loader = AsyncMock(return_value=mock_user)
        service = AuthService(user_loader=loader)

        # First authenticate to get a refresh token
        auth_result = await service.authenticate("a@b.com", "pass123")

        # Then refresh
        refresh_result = await service.refresh(auth_result.refresh_token)
        assert refresh_result.access_token
        assert refresh_result.refresh_token == auth_result.refresh_token

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self) -> None:
        mock_user = MockUser("u1", "a@b.com", Role.ADMIN)
        loader = AsyncMock(return_value=mock_user)
        service = AuthService(user_loader=loader)

        auth_result = await service.authenticate("a@b.com", "pass123")

        with pytest.raises(AuthenticationException):
            await service.refresh(auth_result.access_token)

    @pytest.mark.asyncio
    async def test_get_current_user_success(self) -> None:
        mock_user = MockUser("u1", "a@b.com", Role.ANALYST)
        loader = AsyncMock(return_value=mock_user)
        service = AuthService(user_loader=loader)

        auth_result = await service.authenticate("a@b.com", "pass123")
        current = await service.get_current_user(auth_result.access_token)
        assert current.sub == str(mock_user.id)
        assert Role.ANALYST in current.roles
        assert Permission.REPORT_CREATE in current.permissions

    @pytest.mark.asyncio
    async def test_get_current_user_with_refresh_token_fails(self) -> None:
        mock_user = MockUser("u1", "a@b.com", Role.ADMIN)
        loader = AsyncMock(return_value=mock_user)
        service = AuthService(user_loader=loader)

        auth_result = await service.authenticate("a@b.com", "pass123")

        with pytest.raises(AuthenticationException):
            await service.get_current_user(auth_result.refresh_token)


# ── Dependencies helpers ─────────────────────────────────────────────────


class TestDependencies:
    def test_missing_permissions(self) -> None:
        missing = _missing_permissions(
            {Permission.USER_READ},
            (Permission.USER_READ, Permission.REPORT_CREATE),
        )
        assert missing == ["report:create"]

        missing = _missing_permissions(
            {Permission.USER_READ, Permission.REPORT_CREATE},
            (Permission.USER_READ,),
        )
        assert missing == []

    def test_anonymous_user(self) -> None:
        anon = AnonymousUser()
        assert anon.is_authenticated is False
        assert anon.sub == ""
        assert anon.roles == []
        assert anon.permissions == set()
