"""String manipulation helpers: slugify, truncate, case conversion, etc."""

from __future__ import annotations

import re
import secrets
import string as str_mod

_RE_SLUGIFY = re.compile(r"[^\w\s-]", re.UNICODE)
_RE_WHITESPACE = re.compile(r"[_\s]+")
_RE_CAMEL_TO_SNAKE = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_RE_SNAKE_TO_CAMEL = re.compile(r"_([a-z])")


def slugify(value: str, separator: str = "-") -> str:
    """Convert *value* to a URL-safe slug.

    Examples::

        slugify("Hello World")        -> "hello-world"
        slugify("ADIP Config")        -> "adip-config"
        slugify(" déjà_vu! ")         -> "deja-vu"
    """
    value = _RE_SLUGIFY.sub("", value).strip().lower()
    value = _RE_WHITESPACE.sub(separator, value)
    return value.strip(separator)


def truncate(value: str, max_length: int, suffix: str = "...") -> str:
    """Truncate *value* to *max_length* characters, appending *suffix*.

    If *value* is shorter than *max_length*, it is returned unchanged.
    """
    if len(value) <= max_length:
        return value
    return value[: max_length - len(suffix)].rstrip() + suffix


def camel_to_snake(value: str) -> str:
    """Convert ``camelCase`` or ``PascalCase`` to ``snake_case``.

    Examples::

        camel_to_snake("userId")       -> "user_id"
        camel_to_snake("APIKey")       -> "api_key"
        camel_to_snake("HTTPServer")   -> "http_server"
    """
    return _RE_CAMEL_TO_SNAKE.sub("_", value).lower()


def snake_to_camel(value: str, upper_first: bool = False) -> str:
    """Convert ``snake_case`` to ``camelCase``.

    Parameters
    ----------
    upper_first:
        If ``True``, produce ``PascalCase`` instead of ``camelCase``.
    """
    parts = value.lower().split("_")
    if upper_first:
        return "".join(p.capitalize() for p in parts)
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def random_string(length: int = 16, alphabet: str = str_mod.ascii_letters + str_mod.digits) -> str:
    """Return a cryptographically random string of *length* characters.

    Uses ``secrets`` module; suitable for tokens or temporary passwords.
    """
    return "".join(secrets.choice(alphabet) for _ in range(length))
