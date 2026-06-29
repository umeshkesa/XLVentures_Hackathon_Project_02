"""Password hashing and verification using bcrypt.

The stdlib-only PBKDF2 fallback is replaced with bcrypt for stronger
defence-in-depth and standardised hash encoding (modular crypt format).
"""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password* (modular crypt format)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify *password* against a bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())
