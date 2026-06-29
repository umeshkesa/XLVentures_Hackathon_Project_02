"""Authentication and user-management endpoints.

Routes
------
- ``POST   /auth/login``   —  authenticate with email + password
- ``POST   /auth/refresh`` —  obtain a new access token from a refresh token
- ``POST   /auth/logout``  —  client-side logout (no-op on the server)
- ``GET    /users/me``     —  return the current user's profile
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adip.api.auth.schemas import (
    LoginRequest,
    LogoutResponse,
    RefreshRequest,
    TokenResponse,
    UserMeResponse,
)
from adip.database.connections.session import get_session
from adip.repositories.postgres.user_repository import UserRepository
from adip.security.auth import AuthenticatedUser
from adip.security.dependencies import require_authentication
from adip.services.auth import AuthService

router = APIRouter(tags=["auth"])


def _build_auth_service(session: AsyncSession) -> AuthService:
    repo = UserRepository(session)
    return AuthService(user_loader=repo.find_by_email)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> TokenResponse:
    """Authenticate with email and password, returning a token pair."""
    service = _build_auth_service(session)
    return await service.authenticate(body.email, body.password)


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> TokenResponse:
    """Exchange a valid refresh token for a new access token."""
    service = _build_auth_service(session)
    return await service.refresh(body.refresh_token)


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout() -> LogoutResponse:
    """Log out the current client.

    This is a **no-op** from the server's perspective — token
    invalidation is handled client-side by discarding the tokens.
    """
    return LogoutResponse()


@router.get("/users/me", response_model=UserMeResponse)
async def users_me(
    current_user: AuthenticatedUser = Depends(require_authentication),  # noqa: B008
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> UserMeResponse:
    """Return the authenticated user's profile."""
    repo = UserRepository(session)
    user = await repo.find_one_by(email=current_user.sub)
    return UserMeResponse(
        id=current_user.sub,
        email=user.email if user else current_user.sub,
        full_name=user.full_name if user else None,
        role=current_user.roles[0].value if current_user.roles else "",
        is_active=user.is_active if user else True,
    )
