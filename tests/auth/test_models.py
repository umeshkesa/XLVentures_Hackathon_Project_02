"""Tests for Auth & Authorization domain models."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

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


class TestPermission:
    def test_defaults(self) -> None:
        p = Permission()
        assert p.resource == ""
        assert p.permission_type == PermissionType.READ
        assert p.description == ""
        assert p.domain == AuthDomain.SYSTEM
        assert p.conditions == {}
        assert p.metadata == {}

    def test_custom_values(self) -> None:
        p = Permission(
            resource="energy:readings:read",
            permission_type=PermissionType.READ,
            description="Read energy readings",
            domain=AuthDomain.ENERGY,
            conditions={"ip_range": "10.0.0.0/8"},
        )
        assert p.resource == "energy:readings:read"
        assert p.permission_type == PermissionType.READ
        assert p.domain == AuthDomain.ENERGY
        assert p.conditions["ip_range"] == "10.0.0.0/8"

    def test_uuid_generated(self) -> None:
        p = Permission()
        assert isinstance(p.permission_id, uuid.UUID)


class TestRole:
    def test_defaults(self) -> None:
        r = Role()
        assert r.name == ""
        assert r.description == ""
        assert r.permissions == []
        assert r.parent_role_id is None
        assert r.domain == AuthDomain.SYSTEM
        assert not r.is_system_role

    def test_custom_values(self) -> None:
        perm = Permission(resource="energy:read", permission_type=PermissionType.READ)
        r = Role(
            name="Energy Viewer",
            description="Can view energy data",
            permissions=[perm],
            domain=AuthDomain.ENERGY,
            is_system_role=True,
        )
        assert r.name == "Energy Viewer"
        assert len(r.permissions) == 1
        assert r.permissions[0].resource == "energy:read"
        assert r.is_system_role

    def test_with_parent_role(self) -> None:
        parent_id = uuid.uuid4()
        r = Role(name="Child Role", parent_role_id=parent_id)
        assert r.parent_role_id == parent_id


class TestGroup:
    def test_defaults(self) -> None:
        g = Group()
        assert g.name == ""
        assert g.group_type == GroupType.TEAM
        assert g.member_ids == []
        assert g.role_ids == []
        assert g.parent_group_id is None

    def test_custom_values(self) -> None:
        member_id = uuid.uuid4()
        role_id = uuid.uuid4()
        g = Group(
            name="Energy Team",
            description="Team handling energy operations",
            group_type=GroupType.DEPARTMENT,
            member_ids=[member_id],
            role_ids=[role_id],
            domain=AuthDomain.ENERGY,
        )
        assert g.name == "Energy Team"
        assert g.group_type == GroupType.DEPARTMENT
        assert len(g.member_ids) == 1
        assert len(g.role_ids) == 1
        assert g.domain == AuthDomain.ENERGY


class TestOrganization:
    def test_defaults(self) -> None:
        o = Organization()
        assert o.name == ""
        assert o.org_type == OrganizationType.ENTERPRISE
        assert o.domains == []
        assert o.is_active

    def test_custom_values(self) -> None:
        o = Organization(
            name="ACME Energy Corp",
            description="Energy provider",
            org_type=OrganizationType.ENTERPRISE,
            domains=[AuthDomain.ENERGY, AuthDomain.SYSTEM],
            is_active=True,
        )
        assert o.name == "ACME Energy Corp"
        assert len(o.domains) == 2
        assert o.is_active


class TestUser:
    def test_defaults(self) -> None:
        u = User()
        assert u.username == ""
        assert u.email == ""
        assert u.display_name == ""
        assert u.status == UserStatus.PENDING_ACTIVATION
        assert u.roles == []
        assert u.groups == []
        assert u.organization_id is None
        assert u.permissions == []
        assert u.domains == []

    def test_custom_values(self) -> None:
        role_id = uuid.uuid4()
        group_id = uuid.uuid4()
        org_id = uuid.uuid4()
        u = User(
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
            status=UserStatus.ACTIVE,
            roles=[role_id],
            groups=[group_id],
            organization_id=org_id,
            domains=[AuthDomain.ENERGY],
        )
        assert u.username == "john.doe"
        assert u.email == "john@example.com"
        assert u.status == UserStatus.ACTIVE
        assert len(u.roles) == 1
        assert u.organization_id == org_id

    def test_with_direct_permissions(self) -> None:
        perm = Permission(resource="admin:manage", permission_type=PermissionType.MANAGE)
        u = User(username="admin", permissions=[perm])
        assert len(u.permissions) == 1
        assert u.permissions[0].resource == "admin:manage"


class TestServiceAccount:
    def test_defaults(self) -> None:
        sa = ServiceAccount()
        assert sa.name == ""
        assert sa.status == UserStatus.ACTIVE
        assert sa.roles == []
        assert sa.organization_id is None
        assert sa.permissions == []
        assert sa.domains == []

    def test_custom_values(self) -> None:
        org_id = uuid.uuid4()
        sa = ServiceAccount(
            name="data-pipeline",
            description="ETL data pipeline",
            status=UserStatus.ACTIVE,
            organization_id=org_id,
            domains=[AuthDomain.ENERGY, AuthDomain.KNOWLEDGE],
        )
        assert sa.name == "data-pipeline"
        assert sa.status == UserStatus.ACTIVE
        assert len(sa.domains) == 2


class TestToken:
    def test_defaults(self) -> None:
        expiry = datetime.now(UTC) + timedelta(hours=1)
        t = Token(
            token_type=TokenType.JWT,
            principal_id=uuid.uuid4(),
            expires_at=expiry,
        )
        assert t.token_type == TokenType.JWT
        assert not t.is_revoked
        assert t.metadata == {}
        assert isinstance(t.token_id, uuid.UUID)

    def test_revoked(self) -> None:
        expiry = datetime.now(UTC) + timedelta(hours=1)
        t = Token(
            token_type=TokenType.API_KEY,
            principal_id=uuid.uuid4(),
            expires_at=expiry,
            is_revoked=True,
        )
        assert t.is_revoked

    def test_invalid_expiry_in_past(self) -> None:
        expiry = datetime.now(UTC) - timedelta(hours=1)
        t = Token(
            token_type=TokenType.JWT,
            principal_id=uuid.uuid4(),
            expires_at=expiry,
        )
        assert t.expires_at < datetime.now(UTC)


class TestRefreshToken:
    def test_defaults(self) -> None:
        expiry = datetime.now(UTC) + timedelta(days=7)
        rt = RefreshToken(
            token_id=uuid.uuid4(),
            principal_id=uuid.uuid4(),
            expires_at=expiry,
        )
        assert rt.rotation_count == 0
        assert not rt.is_revoked
        assert isinstance(rt.refresh_token_id, uuid.UUID)

    def test_rotation(self) -> None:
        expiry = datetime.now(UTC) + timedelta(days=7)
        rt = RefreshToken(
            token_id=uuid.uuid4(),
            principal_id=uuid.uuid4(),
            expires_at=expiry,
            rotation_count=3,
        )
        assert rt.rotation_count == 3


class TestApiKey:
    def test_defaults(self) -> None:
        ak = ApiKey(
            principal_id=uuid.uuid4(),
        )
        assert ak.key_prefix == ""
        assert ak.name == ""
        assert ak.expires_at is None
        assert not ak.is_revoked
        assert ak.last_used_at is None
        assert ak.permissions == []

    def test_custom_values(self) -> None:
        ak = ApiKey(
            key_prefix="ak_abc123",
            principal_id=uuid.uuid4(),
            name="CI/CD Pipeline Key",
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
        assert ak.key_prefix == "ak_abc123"
        assert ak.name == "CI/CD Pipeline Key"
        assert ak.expires_at is not None

    def test_with_permissions(self) -> None:
        p = Permission(resource="ci:pipeline", permission_type=PermissionType.EXECUTE)
        ak = ApiKey(
            key_prefix="ak_abc",
            principal_id=uuid.uuid4(),
            permissions=[p],
        )
        assert len(ak.permissions) == 1


class TestSession:
    def test_defaults(self) -> None:
        expiry = datetime.now(UTC) + timedelta(hours=8)
        s = Session(
            principal_id=uuid.uuid4(),
            expires_at=expiry,
        )
        assert s.status == SessionStatus.ACTIVE
        assert s.principal_type == "user"
        assert s.auth_method == AuthenticationMethod.TOKEN
        assert s.ip_address == ""
        assert s.user_agent == ""
        assert s.metadata == {}

    def test_custom_values(self) -> None:
        token_id = uuid.uuid4()
        expiry = datetime.now(UTC) + timedelta(hours=8)
        s = Session(
            principal_id=uuid.uuid4(),
            principal_type="service_account",
            status=SessionStatus.ACTIVE,
            token_id=token_id,
            auth_method=AuthenticationMethod.SERVICE_ACCOUNT,
            ip_address="10.0.0.1",
            user_agent="data-pipeline/1.0",
            expires_at=expiry,
        )
        assert s.principal_type == "service_account"
        assert s.auth_method == AuthenticationMethod.SERVICE_ACCOUNT
        assert s.ip_address == "10.0.0.1"

    def test_expired_session(self) -> None:
        expiry = datetime.now(UTC) - timedelta(hours=1)
        s = Session(
            principal_id=uuid.uuid4(),
            status=SessionStatus.EXPIRED,
            expires_at=expiry,
        )
        assert s.status == SessionStatus.EXPIRED
        assert s.expires_at < datetime.now(UTC)


class TestSecurityContext:
    def test_defaults(self) -> None:
        sc = SecurityContext(principal_id=uuid.uuid4())
        assert sc.principal_type == "user"
        assert sc.session_id is None
        assert sc.token_id is None
        assert sc.organization_id is None
        assert sc.roles == []
        assert sc.permissions == []
        assert sc.domains == []
        assert not sc.is_authenticated

    def test_authenticated(self) -> None:
        org_id = uuid.uuid4()
        sc = SecurityContext(
            principal_id=uuid.uuid4(),
            principal_type="user",
            session_id=uuid.uuid4(),
            token_id=uuid.uuid4(),
            organization_id=org_id,
            roles=["energy_viewer", "admin"],
            permissions=["energy:read", "energy:write"],
            domains=[AuthDomain.ENERGY],
            is_authenticated=True,
        )
        assert sc.is_authenticated
        assert len(sc.roles) == 2
        assert sc.permissions[0] == "energy:read"
        assert sc.organization_id == org_id


class TestAuthenticationContext:
    def test_defaults(self) -> None:
        ac = AuthenticationContext()
        assert ac.principal_id is None
        assert ac.method == AuthenticationMethod.TOKEN
        assert ac.credentials == {}
        assert ac.ip_address == ""
        assert ac.user_agent == ""

    def test_custom_values(self) -> None:
        ac = AuthenticationContext(
            principal_id=uuid.uuid4(),
            method=AuthenticationMethod.PASSWORD,
            credentials={"username": "john", "password": "***"},
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        assert ac.method == AuthenticationMethod.PASSWORD
        assert ac.credentials["username"] == "john"
        assert ac.ip_address == "192.168.1.1"


class TestAuthorizationContext:
    def test_defaults(self) -> None:
        ac = AuthorizationContext(principal_id=uuid.uuid4())
        assert ac.principal_type == "user"
        assert ac.resource == ""
        assert ac.action == PermissionType.READ
        assert ac.domain == AuthDomain.SYSTEM
        assert ac.organization_id is None

    def test_custom_values(self) -> None:
        org_id = uuid.uuid4()
        ac = AuthorizationContext(
            principal_id=uuid.uuid4(),
            principal_type="service_account",
            resource="energy:readings:write",
            action=PermissionType.WRITE,
            domain=AuthDomain.ENERGY,
            organization_id=org_id,
            environment={"ip_range": "10.0.0.0/8"},
        )
        assert ac.action == PermissionType.WRITE
        assert ac.domain == AuthDomain.ENERGY
        assert ac.environment["ip_range"] == "10.0.0.0/8"


class TestAuthMetrics:
    def test_defaults(self) -> None:
        m = AuthMetrics()
        assert m.authentications_total == 0
        assert m.authentications_success == 0
        assert m.authentications_failed == 0
        assert m.authorizations_total == 0
        assert m.tokens_issued == 0
        assert m.sessions_active == 0

    def test_custom_values(self) -> None:
        m = AuthMetrics(
            authentications_total=100,
            authentications_success=95,
            authentications_failed=5,
            authorizations_total=500,
            authorizations_granted=450,
            authorizations_denied=50,
            tokens_issued=80,
            tokens_revoked=10,
            sessions_active=25,
            sessions_expired=5,
        )
        assert m.authentications_total == 100
        assert m.authentications_success == 95
        assert m.sessions_active == 25

    def test_invalid_negative(self) -> None:
        with pytest.raises(ValidationError):
            AuthMetrics(authentications_total=-1)


class TestAuthMetadata:
    def test_defaults(self) -> None:
        m = AuthMetadata()
        assert m.correlation_id == ""
        assert m.request_id == ""
        assert m.duration_ms == 0.0
        assert m.ip_address == ""
        assert m.user_agent == ""

    def test_custom_values(self) -> None:
        m = AuthMetadata(
            correlation_id="corr-123",
            request_id="req-456",
            duration_ms=42.5,
            ip_address="10.0.0.1",
            user_agent="curl/7.68",
            metadata={"source": "api"},
        )
        assert m.correlation_id == "corr-123"
        assert m.duration_ms == 42.5
        assert m.metadata["source"] == "api"

    def test_invalid_duration_negative(self) -> None:
        with pytest.raises(ValidationError):
            AuthMetadata(duration_ms=-1.0)
