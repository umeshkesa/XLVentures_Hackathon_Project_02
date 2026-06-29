"""Enumerations for the Registry Framework.

Defines all enum types used across registry domain models, events,
interfaces, and DTOs.
"""

from __future__ import annotations

from enum import StrEnum


class RegistryType(StrEnum):
    """Supported registry types for the ADIP platform.

    CAPABILITY — capability registry for plugin capabilities and features.
    AGENT — agent registry for autonomous agents.
    TOOL — tool registry for utility tools and connectors.
    RULE — rule registry for enterprise policy rules.
    PLUGIN — plugin registry for all plugin types.
    WORKFLOW — workflow registry for workflow definitions.

    Future-ready: MODEL, CONNECTOR, POLICY, UI, REPORTING, ANALYTICS.
    """

    CAPABILITY = "CAPABILITY"
    AGENT = "AGENT"
    TOOL = "TOOL"
    RULE = "RULE"
    PLUGIN = "PLUGIN"
    WORKFLOW = "WORKFLOW"


class RegistryLifecycleStatus(StrEnum):
    """Lifecycle status of a registry entry.

    REGISTERED — entry has been registered but not yet validated.
    VALIDATED — entry has passed validation checks.
    ACTIVE — entry is active and available for use.
    SUSPENDED — entry is temporarily disabled.
    DEPRECATED — entry is superseded and scheduled for removal.
    REMOVED — entry has been permanently removed.
    """

    REGISTERED = "REGISTERED"
    VALIDATED = "VALIDATED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"
    REMOVED = "REMOVED"


class RegistryScope(StrEnum):
    """Scope of a registry entry.

    GLOBAL — accessible across the entire platform.
    SYSTEM — restricted to system-level components.
    DOMAIN — scoped to a specific domain.
    PLUGIN — scoped to a specific plugin.
    TENANT — scoped to a specific tenant.
    USER — scoped to a specific user.
    """

    GLOBAL = "GLOBAL"
    SYSTEM = "SYSTEM"
    DOMAIN = "DOMAIN"
    PLUGIN = "PLUGIN"
    TENANT = "TENANT"
    USER = "USER"
