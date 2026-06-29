"""File-system helpers for safe read/write, directory management, and temp files."""

from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import suppress
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """Create *path* and all parents if they do not exist.

    Returns the resolved ``Path``.
    """
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_read(path: str | Path, encoding: str = "utf-8") -> str | None:
    """Read a text file, returning ``None`` if the file does not exist.

    Raises ``PermissionError`` / ``OSError`` for other failures.
    """
    p = Path(path)
    if not p.is_file():
        return None
    return p.read_text(encoding=encoding)


def safe_read_bytes(path: str | Path) -> bytes | None:
    """Read a binary file, returning ``None`` if the file does not exist."""
    p = Path(path)
    if not p.is_file():
        return None
    return p.read_bytes()


def safe_write(path: str | Path, content: str | bytes, encoding: str = "utf-8") -> bool:
    """Write *content* to *path*, creating parent directories as needed.

    Returns ``True`` on success.
    """
    p = Path(path)
    ensure_dir(p.parent)
    if isinstance(content, str):
        p.write_text(content, encoding=encoding)
    else:
        p.write_bytes(content)
    return True


def atomic_write(path: str | Path, content: str | bytes, encoding: str = "utf-8") -> bool:
    """Atomically write *content* to *path* via a temporary file and rename.

    Prevents partial writes from being observed by concurrent readers.
    """
    p = Path(path).resolve()
    ensure_dir(p.parent)

    fd, tmp_path_str = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w" if isinstance(content, str) else "wb") as f:
            f.write(content)  # type: ignore[arg-type]
        os.replace(tmp_path_str, str(p))
    except BaseException:
        with suppress(OSError):
            os.unlink(tmp_path_str)
        raise
    return True


def get_size(path: str | Path) -> int:
    """Return the total size in bytes of a file or directory.

    For directories, the size is summed recursively.
    """
    p = Path(path)
    if p.is_file():
        return p.stat().st_size
    if p.is_dir():
        total = 0
        for entry in p.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
        return total
    return 0


def list_files(directory: str | Path, pattern: str = "*") -> list[Path]:
    """Return all files matching *pattern* under *directory*, recursively."""
    return sorted(Path(directory).rglob(pattern))


def copy_file(src: str | Path, dst: str | Path, overwrite: bool = False) -> bool:
    """Copy a single file from *src* to *dst*.

    Returns ``False`` if *dst* already exists and *overwrite* is ``False``.
    """
    dst_p = Path(dst)
    if dst_p.exists() and not overwrite:
        return False
    ensure_dir(dst_p.parent)
    shutil.copy2(str(src), str(dst_p))
    return True
