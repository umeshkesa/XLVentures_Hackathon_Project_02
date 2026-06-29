"""Tests for Plugin Manager Phase 1 — Architecture, Contracts & Models.

Tests cover all enums, domain models, DTOs, events, exceptions,
and interfaces. No loading or execution logic is tested.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from adip.plugins.contracts.events import (
    EventVersion,
    PluginActivated,
    PluginDiscovered,
    PluginEvent,
    PluginInstalled,
    PluginLoaded,
    PluginRemoved,
    PluginSuspended,
    PluginUnloaded,
    PluginValidated,
    SandboxCreated,
    SandboxDestroyed,
)
from adip.plugins.contracts.exceptions import (
    PluginDependencyException,
    PluginException,
    PluginLoadException,
    PluginValidationException,
    SandboxException,
)
from adip.plugins.contracts.models import (
    Plugin,
    PluginCapability,
    PluginConfiguration,
    PluginDecision,
    PluginDependency,
    PluginHealth,
    PluginManifest,
    PluginMetadata,
    PluginMetrics,
    PluginNamespace,
    PluginPolicy,
    PluginSandbox,
    PluginSession,
)
from adip.plugins.dtos import (
    PluginDiscoveryDTO,
    PluginInstallDTO,
    PluginRequestDTO,
    PluginResponseDTO,
    PluginSandboxDTO,
)
from adip.plugins.enums import (
    PluginDomain,
    PluginLifecycleStatus,
    PluginType,
)

# ═════════════════════════════════════════════════════════════════════════════
# Enums
# ═════════════════════════════════════════════════════════════════════════════

class TestPluginType:
    def test_values(self) -> None:
        assert PluginType.DOMAIN == "DOMAIN"
        assert PluginType.AGENT == "AGENT"
        assert PluginType.TOOL == "TOOL"
        assert PluginType.KNOWLEDGE == "KNOWLEDGE"
        assert PluginType.RULE == "RULE"
        assert PluginType.WORKFLOW == "WORKFLOW"
        assert PluginType.ACTION == "ACTION"

    def test_all_members(self) -> None:
        assert len(PluginType) == 7

    def test_member_access(self) -> None:
        assert PluginType("DOMAIN") == PluginType.DOMAIN
        assert PluginType("AGENT") == PluginType.AGENT


class TestPluginLifecycleStatus:
    def test_values(self) -> None:
        assert PluginLifecycleStatus.DISCOVERED == "DISCOVERED"
        assert PluginLifecycleStatus.VALIDATED == "VALIDATED"
        assert PluginLifecycleStatus.INSTALLED == "INSTALLED"
        assert PluginLifecycleStatus.LOADED == "LOADED"
        assert PluginLifecycleStatus.INITIALIZED == "INITIALIZED"
        assert PluginLifecycleStatus.ACTIVE == "ACTIVE"
        assert PluginLifecycleStatus.SUSPENDED == "SUSPENDED"
        assert PluginLifecycleStatus.UNLOADED == "UNLOADED"
        assert PluginLifecycleStatus.REMOVED == "REMOVED"

    def test_all_members(self) -> None:
        assert len(PluginLifecycleStatus) == 9

    def test_lifecycle_order(self) -> None:
        statuses = list(PluginLifecycleStatus)
        assert statuses.index(PluginLifecycleStatus.DISCOVERED) < statuses.index(PluginLifecycleStatus.VALIDATED)
        assert statuses.index(PluginLifecycleStatus.VALIDATED) < statuses.index(PluginLifecycleStatus.INSTALLED)
        assert statuses.index(PluginLifecycleStatus.INSTALLED) < statuses.index(PluginLifecycleStatus.LOADED)
        assert statuses.index(PluginLifecycleStatus.LOADED) < statuses.index(PluginLifecycleStatus.INITIALIZED)
        assert statuses.index(PluginLifecycleStatus.INITIALIZED) < statuses.index(PluginLifecycleStatus.ACTIVE)


class TestPluginDomain:
    def test_values(self) -> None:
        assert PluginDomain.SYSTEM == "SYSTEM"
        assert PluginDomain.ENERGY == "ENERGY"
        assert PluginDomain.HEALTHCARE == "HEALTHCARE"
        assert PluginDomain.FINANCE == "FINANCE"
        assert PluginDomain.MANUFACTURING == "MANUFACTURING"
        assert PluginDomain.CUSTOMER == "CUSTOMER"
        assert PluginDomain.GENERAL == "GENERAL"

    def test_all_members(self) -> None:
        assert len(PluginDomain) == 7

    def test_member_access(self) -> None:
        assert PluginDomain("ENERGY") == PluginDomain.ENERGY
        assert PluginDomain("SYSTEM") == PluginDomain.SYSTEM


# ═════════════════════════════════════════════════════════════════════════════
# Domain Models
# ═════════════════════════════════════════════════════════════════════════════

class TestPluginCapability:
    def test_defaults(self) -> None:
        cap = PluginCapability()
        assert cap.name == ""
        assert cap.description == ""
        assert cap.version == "1.0.0"
        assert cap.dependencies == []
        assert cap.category == ""
        assert cap.visibility == "public"
        assert cap.metadata == {}

    def test_custom_values(self) -> None:
        cap = PluginCapability(
            name="weather-forecast",
            description="Provides weather forecast data",
            version="2.0.0",
            dependencies=["data-fetch"],
            category="data",
            visibility="public",
            metadata={"provider": "openweather"},
        )
        assert cap.name == "weather-forecast"
        assert cap.version == "2.0.0"
        assert len(cap.dependencies) == 1
        assert cap.category == "data"
        assert cap.metadata["provider"] == "openweather"

    def test_uuid_generated(self) -> None:
        cap = PluginCapability()
        assert isinstance(cap.capability_id, uuid.UUID)


class TestPluginDependency:
    def test_defaults(self) -> None:
        dep = PluginDependency()
        assert dep.plugin_id == ""
        assert dep.plugin_name == ""
        assert dep.version_constraint == ">=1.0.0"
        assert dep.optional is False
        assert dep.required is True
        assert dep.status == "pending"

    def test_is_required(self) -> None:
        req = PluginDependency(required=True, optional=False)
        assert req.is_required is True
        opt = PluginDependency(required=False, optional=True)
        assert opt.is_required is False

    def test_custom_values(self) -> None:
        dep = PluginDependency(
            plugin_id="plugin-123",
            plugin_name="data-fetcher",
            version_constraint=">=2.0.0 <3.0.0",
            optional=True,
            required=False,
            status="satisfied",
        )
        assert dep.plugin_id == "plugin-123"
        assert dep.plugin_name == "data-fetcher"
        assert dep.version_constraint == ">=2.0.0 <3.0.0"
        assert dep.optional is True
        assert dep.is_required is False
        assert dep.status == "satisfied"

    def test_uuid_generated(self) -> None:
        dep = PluginDependency()
        assert isinstance(dep.dependency_id, uuid.UUID)


class TestPluginManifest:
    def test_defaults(self) -> None:
        manifest = PluginManifest(plugin_type=PluginType.DOMAIN)
        assert manifest.plugin_name == ""
        assert manifest.plugin_version == "1.0.0"
        assert manifest.plugin_type == PluginType.DOMAIN
        assert manifest.plugin_domain == PluginDomain.GENERAL
        assert manifest.description == ""
        assert manifest.author == ""
        assert manifest.entry_point == ""
        assert manifest.capabilities == []
        assert manifest.dependencies == []

    def test_custom_values(self) -> None:
        cap = PluginCapability(name="search", category="data")
        dep = PluginDependency(plugin_name="base-tools")
        manifest = PluginManifest(
            plugin_name="energy-optimizer",
            plugin_version="2.1.0",
            plugin_type=PluginType.DOMAIN,
            plugin_domain=PluginDomain.ENERGY,
            description="Optimises energy consumption",
            author="ADIP Team",
            entry_point="plugins.energy.main",
            capabilities=[cap],
            dependencies=[dep],
            tags=["energy", "optimisation"],
        )
        assert manifest.plugin_name == "energy-optimizer"
        assert manifest.plugin_version == "2.1.0"
        assert manifest.plugin_type == PluginType.DOMAIN
        assert manifest.plugin_domain == PluginDomain.ENERGY
        assert len(manifest.capabilities) == 1
        assert len(manifest.dependencies) == 1
        assert len(manifest.tags) == 2

    def test_uuid_generated(self) -> None:
        manifest = PluginManifest(plugin_type=PluginType.TOOL)
        assert isinstance(manifest.manifest_id, uuid.UUID)


class TestPluginMetadata:
    def test_defaults(self) -> None:
        meta = PluginMetadata()
        assert meta.installed_at is None
        assert meta.loaded_at is None
        assert meta.activated_at is None
        assert meta.last_error == ""
        assert meta.error_count == 0
        assert meta.load_count == 0
        assert meta.total_executions == 0
        assert meta.custom == {}

    def test_custom_values(self) -> None:
        now = datetime.now(UTC)
        meta = PluginMetadata(
            installed_at=now,
            loaded_at=now,
            activated_at=now,
            last_error="None",
            error_count=2,
            load_count=5,
            total_executions=100,
            custom={"region": "us-east"},
        )
        assert meta.installed_at == now
        assert meta.error_count == 2
        assert meta.load_count == 5
        assert meta.custom["region"] == "us-east"


class TestPlugin:
    def test_defaults(self) -> None:
        plugin = Plugin()
        assert plugin.name == ""
        assert plugin.version == "1.0.0"
        assert plugin.plugin_type == PluginType.DOMAIN
        assert plugin.domain == PluginDomain.GENERAL
        assert plugin.status == PluginLifecycleStatus.DISCOVERED
        assert plugin.enabled is True
        assert plugin.namespace == "default"
        assert isinstance(plugin.metadata, PluginMetadata)

    def test_custom_values(self) -> None:
        manifest = PluginManifest(plugin_type=PluginType.DOMAIN)
        plugin = Plugin(
            name="energy-monitor",
            version="2.0.0",
            plugin_type=PluginType.TOOL,
            domain=PluginDomain.ENERGY,
            status=PluginLifecycleStatus.INSTALLED,
            manifest=manifest,
            enabled=True,
            tags=["monitoring"],
            namespace="energy",
            owner_id="user-1",
        )
        assert plugin.name == "energy-monitor"
        assert plugin.version == "2.0.0"
        assert plugin.plugin_type == PluginType.TOOL
        assert plugin.domain == PluginDomain.ENERGY
        assert plugin.status == PluginLifecycleStatus.INSTALLED
        assert plugin.manifest is not None
        assert plugin.namespace == "energy"

    def test_uuid_generated(self) -> None:
        plugin = Plugin()
        assert isinstance(plugin.plugin_id, uuid.UUID)

    def test_timestamps(self) -> None:
        plugin = Plugin()
        assert isinstance(plugin.created_at, datetime)
        assert isinstance(plugin.updated_at, datetime)


class TestPluginConfiguration:
    def test_defaults(self) -> None:
        plugin = Plugin()
        config = PluginConfiguration(plugin_id=plugin.plugin_id)
        assert config.settings == {}
        assert config.environment == "production"
        assert config.version == 1
        assert config.enabled is True

    def test_custom_values(self) -> None:
        plugin = Plugin()
        config = PluginConfiguration(
            plugin_id=plugin.plugin_id,
            settings={"api_key": "***", "endpoint": "https://api.example.com"},
            environment="staging",
            version=3,
            enabled=True,
        )
        assert config.settings["endpoint"] == "https://api.example.com"
        assert config.environment == "staging"
        assert config.version == 3

    def test_version_constraint(self) -> None:
        plugin = Plugin()
        with pytest.raises(ValidationError):
            PluginConfiguration(plugin_id=plugin.plugin_id, version=0)


class TestPluginNamespace:
    def test_defaults(self) -> None:
        plugin = Plugin()
        ns = PluginNamespace(plugin_id=plugin.plugin_id)
        assert ns.name == ""
        assert ns.memory_namespace == ""
        assert ns.knowledge_namespace == ""
        assert ns.rule_namespace == ""
        assert ns.action_namespace == ""
        assert ns.capability_namespace == ""
        assert ns.enabled is True

    def test_custom_values(self) -> None:
        plugin = Plugin()
        ns = PluginNamespace(
            plugin_id=plugin.plugin_id,
            name="energy",
            memory_namespace="plugin_energy_mem",
            knowledge_namespace="plugin_energy_know",
            rule_namespace="plugin_energy_rules",
            action_namespace="plugin_energy_actions",
            capability_namespace="plugin_energy_caps",
        )
        assert ns.name == "energy"
        assert ns.memory_namespace == "plugin_energy_mem"
        assert ns.rule_namespace == "plugin_energy_rules"

    def test_uuid_generated(self) -> None:
        plugin = Plugin()
        ns = PluginNamespace(plugin_id=plugin.plugin_id)
        assert isinstance(ns.namespace_id, uuid.UUID)


class TestPluginSandbox:
    def test_defaults(self) -> None:
        plugin = Plugin()
        sandbox = PluginSandbox(plugin_id=plugin.plugin_id)
        assert sandbox.namespace == ""
        assert sandbox.domain == PluginDomain.GENERAL
        assert sandbox.configuration == {}
        assert sandbox.resource_limits == {}
        assert sandbox.permissions == []
        assert sandbox.isolation_policy == "strict"
        assert sandbox.enabled is True

    def test_custom_values(self) -> None:
        plugin = Plugin()
        sandbox = PluginSandbox(
            plugin_id=plugin.plugin_id,
            namespace="energy",
            domain=PluginDomain.ENERGY,
            configuration={"timeout": 30},
            memory_namespace="plugin_energy_mem",
            knowledge_namespace="plugin_energy_know",
            rule_namespace="plugin_energy_rules",
            action_namespace="plugin_energy_actions",
            capability_namespace="plugin_energy_caps",
            resource_limits={"cpu": 2, "memory_mb": 512},
            permissions=["network", "filesystem_read"],
            isolation_policy="strict",
        )
        assert sandbox.namespace == "energy"
        assert sandbox.domain == PluginDomain.ENERGY
        assert sandbox.resource_limits["cpu"] == 2
        assert sandbox.permissions[0] == "network"
        assert sandbox.isolation_policy == "strict"

    def test_uuid_generated(self) -> None:
        plugin = Plugin()
        sandbox = PluginSandbox(plugin_id=plugin.plugin_id)
        assert isinstance(sandbox.sandbox_id, uuid.UUID)


class TestPluginPolicy:
    def test_defaults(self) -> None:
        plugin = Plugin()
        policy = PluginPolicy(plugin_id=plugin.plugin_id)
        assert policy.name == ""
        assert policy.allowed_capabilities == []
        assert policy.denied_capabilities == []
        assert policy.allowed_domains == []
        assert policy.network_access is False
        assert policy.filesystem_access is False
        assert policy.version == 1

    def test_custom_values(self) -> None:
        plugin = Plugin()
        policy = PluginPolicy(
            plugin_id=plugin.plugin_id,
            name="Energy REST Policy",
            description="Restricts energy plugin to read-only data access",
            allowed_capabilities=["read_sensor", "query_history"],
            denied_capabilities=["write_config"],
            allowed_domains=[PluginDomain.ENERGY],
            network_access=True,
            filesystem_access=False,
            version=2,
        )
        assert policy.name == "Energy REST Policy"
        assert len(policy.allowed_capabilities) == 2
        assert len(policy.allowed_domains) == 1
        assert policy.network_access is True
        assert policy.version == 2

    def test_version_constraint(self) -> None:
        plugin = Plugin()
        with pytest.raises(ValidationError):
            PluginPolicy(plugin_id=plugin.plugin_id, version=0)

    def test_uuid_generated(self) -> None:
        plugin = Plugin()
        policy = PluginPolicy(plugin_id=plugin.plugin_id)
        assert isinstance(policy.policy_id, uuid.UUID)


class TestPluginDecision:
    def test_defaults(self) -> None:
        plugin = Plugin()
        decision = PluginDecision(plugin_id=plugin.plugin_id)
        assert decision.decision == ""
        assert decision.reason == ""
        assert decision.decided_by == ""

    def test_custom_values(self) -> None:
        plugin = Plugin()
        decision = PluginDecision(
            plugin_id=plugin.plugin_id,
            decision="approve",
            reason="All dependencies satisfied and policy compliant",
            decided_by="admin-1",
        )
        assert decision.decision == "approve"
        assert "dependencies satisfied" in decision.reason
        assert decision.decided_by == "admin-1"

    def test_uuid_generated(self) -> None:
        plugin = Plugin()
        decision = PluginDecision(plugin_id=plugin.plugin_id)
        assert isinstance(decision.decision_id, uuid.UUID)


class TestPluginHealth:
    def test_defaults(self) -> None:
        plugin = Plugin()
        health = PluginHealth(plugin_id=plugin.plugin_id)
        assert health.overall_status == "UNKNOWN"
        assert health.discovery_status == "UNKNOWN"
        assert health.validation_status == "UNKNOWN"
        assert health.loader_status == "UNKNOWN"
        assert health.dependency_resolver_status == "UNKNOWN"
        assert health.sandbox_status == "UNKNOWN"
        assert health.compatibility_status == "UNKNOWN"
        assert health.lifecycle_status == "UNKNOWN"
        assert health.capability_status == "UNKNOWN"
        assert health.error_count == 0
        assert health.error_rate == 0.0
        assert health.average_load_time_ms == 0.0
        assert health.active_plugins == 0
        assert health.uptime_seconds == 0.0

    def test_custom_values(self) -> None:
        plugin = Plugin()
        health = PluginHealth(
            plugin_id=plugin.plugin_id,
            plugin_name="energy-monitor",
            overall_status="HEALTHY",
            discovery_status="HEALTHY",
            validation_status="HEALTHY",
            loader_status="HEALTHY",
            sandbox_status="HEALTHY",
            compatibility_status="HEALTHY",
            lifecycle_status="HEALTHY",
            capability_status="HEALTHY",
            uptime_seconds=86400.0,
            error_count=0,
            total_executions=1000,
        )
        assert health.overall_status == "HEALTHY"
        assert health.plugin_name == "energy-monitor"
        assert health.uptime_seconds == 86400.0
        assert health.total_executions == 1000

    def test_is_healthy(self) -> None:
        plugin = Plugin()
        healthy = PluginHealth(plugin_id=plugin.plugin_id, overall_status="HEALTHY")
        assert healthy.is_healthy() is True
        degraded = PluginHealth(plugin_id=plugin.plugin_id, overall_status="DEGRADED")
        assert degraded.is_healthy() is False


class TestPluginMetrics:
    def test_defaults(self) -> None:
        plugin = Plugin()
        metrics = PluginMetrics(plugin_id=plugin.plugin_id)
        assert metrics.executions_total == 0
        assert metrics.executions_success == 0
        assert metrics.executions_failed == 0
        assert metrics.average_execution_time_ms == 0.0
        assert metrics.errors_total == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0

    def test_custom_values(self) -> None:
        plugin = Plugin()
        metrics = PluginMetrics(
            plugin_id=plugin.plugin_id,
            plugin_name="energy-monitor",
            executions_total=500,
            executions_success=480,
            executions_failed=20,
            average_execution_time_ms=15.5,
            errors_total=5,
            cache_hits=200,
            cache_misses=50,
        )
        assert metrics.plugin_name == "energy-monitor"
        assert metrics.executions_total == 500
        assert metrics.average_execution_time_ms == 15.5
        assert metrics.cache_hits == 200


class TestPluginSession:
    def test_defaults(self) -> None:
        plugin = Plugin()
        session = PluginSession(plugin_id=plugin.plugin_id)
        assert session.status == "PENDING"
        assert session.inputs == {}
        assert session.outputs == {}
        assert session.error_message == ""
        assert session.completed_at is None
        assert session.duration_ms == 0.0

    def test_custom_values(self) -> None:
        plugin = Plugin()
        now = datetime.now(UTC)
        session = PluginSession(
            plugin_id=plugin.plugin_id,
            capability_id=uuid.uuid4(),
            user_id="operator-1",
            correlation_id="corr-123",
            inputs={"query": "forecast"},
            outputs={"result": "sunny"},
            status="COMPLETED",
            started_at=now,
            completed_at=now,
            duration_ms=150.5,
        )
        assert session.user_id == "operator-1"
        assert session.correlation_id == "corr-123"
        assert session.inputs["query"] == "forecast"
        assert session.status == "COMPLETED"
        assert session.duration_ms == 150.5

    def test_uuid_generated(self) -> None:
        plugin = Plugin()
        session = PluginSession(plugin_id=plugin.plugin_id)
        assert isinstance(session.session_id, uuid.UUID)

    def test_capability_id_optional(self) -> None:
        plugin = Plugin()
        session = PluginSession(plugin_id=plugin.plugin_id)
        assert session.capability_id is None


# ═════════════════════════════════════════════════════════════════════════════
# Events
# ═════════════════════════════════════════════════════════════════════════════

class TestEventVersion:
    def test_version_string(self) -> None:
        assert EventVersion == "1.0.0"


class TestPluginEvent:
    def test_defaults(self) -> None:
        event = PluginDiscovered(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
        )
        assert event.domain == PluginDomain.GENERAL
        assert event.correlation_id == ""
        assert event.payload == {}
        assert isinstance(event.timestamp, datetime)

    def test_custom_values(self) -> None:
        event = PluginDiscovered(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.TOOL,
            domain=PluginDomain.ENERGY,
            correlation_id="corr-789",
            payload={"source": "registry"},
        )
        assert event.domain == PluginDomain.ENERGY
        assert event.correlation_id == "corr-789"
        assert event.payload["source"] == "registry"

    def test_uuid_generated(self) -> None:
        event = PluginDiscovered(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
        )
        assert isinstance(event.event_id, uuid.UUID)


class TestPluginDiscovered:
    def test_defaults(self) -> None:
        event = PluginDiscovered(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
        )
        assert event.discovery_source == ""

    def test_custom_source(self) -> None:
        event = PluginDiscovered(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            discovery_source="filesystem",
        )
        assert event.discovery_source == "filesystem"


class TestPluginValidated:
    def test_custom_results(self) -> None:
        event = PluginValidated(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.AGENT,
            validation_results=["manifest_valid", "dependencies_satisfied"],
        )
        assert len(event.validation_results) == 2


class TestPluginInstalled:
    def test_defaults(self) -> None:
        event = PluginInstalled(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.TOOL,
        )
        assert event.version == "1.0.0"

    def test_custom_version(self) -> None:
        event = PluginInstalled(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            version="2.0.0",
        )
        assert event.version == "2.0.0"


class TestPluginLoaded:
    def test_defaults(self) -> None:
        event = PluginLoaded(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
        )
        assert event.load_time_ms == 0.0

    def test_custom_load_time(self) -> None:
        event = PluginLoaded(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            load_time_ms=45.2,
        )
        assert event.load_time_ms == 45.2


class TestPluginActivated:
    def test_custom_values(self) -> None:
        event = PluginActivated(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.WORKFLOW,
            previous_status=PluginLifecycleStatus.LOADED,
        )
        assert event.previous_status == PluginLifecycleStatus.LOADED


class TestPluginSuspended:
    def test_custom_values(self) -> None:
        event = PluginSuspended(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            reason="Resource quota exceeded",
        )
        assert event.reason == "Resource quota exceeded"


class TestPluginUnloaded:
    def test_custom_values(self) -> None:
        event = PluginUnloaded(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            unload_reason="Plugin update in progress",
        )
        assert event.unload_reason == "Plugin update in progress"


class TestPluginRemoved:
    def test_custom_values(self) -> None:
        event = PluginRemoved(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            removal_reason="Manual removal by admin",
        )
        assert event.removal_reason == "Manual removal by admin"


class TestSandboxCreated:
    def test_custom_values(self) -> None:
        sandbox_id = uuid.uuid4()
        event = SandboxCreated(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            sandbox_id=sandbox_id,
            namespace="energy",
        )
        assert event.sandbox_id == sandbox_id
        assert event.namespace == "energy"


class TestSandboxDestroyed:
    def test_custom_values(self) -> None:
        sandbox_id = uuid.uuid4()
        event = SandboxDestroyed(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            sandbox_id=sandbox_id,
            reason="Plugin uninstalled",
        )
        assert event.sandbox_id == sandbox_id
        assert event.reason == "Plugin uninstalled"

    def test_inheritance(self) -> None:
        event = SandboxDestroyed(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.TOOL,
            sandbox_id=uuid.uuid4(),
        )
        assert isinstance(event, PluginEvent)


# ═════════════════════════════════════════════════════════════════════════════
# DTOs
# ═════════════════════════════════════════════════════════════════════════════

class TestPluginRequestDTO:
    def test_defaults(self) -> None:
        dto = PluginRequestDTO()
        assert dto.name == ""
        assert dto.version == "1.0.0"
        assert dto.plugin_type == PluginType.DOMAIN
        assert dto.domain == PluginDomain.GENERAL
        assert dto.namespace == "default"

    def test_custom_values(self) -> None:
        dto = PluginRequestDTO(
            name="energy-optimizer",
            version="2.0.0",
            plugin_type=PluginType.TOOL,
            domain=PluginDomain.ENERGY,
            owner_id="user-1",
            namespace="energy",
            tags=["energy", "optimisation"],
        )
        assert dto.name == "energy-optimizer"
        assert dto.plugin_type == PluginType.TOOL
        assert dto.domain == PluginDomain.ENERGY
        assert len(dto.tags) == 2


class TestPluginResponseDTO:
    def test_defaults(self) -> None:
        now = datetime.now(UTC)
        dto = PluginResponseDTO(
            plugin_id=uuid.uuid4(),
            plugin_type=PluginType.DOMAIN,
            created_at=now,
            updated_at=now,
        )
        assert dto.name == ""
        assert dto.version == "1.0.0"
        assert dto.domain == PluginDomain.GENERAL
        assert dto.status == PluginLifecycleStatus.DISCOVERED
        assert dto.enabled is True

    def test_custom_values(self) -> None:
        now = datetime.now(UTC)
        dto = PluginResponseDTO(
            plugin_id=uuid.uuid4(),
            name="active-plugin",
            version="3.0.0",
            plugin_type=PluginType.AGENT,
            domain=PluginDomain.HEALTHCARE,
            status=PluginLifecycleStatus.ACTIVE,
            enabled=True,
            created_at=now,
            updated_at=now,
        )
        assert dto.name == "active-plugin"
        assert dto.status == PluginLifecycleStatus.ACTIVE
        assert dto.domain == PluginDomain.HEALTHCARE


class TestPluginInstallDTO:
    def test_defaults(self) -> None:
        dto = PluginInstallDTO()
        assert dto.source == ""
        assert dto.name == ""
        assert dto.version == "1.0.0"
        assert dto.plugin_type == PluginType.DOMAIN
        assert dto.domain == PluginDomain.GENERAL
        assert dto.namespace == "default"

    def test_custom_values(self) -> None:
        dto = PluginInstallDTO(
            source="/path/to/plugin.zip",
            name="energy-monitor",
            version="1.5.0",
            plugin_type=PluginType.TOOL,
            domain=PluginDomain.ENERGY,
            namespace="energy",
            config={"api_key": "test123"},
        )
        assert dto.source == "/path/to/plugin.zip"
        assert dto.version == "1.5.0"
        assert dto.config["api_key"] == "test123"


class TestPluginDiscoveryDTO:
    def test_defaults(self) -> None:
        dto = PluginDiscoveryDTO()
        assert dto.name == ""
        assert dto.version == ""
        assert dto.plugin_type is None
        assert dto.domain == PluginDomain.GENERAL
        assert dto.source == ""

    def test_custom_values(self) -> None:
        dto = PluginDiscoveryDTO(
            name="energy-optimizer",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            domain=PluginDomain.ENERGY,
            source="/discovered/plugins/energy",
        )
        assert dto.name == "energy-optimizer"
        assert dto.plugin_type == PluginType.DOMAIN
        assert dto.source == "/discovered/plugins/energy"


class TestPluginSandboxDTO:
    def test_defaults(self) -> None:
        plugin = Plugin()
        dto = PluginSandboxDTO(plugin_id=plugin.plugin_id)
        assert dto.namespace == ""
        assert dto.domain == PluginDomain.GENERAL
        assert dto.resource_limits == {}
        assert dto.permissions == []
        assert dto.isolation_policy == "strict"

    def test_custom_values(self) -> None:
        plugin = Plugin()
        dto = PluginSandboxDTO(
            plugin_id=plugin.plugin_id,
            namespace="energy",
            domain=PluginDomain.ENERGY,
            resource_limits={"cpu": 4, "memory_mb": 1024},
            permissions=["network", "filesystem"],
            isolation_policy="moderate",
        )
        assert dto.namespace == "energy"
        assert dto.resource_limits["cpu"] == 4
        assert dto.isolation_policy == "moderate"


# ═════════════════════════════════════════════════════════════════════════════
# Exceptions
# ═════════════════════════════════════════════════════════════════════════════

class TestPluginException:
    def test_default_message(self) -> None:
        exc = PluginException()
        assert str(exc) == "Plugin error"

    def test_custom_message(self) -> None:
        exc = PluginException("Custom error")
        assert str(exc) == "Custom error"

    def test_inheritance(self) -> None:
        assert issubclass(PluginException, Exception)


class TestPluginValidationException:
    def test_default_message(self) -> None:
        exc = PluginValidationException()
        assert str(exc) == "Plugin validation error"

    def test_inheritance(self) -> None:
        assert issubclass(PluginValidationException, PluginException)


class TestPluginDependencyException:
    def test_default_message(self) -> None:
        exc = PluginDependencyException()
        assert str(exc) == "Plugin dependency error"

    def test_with_ids(self) -> None:
        exc = PluginDependencyException(plugin_id="plugin-1", dependency_id="dep-1")
        assert "plugin-1" in str(exc)
        assert "dep-1" in str(exc)

    def test_inheritance(self) -> None:
        assert issubclass(PluginDependencyException, PluginException)


class TestPluginLoadException:
    def test_default_message(self) -> None:
        exc = PluginLoadException()
        assert str(exc) == "Plugin load failed"

    def test_with_id(self) -> None:
        exc = PluginLoadException(plugin_id="plugin-1")
        assert "plugin-1" in str(exc)

    def test_inheritance(self) -> None:
        assert issubclass(PluginLoadException, PluginException)


class TestSandboxException:
    def test_default_message(self) -> None:
        exc = SandboxException()
        assert str(exc) == "Sandbox error"

    def test_with_id(self) -> None:
        exc = SandboxException(sandbox_id="sandbox-1")
        assert "sandbox-1" in str(exc)

    def test_inheritance(self) -> None:
        assert issubclass(SandboxException, PluginException)


# ═════════════════════════════════════════════════════════════════════════════
# Backward Compatibility & General Validation
# ═════════════════════════════════════════════════════════════════════════════

class TestModelConstraints:
    def test_plugin_config_version_must_be_positive(self) -> None:
        plugin = Plugin()
        with pytest.raises(ValidationError):
            PluginConfiguration(plugin_id=plugin.plugin_id, version=-1)

    def test_policy_version_must_be_positive(self) -> None:
        plugin = Plugin()
        with pytest.raises(ValidationError):
            PluginPolicy(plugin_id=plugin.plugin_id, version=0)

    def test_health_error_count_non_negative(self) -> None:
        plugin = Plugin()
        with pytest.raises(ValidationError):
            PluginHealth(plugin_id=plugin.plugin_id, error_count=-1)

    def test_metrics_executions_non_negative(self) -> None:
        plugin = Plugin()
        with pytest.raises(ValidationError):
            PluginMetrics(plugin_id=plugin.plugin_id, executions_total=-1)

    def test_session_duration_non_negative(self) -> None:
        plugin = Plugin()
        with pytest.raises(ValidationError):
            PluginSession(plugin_id=plugin.plugin_id, duration_ms=-1.0)

    def test_metadata_error_count_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            PluginMetadata(error_count=-1)
