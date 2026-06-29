"""Plugin Manager exception hierarchy.

All plugin-related exceptions inherit from PluginException to ensure
consistent error handling across the platform.
"""

from __future__ import annotations


class PluginException(Exception):
    """Base exception for all plugin errors."""

    def __init__(self, message: str = "Plugin error") -> None:
        self.message = message
        super().__init__(self.message)


class PluginValidationException(PluginException):
    """Raised when a plugin operation fails validation."""

    def __init__(self, message: str = "Plugin validation error") -> None:
        super().__init__(message)


class PluginDependencyException(PluginException):
    """Raised when a plugin has unmet or incompatible dependencies."""

    def __init__(
        self,
        plugin_id: str = "",
        dependency_id: str = "",
        message: str = "",
    ) -> None:
        self.plugin_id = plugin_id
        self.dependency_id = dependency_id
        if not message:
            details = []
            if plugin_id:
                details.append(f"plugin: {plugin_id}")
            if dependency_id:
                details.append(f"dependency: {dependency_id}")
            message = f"Plugin dependency error ({'; '.join(details)})" if details else "Plugin dependency error"
        super().__init__(message)


class PluginLoadException(PluginException):
    """Raised when a plugin fails to load."""

    def __init__(
        self,
        plugin_id: str = "",
        message: str = "",
    ) -> None:
        self.plugin_id = plugin_id
        if not message:
            message = f"Plugin load failed for: {plugin_id}" if plugin_id else "Plugin load failed"
        super().__init__(message)


class SandboxException(PluginException):
    """Raised when a sandbox operation fails."""

    def __init__(
        self,
        sandbox_id: str = "",
        message: str = "",
    ) -> None:
        self.sandbox_id = sandbox_id
        if not message:
            message = f"Sandbox error ({sandbox_id})" if sandbox_id else "Sandbox error"
        super().__init__(message)
