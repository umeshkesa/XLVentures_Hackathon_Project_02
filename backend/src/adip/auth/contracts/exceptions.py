"""Auth & Authorization exception hierarchy.

All auth-related exceptions inherit from AuthException to ensure
consistent error handling across the platform.
"""

from __future__ import annotations


class AuthException(Exception):
    """Base exception for all auth & authorization errors."""

    def __init__(self, message: str = "Auth error") -> None:
        self.message = message
        super().__init__(self.message)


class AuthenticationException(AuthException):
    """Raised when an authentication operation fails."""

    def __init__(
        self,
        principal_id: str = "",
        method: str = "",
        message: str = "",
    ) -> None:
        self.principal_id = principal_id
        self.method = method
        if not message:
            details = []
            if principal_id:
                details.append(f"principal: {principal_id}")
            if method:
                details.append(f"method: {method}")
            message = f"Authentication failed ({'; '.join(details)})" if details else "Authentication failed"
        super().__init__(message)


class AuthorizationException(AuthException):
    """Raised when an authorization check fails."""

    def __init__(
        self,
        principal_id: str = "",
        resource: str = "",
        action: str = "",
        message: str = "",
    ) -> None:
        self.principal_id = principal_id
        self.resource = resource
        self.action = action
        if not message:
            details = []
            if principal_id:
                details.append(f"principal: {principal_id}")
            if resource:
                details.append(f"resource: {resource}")
            if action:
                details.append(f"action: {action}")
            message = f"Authorization denied ({'; '.join(details)})" if details else "Authorization denied"
        super().__init__(message)


class TokenException(AuthException):
    """Raised when a token operation fails."""

    def __init__(
        self,
        token_id: str = "",
        token_type: str = "",
        message: str = "",
    ) -> None:
        self.token_id = token_id
        self.token_type = token_type
        if not message:
            details = []
            if token_id:
                details.append(f"token: {token_id}")
            if token_type:
                details.append(f"type: {token_type}")
            message = f"Token error ({'; '.join(details)})" if details else "Token error"
        super().__init__(message)


class SessionException(AuthException):
    """Raised when a session operation fails."""

    def __init__(
        self,
        session_id: str = "",
        principal_id: str = "",
        message: str = "",
    ) -> None:
        self.session_id = session_id
        self.principal_id = principal_id
        if not message:
            details = []
            if session_id:
                details.append(f"session: {session_id}")
            if principal_id:
                details.append(f"principal: {principal_id}")
            message = f"Session error ({'; '.join(details)})" if details else "Session error"
        super().__init__(message)
