"""Tests for Auth & Authorization DTOs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from adip.auth.dtos import LoginRequestDTO, LoginResponseDTO, PermissionDTO, TokenDTO
from adip.auth.enums import AuthDomain, AuthenticationMethod, PermissionType


class TestLoginRequestDTO:
    def test_defaults(self) -> None:
        dto = LoginRequestDTO()
        assert dto.username == ""
        assert dto.password == ""
        assert dto.method == AuthenticationMethod.PASSWORD
        assert dto.organization_id is None
        assert dto.ip_address == ""
        assert dto.user_agent == ""
        assert dto.metadata == {}

    def test_custom_values(self) -> None:
        org_id = uuid.uuid4()
        dto = LoginRequestDTO(
            username="john.doe",
            password="s3cret",
            method=AuthenticationMethod.PASSWORD,
            organization_id=org_id,
            ip_address="10.0.0.1",
            user_agent="Mozilla/5.0",
            metadata={"source": "web"},
        )
        assert dto.username == "john.doe"
        assert dto.password == "s3cret"
        assert dto.method == AuthenticationMethod.PASSWORD
        assert dto.organization_id == org_id
        assert dto.ip_address == "10.0.0.1"


class TestLoginResponseDTO:
    def test_defaults(self) -> None:
        dto = LoginResponseDTO()
        assert not dto.success
        assert dto.session_id is None
        assert dto.token_id is None
        assert dto.principal_id is None
        assert dto.message == ""
        assert dto.metadata == {}

    def test_success_response(self) -> None:
        session_id = uuid.uuid4()
        token_id = uuid.uuid4()
        principal_id = uuid.uuid4()
        dto = LoginResponseDTO(
            success=True,
            session_id=session_id,
            token_id=token_id,
            principal_id=principal_id,
            message="Login successful",
        )
        assert dto.success
        assert dto.session_id == session_id
        assert dto.token_id == token_id
        assert dto.principal_id == principal_id
        assert dto.message == "Login successful"

    def test_failure_response(self) -> None:
        dto = LoginResponseDTO(
            success=False,
            message="Invalid credentials",
        )
        assert not dto.success
        assert dto.message == "Invalid credentials"
        assert dto.session_id is None


class TestTokenDTO:
    def test_defaults(self) -> None:
        now = datetime.now(UTC)
        dto = TokenDTO(
            token_id=uuid.uuid4(),
            principal_id=uuid.uuid4(),
            issued_at=now,
            expires_at=now,
        )
        assert dto.token_type == ""
        assert not dto.is_revoked
        assert dto.metadata == {}

    def test_custom_values(self) -> None:
        now = datetime.now(UTC)
        dto = TokenDTO(
            token_id=uuid.uuid4(),
            token_type="JWT",
            principal_id=uuid.uuid4(),
            issued_at=now,
            expires_at=now,
            is_revoked=True,
            metadata={"source": "refresh"},
        )
        assert dto.token_type == "JWT"
        assert dto.is_revoked
        assert dto.metadata["source"] == "refresh"


class TestPermissionDTO:
    def test_defaults(self) -> None:
        dto = PermissionDTO(
            permission_id=uuid.uuid4(),
        )
        assert dto.resource == ""
        assert dto.permission_type == PermissionType.READ
        assert dto.domain == AuthDomain.SYSTEM
        assert dto.granted

    def test_custom_values(self) -> None:
        dto = PermissionDTO(
            permission_id=uuid.uuid4(),
            resource="energy:readings:write",
            permission_type=PermissionType.WRITE,
            domain=AuthDomain.ENERGY,
            granted=True,
            metadata={"source": "role_assignment"},
        )
        assert dto.resource == "energy:readings:write"
        assert dto.permission_type == PermissionType.WRITE
        assert dto.domain == AuthDomain.ENERGY
        assert dto.metadata["source"] == "role_assignment"
