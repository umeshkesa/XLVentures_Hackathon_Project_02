"""Enumerations for the Plugin Manager.

Defines all enum types used across plugin domain models, events,
interfaces, and DTOs.
"""

from __future__ import annotations

from enum import StrEnum


class PluginType(StrEnum):
    """Supported plugin types for the ADIP platform.

    Domain — extends a specific domain (energy, healthcare, etc.).
    Agent — provides autonomous agent capabilities.
    Tool — provides utility tools and connectors.
    Knowledge — extends knowledge management.
    Rule — extends rule evaluation.
    Workflow — adds workflow orchestration primitives.
    Action — provides new action types for the action engine.

    Future-ready: UI, Connector, Integration, Reporting, Analytics, ML.
    """

    DOMAIN = "DOMAIN"
    AGENT = "AGENT"
    TOOL = "TOOL"
    KNOWLEDGE = "KNOWLEDGE"
    RULE = "RULE"
    WORKFLOW = "WORKFLOW"
    ACTION = "ACTION"


class PluginLifecycleStatus(StrEnum):
    """Lifecycle status of a plugin.

    DISCOVERED — found but not yet validated.
    VALIDATED — manifest and dependencies checked.
    INSTALLED — registered with the Plugin Manager.
    LOADED — loaded into memory but not yet initialised.
    INITIALIZED — initialisation complete but not yet active.
    ACTIVE — fully active and serving requests.
    SUSPENDED — temporarily disabled.
    UNLOADED — removed from memory but still installed.
    REMOVED — permanently unregistered.
    """

    DISCOVERED = "DISCOVERED"
    VALIDATED = "VALIDATED"
    INSTALLED = "INSTALLED"
    LOADED = "LOADED"
    INITIALIZED = "INITIALIZED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    UNLOADED = "UNLOADED"
    REMOVED = "REMOVED"


class PluginDomain(StrEnum):
    """Enterprise plugin domains.

    Each plugin operates within a specific domain. Future domains
    can be added without architecture changes by extending this
    enum.
    """

    SYSTEM = "SYSTEM"
    ENERGY = "ENERGY"
    HEALTHCARE = "HEALTHCARE"
    FINANCE = "FINANCE"
    MANUFACTURING = "MANUFACTURING"
    CUSTOMER = "CUSTOMER"
    GENERAL = "GENERAL"
