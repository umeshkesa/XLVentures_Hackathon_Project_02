"""Authentication & Authorization Module for the ADIP Platform.

Provides enterprise identity, session, token, and permission management
for the ADIP platform. Integrates with the REST API Layer but remains
completely independent from business logic.

Architecture:
    AuthService  →  AuthManager  →  AuthCoordinator
                                        ├── AuthenticationProvider
                                        ├── AuthorizationProvider
                                        ├── TokenProvider
                                        ├── SessionProvider
                                        └── PermissionProvider

AuthService is the ONLY public API.
"""

from __future__ import annotations
