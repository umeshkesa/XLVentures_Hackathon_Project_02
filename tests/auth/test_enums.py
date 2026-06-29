"""Tests for Auth & Authorization enums."""

from __future__ import annotations

from enum import StrEnum

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


class TestTokenType:
    def test_values(self) -> None:
        assert TokenType.JWT == "JWT"
        assert TokenType.REFRESH_TOKEN == "REFRESH_TOKEN"
        assert TokenType.API_KEY == "API_KEY"
        assert TokenType.SERVICE_TOKEN == "SERVICE_TOKEN"

    def test_all_members(self) -> None:
        assert len(TokenType) == 4

    def test_is_str_enum(self) -> None:
        assert issubclass(TokenType, StrEnum)

    def test_member_access(self) -> None:
        assert TokenType("JWT") == TokenType.JWT
        assert TokenType("API_KEY") == TokenType.API_KEY


class TestSessionStatus:
    def test_values(self) -> None:
        assert SessionStatus.ACTIVE == "ACTIVE"
        assert SessionStatus.EXPIRED == "EXPIRED"
        assert SessionStatus.REVOKED == "REVOKED"
        assert SessionStatus.LOCKED == "LOCKED"

    def test_all_members(self) -> None:
        assert len(SessionStatus) == 4

    def test_is_str_enum(self) -> None:
        assert issubclass(SessionStatus, StrEnum)


class TestPermissionType:
    def test_values(self) -> None:
        assert PermissionType.READ == "READ"
        assert PermissionType.WRITE == "WRITE"
        assert PermissionType.EXECUTE == "EXECUTE"
        assert PermissionType.REVIEW == "REVIEW"
        assert PermissionType.APPROVE == "APPROVE"
        assert PermissionType.MANAGE == "MANAGE"

    def test_all_members(self) -> None:
        assert len(PermissionType) == 6

    def test_is_str_enum(self) -> None:
        assert issubclass(PermissionType, StrEnum)


class TestAuthDomain:
    def test_values(self) -> None:
        assert AuthDomain.SYSTEM == "SYSTEM"
        assert AuthDomain.PLANNER == "PLANNER"
        assert AuthDomain.WORKFLOW == "WORKFLOW"
        assert AuthDomain.MEMORY == "MEMORY"
        assert AuthDomain.KNOWLEDGE == "KNOWLEDGE"
        assert AuthDomain.REASONING == "REASONING"
        assert AuthDomain.EVIDENCE == "EVIDENCE"
        assert AuthDomain.ACTION == "ACTION"
        assert AuthDomain.ENERGY == "ENERGY"
        assert AuthDomain.CUSTOMER == "CUSTOMER"
        assert AuthDomain.PLUGIN == "PLUGIN"
        assert AuthDomain.AUTH == "AUTH"
        assert AuthDomain.API == "API"

    def test_all_members(self) -> None:
        assert len(AuthDomain) == 13

    def test_is_str_enum(self) -> None:
        assert issubclass(AuthDomain, StrEnum)


class TestAuthenticationMethod:
    def test_values(self) -> None:
        assert AuthenticationMethod.PASSWORD == "PASSWORD"
        assert AuthenticationMethod.TOKEN == "TOKEN"
        assert AuthenticationMethod.API_KEY == "API_KEY"
        assert AuthenticationMethod.SERVICE_ACCOUNT == "SERVICE_ACCOUNT"
        assert AuthenticationMethod.MULTI_FACTOR == "MULTI_FACTOR"

    def test_all_members(self) -> None:
        assert len(AuthenticationMethod) == 5

    def test_is_str_enum(self) -> None:
        assert issubclass(AuthenticationMethod, StrEnum)


class TestUserStatus:
    def test_values(self) -> None:
        assert UserStatus.ACTIVE == "ACTIVE"
        assert UserStatus.INACTIVE == "INACTIVE"
        assert UserStatus.LOCKED == "LOCKED"
        assert UserStatus.SUSPENDED == "SUSPENDED"
        assert UserStatus.DEACTIVATED == "DEACTIVATED"
        assert UserStatus.PENDING_ACTIVATION == "PENDING_ACTIVATION"

    def test_all_members(self) -> None:
        assert len(UserStatus) == 6

    def test_is_str_enum(self) -> None:
        assert issubclass(UserStatus, StrEnum)


class TestGroupType:
    def test_values(self) -> None:
        assert GroupType.DEPARTMENT == "DEPARTMENT"
        assert GroupType.TEAM == "TEAM"
        assert GroupType.ROLE_BASED == "ROLE_BASED"
        assert GroupType.PROJECT == "PROJECT"
        assert GroupType.CUSTOM == "CUSTOM"

    def test_all_members(self) -> None:
        assert len(GroupType) == 5

    def test_is_str_enum(self) -> None:
        assert issubclass(GroupType, StrEnum)


class TestOrganizationType:
    def test_values(self) -> None:
        assert OrganizationType.ENTERPRISE == "ENTERPRISE"
        assert OrganizationType.TEAM == "TEAM"
        assert OrganizationType.INDIVIDUAL == "INDIVIDUAL"
        assert OrganizationType.PARTNER == "PARTNER"

    def test_all_members(self) -> None:
        assert len(OrganizationType) == 4

    def test_is_str_enum(self) -> None:
        assert issubclass(OrganizationType, StrEnum)
