"""Request and response schemas for authentication endpoints."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """POST /auth/login request body."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=1, description="User password")


class TokenResponse(BaseModel):
    """Successful authentication response."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshRequest(BaseModel):
    """POST /auth/refresh request body."""

    refresh_token: str = Field(min_length=1, description="Valid refresh token")


class UserMeResponse(BaseModel):
    """GET /users/me response body."""

    id: str = Field(description="User UUID")
    email: str = Field(description="Email address")
    full_name: str | None = Field(default=None, description="Display name")
    role: str = Field(description="Assigned role")
    is_active: bool = Field(description="Whether the account is active")


class LogoutResponse(BaseModel):
    """POST /auth/logout response body."""

    message: str = Field(default="Logged out successfully.")
