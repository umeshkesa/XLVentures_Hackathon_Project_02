"""Phase 1 validation tests for the Registry Framework.

Tests cover enums, models, events, exceptions, DTOs, interfaces,
BaseRegistry, and imports — no implementation logic is tested.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from adip.registry import (
    # Interfaces
    BaseRegistry,
    EntryActivated,
    EntryDeprecated,
    EntryRegistered,
    EntryRemoved,
    EntryUpdated,
    EntryValidated,
    RegistryCache,
    RegistryConflictException,
    RegistryCoordinator,
    RegistryDecision,
    # Models
    RegistryEntry,
    # Events
    RegistryEvent,
    # Exceptions
    RegistryException,
    RegistryFilter,
    RegistryHealth,
    RegistryHealthChecker,
    RegistryLifecycleManager,
    RegistryManager,
    RegistryMetadata,
    RegistryMetrics,
    RegistryNamespace,
    RegistryRegistrationDTO,
    # DTOs
    RegistryRequestDTO,
    RegistryResponseDTO,
    RegistryScope,
    RegistrySearchDTO,
    RegistrySearcher,
    RegistrySearchException,
    RegistrySearchResult,
    RegistryService,
    RegistrySession,
    # Enums
    RegistryType,
    RegistryValidationException,
    RegistryValidator,
    RegistryVersion,
    RegistryVersionManager,
)
from adip.registry.contracts.events import EventVersion
from adip.registry.enums import RegistryLifecycleStatus as RLS

# ===================================================================
# Enums
# ===================================================================

class TestRegistryType:
    def test_values(self) -> None:
        assert RegistryType.CAPABILITY == "CAPABILITY"
        assert RegistryType.AGENT == "AGENT"
        assert RegistryType.TOOL == "TOOL"
        assert RegistryType.RULE == "RULE"
        assert RegistryType.PLUGIN == "PLUGIN"
        assert RegistryType.WORKFLOW == "WORKFLOW"

    def test_six_values(self) -> None:
        values = list(RegistryType)
        assert len(values) == 6

    def test_str_enum(self) -> None:
        assert str(RegistryType.CAPABILITY) == "CAPABILITY"

    def test_from_string(self) -> None:
        assert RegistryType("CAPABILITY") == RegistryType.CAPABILITY
        assert RegistryType("AGENT") == RegistryType.AGENT


class TestRegistryLifecycleStatus:
    def test_values(self) -> None:
        assert RLS.REGISTERED == "REGISTERED"
        assert RLS.VALIDATED == "VALIDATED"
        assert RLS.ACTIVE == "ACTIVE"
        assert RLS.SUSPENDED == "SUSPENDED"
        assert RLS.DEPRECATED == "DEPRECATED"
        assert RLS.REMOVED == "REMOVED"

    def test_six_values(self) -> None:
        values = list(RLS)
        assert len(values) == 6

    def test_str_enum(self) -> None:
        assert str(RLS.REGISTERED) == "REGISTERED"



class TestRegistryScope:
    def test_values(self) -> None:
        assert RegistryScope.GLOBAL == "GLOBAL"
        assert RegistryScope.SYSTEM == "SYSTEM"
        assert RegistryScope.DOMAIN == "DOMAIN"
        assert RegistryScope.PLUGIN == "PLUGIN"
        assert RegistryScope.TENANT == "TENANT"
        assert RegistryScope.USER == "USER"

    def test_six_values(self) -> None:
        values = list(RegistryScope)
        assert len(values) == 6

    def test_str_enum(self) -> None:
        assert str(RegistryScope.GLOBAL) == "GLOBAL"


# ===================================================================
# Models — RegistryEntry
# ===================================================================

class TestRegistryEntry:
    def test_defaults(self) -> None:
        entry = RegistryEntry()
        assert entry.name == ""
        assert entry.version == "1.0.0"
        assert entry.registry_type == RegistryType.CAPABILITY
        assert entry.scope == RegistryScope.GLOBAL
        assert entry.status == RLS.REGISTERED
        assert entry.namespace == "default"
        assert entry.tags == []
        assert entry.metadata == {}

    def test_with_values(self) -> None:
        entry = RegistryEntry(
            name="energy-capability",
            version="2.1.0",
            registry_type=RegistryType.AGENT,
            scope=RegistryScope.DOMAIN,
            owner_id="user-001",
            namespace="energy",
            tags=["energy", "ml"],
        )
        assert entry.name == "energy-capability"
        assert entry.version == "2.1.0"
        assert entry.registry_type == RegistryType.AGENT
        assert entry.scope == RegistryScope.DOMAIN
        assert entry.owner_id == "user-001"
        assert entry.namespace == "energy"
        assert entry.tags == ["energy", "ml"]

    def test_entry_id_generated(self) -> None:
        e1 = RegistryEntry()
        e2 = RegistryEntry()
        assert e1.entry_id != e2.entry_id

    def test_timestamps_generated(self) -> None:
        entry = RegistryEntry()
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.updated_at, datetime)

    def test_serialisation(self) -> None:
        entry = RegistryEntry(name="test")
        data = entry.model_dump()
        assert data["name"] == "test"
        assert data["registry_type"] == "CAPABILITY"
        assert data["scope"] == "GLOBAL"
        assert data["status"] == "REGISTERED"

    def test_deserialisation(self) -> None:
        data: dict[str, Any] = {
            "name": "test-capability",
            "registry_type": "TOOL",
            "status": "ACTIVE",
        }
        entry = RegistryEntry.model_validate(data)
        assert entry.name == "test-capability"
        assert entry.registry_type == RegistryType.TOOL
        assert entry.status == RLS.ACTIVE


# ===================================================================
# Models — RegistryMetadata
# ===================================================================

class TestRegistryMetadata:
    def test_defaults(self) -> None:
        m = RegistryMetadata()
        assert m.description == ""
        assert m.display_name == ""
        assert m.category == ""
        assert m.properties == {}

    def test_with_values(self) -> None:
        m = RegistryMetadata(
            description="Energy forecasting capability",
            display_name="Energy Forecaster",
            category="analytics",
            source="manual",
            documentation_url="https://docs.example.com/energy",
            license="MIT",
            properties={"version": "2.0"},
        )
        assert m.description == "Energy forecasting capability"
        assert m.display_name == "Energy Forecaster"
        assert m.category == "analytics"
        assert m.source == "manual"
        assert m.properties == {"version": "2.0"}


# ===================================================================
# Models — RegistryVersion
# ===================================================================

class TestRegistryVersion:
    def test_defaults(self) -> None:
        v = RegistryVersion(entry_id=uuid.uuid4())
        assert v.version == "1.0.0"
        assert v.previous_version == ""
        assert v.release_notes == ""
        assert v.snapshot == {}

    def test_with_values(self) -> None:
        eid = uuid.uuid4()
        v = RegistryVersion(
            entry_id=eid,
            version="2.0.0",
            previous_version="1.0.0",
            release_notes="Major update",
            snapshot={"name": "test", "version": "2.0.0"},
            created_by="user-001",
        )
        assert v.entry_id == eid
        assert v.version == "2.0.0"
        assert v.previous_version == "1.0.0"
        assert v.release_notes == "Major update"
        assert v.snapshot == {"name": "test", "version": "2.0.0"}
        assert v.created_by == "user-001"

    def test_version_id_generated(self) -> None:
        v1 = RegistryVersion(entry_id=uuid.uuid4())
        v2 = RegistryVersion(entry_id=uuid.uuid4())
        assert v1.version_id != v2.version_id


# ===================================================================
# Models — RegistryHealth
# ===================================================================

class TestRegistryHealth:
    def test_defaults(self) -> None:
        h = RegistryHealth()
        assert h.overall_status == "UNKNOWN"
        assert h.entries_total == 0
        assert h.active_entries == 0
        assert h.error_count == 0
        assert h.uptime_seconds == 0.0

    def test_with_values(self) -> None:
        h = RegistryHealth(
            overall_status="HEALTHY",
            entries_total=100,
            active_entries=75,
            validator_status="HEALTHY",
            searcher_status="HEALTHY",
            error_count=2,
            uptime_seconds=86400.0,
        )
        assert h.overall_status == "HEALTHY"
        assert h.entries_total == 100
        assert h.active_entries == 75
        assert h.validator_status == "HEALTHY"
        assert h.searcher_status == "HEALTHY"
        assert h.error_count == 2
        assert h.uptime_seconds == 86400.0


# ===================================================================
# Models — RegistryMetrics
# ===================================================================

class TestRegistryMetrics:
    def test_defaults(self) -> None:
        m = RegistryMetrics()
        assert m.entries_total == 0
        assert m.registrations_total == 0
        assert m.lookups_total == 0
        assert m.searches_total == 0
        assert m.cache_hits == 0
        assert m.cache_misses == 0
        assert m.errors_total == 0
        assert m.entries_per_scope == {}
        assert m.entries_per_status == {}

    def test_with_values(self) -> None:
        m = RegistryMetrics(
            registry_type=RegistryType.AGENT,
            entries_total=50,
            registrations_total=200,
            deregistrations_total=10,
            lookups_total=5000,
            searches_total=1000,
            active_entries=40,
            cache_hits=4500,
            cache_misses=500,
            errors_total=3,
            entries_per_scope={"GLOBAL": 30, "DOMAIN": 20},
            entries_per_status={"ACTIVE": 40, "REGISTERED": 10},
        )
        assert m.registry_type == RegistryType.AGENT
        assert m.entries_total == 50
        assert m.registrations_total == 200
        assert m.deregistrations_total == 10
        assert m.cache_hits == 4500
        assert m.cache_misses == 500
        assert m.entries_per_scope == {"GLOBAL": 30, "DOMAIN": 20}
        assert m.entries_per_status == {"ACTIVE": 40, "REGISTERED": 10}


# ===================================================================
# Models — RegistrySession
# ===================================================================

class TestRegistrySession:
    def test_defaults(self) -> None:
        s = RegistrySession()
        assert s.operation == ""
        assert s.namespace == "default"
        assert s.correlation_id == ""
        assert s.entries_affected == []
        assert s.status == "ACTIVE"
        assert s.metadata == {}

    def test_with_values(self) -> None:
        eids = ["entry-001", "entry-002"]
        s = RegistrySession(
            registry_type=RegistryType.PLUGIN,
            operation="bulk_register",
            user_id="admin",
            namespace="production",
            correlation_id="corr-001",
            entries_affected=eids,
            status="COMPLETED",
        )
        assert s.registry_type == RegistryType.PLUGIN
        assert s.operation == "bulk_register"
        assert s.user_id == "admin"
        assert s.namespace == "production"
        assert s.correlation_id == "corr-001"
        assert s.entries_affected == eids
        assert s.status == "COMPLETED"

    def test_completed_at_none_when_active(self) -> None:
        s = RegistrySession()
        assert s.completed_at is None

    def test_completed_at_settable(self) -> None:
        now = datetime.now(UTC)
        s = RegistrySession(completed_at=now)
        assert s.completed_at == now


# ===================================================================
# Models — RegistryDecision
# ===================================================================

class TestRegistryDecision:
    def test_defaults(self) -> None:
        d = RegistryDecision(entry_id=uuid.uuid4())
        assert d.operation == ""
        assert d.allowed is True
        assert d.reasoning == []
        assert d.confidence == 0.0
        assert d.metadata == {}

    def test_with_values(self) -> None:
        eid = uuid.uuid4()
        d = RegistryDecision(
            entry_id=eid,
            operation="register",
            allowed=True,
            reasoning=["Validation passed", "Policy check passed"],
            confidence=0.95,
            validation_results=["Schema OK", "Metadata OK"],
            performed_by="user-001",
        )
        assert d.entry_id == eid
        assert d.operation == "register"
        assert d.allowed is True
        assert len(d.reasoning) == 2
        assert d.confidence == 0.95
        assert d.validation_results == ["Schema OK", "Metadata OK"]
        assert d.performed_by == "user-001"

    def test_decision_id_generated(self) -> None:
        d1 = RegistryDecision(entry_id=uuid.uuid4())
        d2 = RegistryDecision(entry_id=uuid.uuid4())
        assert d1.decision_id != d2.decision_id


# ===================================================================
# Models — RegistrySearchResult
# ===================================================================

class TestRegistrySearchResult:
    def test_defaults(self) -> None:
        entry = RegistryEntry(name="test")
        r = RegistrySearchResult(entry=entry)
        assert r.score == 0.0
        assert r.matched_fields == []
        assert r.rank == 0

    def test_with_values(self) -> None:
        entry = RegistryEntry(name="energy-capability", version="1.0.0")
        r = RegistrySearchResult(
            entry=entry,
            score=0.95,
            matched_fields=["name", "tags"],
            rank=1,
        )
        assert r.entry.name == "energy-capability"
        assert r.score == 0.95
        assert r.matched_fields == ["name", "tags"]
        assert r.rank == 1


# ===================================================================
# Models — RegistryFilter
# ===================================================================

class TestRegistryFilter:
    def test_defaults(self) -> None:
        f = RegistryFilter()
        assert f.registry_type is None
        assert f.scope is None
        assert f.status is None
        assert f.namespace == ""
        assert f.tags == []
        assert f.query == ""
        assert f.limit == 20
        assert f.offset == 0

    def test_with_values(self) -> None:
        f = RegistryFilter(
            registry_type=RegistryType.TOOL,
            scope=RegistryScope.DOMAIN,
            status=RLS.ACTIVE,
            namespace="energy",
            tags=["ml", "inference"],
            query="forecast",
            limit=50,
            offset=10,
        )
        assert f.registry_type == RegistryType.TOOL
        assert f.scope == RegistryScope.DOMAIN
        assert f.status == RLS.ACTIVE
        assert f.namespace == "energy"
        assert f.tags == ["ml", "inference"]
        assert f.query == "forecast"
        assert f.limit == 50
        assert f.offset == 10

    def test_limit_bounds(self) -> None:
        with pytest.raises(Exception):
            RegistryFilter(limit=0)
        with pytest.raises(Exception):
            RegistryFilter(limit=1001)

    def test_offset_negative(self) -> None:
        with pytest.raises(Exception):
            RegistryFilter(offset=-1)


# ===================================================================
# Models — RegistryNamespace
# ===================================================================

class TestRegistryNamespace:
    def test_defaults(self) -> None:
        n = RegistryNamespace(name="default")
        assert n.registry_type == RegistryType.CAPABILITY
        assert n.description == ""
        assert n.scope == RegistryScope.DOMAIN
        assert n.max_entries == 0
        assert n.enabled is True

    def test_with_values(self) -> None:
        n = RegistryNamespace(
            name="energy-prod",
            registry_type=RegistryType.AGENT,
            description="Production energy agents",
            scope=RegistryScope.TENANT,
            allowed_scopes=[RegistryScope.DOMAIN, RegistryScope.TENANT],
            owner_id="team-energy",
            tags=["energy", "production"],
            max_entries=100,
            enabled=True,
        )
        assert n.name == "energy-prod"
        assert n.registry_type == RegistryType.AGENT
        assert n.description == "Production energy agents"
        assert n.scope == RegistryScope.TENANT
        assert RegistryScope.DOMAIN in n.allowed_scopes
        assert n.owner_id == "team-energy"
        assert n.max_entries == 100
        assert n.enabled is True

    def test_namespace_id_generated(self) -> None:
        n1 = RegistryNamespace(name="ns1")
        n2 = RegistryNamespace(name="ns2")
        assert n1.namespace_id != n2.namespace_id


# ===================================================================
# Events
# ===================================================================

class TestRegistryEvent:
    def test_event_version_defined(self) -> None:
        assert EventVersion == "1.0.0"

    def test_base_event_defaults(self) -> None:
        e = RegistryEvent(entry_id=uuid.uuid4(), registry_type=RegistryType.TOOL)
        assert e.scope == RegistryScope.GLOBAL
        assert e.correlation_id == ""
        assert e.payload == {}

    def test_entry_registered(self) -> None:
        eid = uuid.uuid4()
        event = EntryRegistered(
            entry_id=eid,
            registry_type=RegistryType.AGENT,
            version="2.0.0",
            registered_by="user-001",
        )
        assert event.entry_id == eid
        assert event.registry_type == RegistryType.AGENT
        assert event.version == "2.0.0"
        assert event.registered_by == "user-001"

    def test_entry_updated(self) -> None:
        eid = uuid.uuid4()
        event = EntryUpdated(
            entry_id=eid,
            registry_type=RegistryType.PLUGIN,
            previous_version="1.0.0",
            new_version="1.1.0",
            updated_by="user-002",
        )
        assert event.entry_id == eid
        assert event.previous_version == "1.0.0"
        assert event.new_version == "1.1.0"
        assert event.updated_by == "user-002"

    def test_entry_validated(self) -> None:
        event = EntryValidated(
            entry_id=uuid.uuid4(),
            registry_type=RegistryType.RULE,
            validation_results=["Schema OK", "Constraints OK"],
            valid=True,
        )
        assert event.valid is True
        assert len(event.validation_results) == 2

    def test_entry_activated(self) -> None:
        eid = uuid.uuid4()
        event = EntryActivated(
            entry_id=eid,
            registry_type=RegistryType.WORKFLOW,
            previous_status=RLS.VALIDATED,
            activated_by="admin",
        )
        assert event.entry_id == eid
        assert event.previous_status == RLS.VALIDATED
        assert event.activated_by == "admin"

    def test_entry_deprecated(self) -> None:
        eid = uuid.uuid4()
        replacement_id = uuid.uuid4()
        event = EntryDeprecated(
            entry_id=eid,
            registry_type=RegistryType.TOOL,
            reason="Superseded by v2",
            replacement_entry_id=replacement_id,
        )
        assert event.reason == "Superseded by v2"
        assert event.replacement_entry_id == replacement_id

    def test_entry_removed(self) -> None:
        event = EntryRemoved(
            entry_id=uuid.uuid4(),
            registry_type=RegistryType.CAPABILITY,
            reason="End of life",
            removed_by="admin",
        )
        assert event.reason == "End of life"
        assert event.removed_by == "admin"

    def test_event_id_generated(self) -> None:
        e1 = EntryRegistered(entry_id=uuid.uuid4(), registry_type=RegistryType.TOOL)
        e2 = EntryRegistered(entry_id=uuid.uuid4(), registry_type=RegistryType.TOOL)
        assert e1.event_id != e2.event_id


# ===================================================================
# Exceptions
# ===================================================================

class TestRegistryExceptions:
    def test_base_exception(self) -> None:
        e = RegistryException("Test error")
        assert str(e) == "Test error"
        assert e.message == "Test error"

    def test_base_exception_default_message(self) -> None:
        e = RegistryException()
        assert str(e) == "Registry error"

    def test_validation_exception(self) -> None:
        e = RegistryValidationException("Invalid metadata")
        assert str(e) == "Invalid metadata"

    def test_validation_exception_default(self) -> None:
        e = RegistryValidationException()
        assert str(e) == "Registry validation error"

    def test_conflict_exception_with_ids(self) -> None:
        e = RegistryConflictException(entry_id="entry-001", conflicting_entry_id="entry-002")
        assert "entry-001" in str(e)
        assert "entry-002" in str(e)

    def test_conflict_exception_default(self) -> None:
        e = RegistryConflictException()
        assert str(e) == "Registry conflict detected"

    def test_conflict_exception_custom_message(self) -> None:
        e = RegistryConflictException(message="Custom conflict")
        assert str(e) == "Custom conflict"

    def test_search_exception_with_query(self) -> None:
        e = RegistrySearchException(query="forecast*")
        assert "forecast*" in str(e)

    def test_search_exception_default(self) -> None:
        e = RegistrySearchException()
        assert str(e) == "Registry search failed"

    def test_exception_hierarchy(self) -> None:
        assert issubclass(RegistryValidationException, RegistryException)
        assert issubclass(RegistryConflictException, RegistryException)
        assert issubclass(RegistrySearchException, RegistryException)


# ===================================================================
# DTOs
# ===================================================================

class TestRegistryRequestDTO:
    def test_defaults(self) -> None:
        dto = RegistryRequestDTO()
        assert dto.name == ""
        assert dto.version == "1.0.0"
        assert dto.registry_type == RegistryType.CAPABILITY
        assert dto.scope == RegistryScope.GLOBAL
        assert dto.namespace == "default"

    def test_with_values(self) -> None:
        dto = RegistryRequestDTO(
            name="energy-capability",
            version="2.0.0",
            registry_type=RegistryType.AGENT,
            scope=RegistryScope.DOMAIN,
            owner_id="user-001",
            namespace="energy",
            tags=["ml"],
            description="Energy ML capability",
        )
        assert dto.name == "energy-capability"
        assert dto.version == "2.0.0"
        assert dto.registry_type == RegistryType.AGENT
        assert dto.scope == RegistryScope.DOMAIN
        assert dto.owner_id == "user-001"
        assert dto.namespace == "energy"
        assert dto.tags == ["ml"]
        assert dto.description == "Energy ML capability"


class TestRegistryResponseDTO:
    def test_defaults(self) -> None:
        now = datetime.now(UTC)
        dto = RegistryResponseDTO(
            entry_id=uuid.uuid4(),
            registry_type=RegistryType.CAPABILITY,
            created_at=now,
            updated_at=now,
        )
        assert dto.name == ""
        assert dto.version == "1.0.0"
        assert dto.registry_type == RegistryType.CAPABILITY
        assert dto.enabled is True

    def test_with_values(self) -> None:
        eid = uuid.uuid4()
        now = datetime.now(UTC)
        dto = RegistryResponseDTO(
            entry_id=eid,
            name="energy-capability",
            version="2.0.0",
            registry_type=RegistryType.AGENT,
            scope=RegistryScope.DOMAIN,
            status=RLS.ACTIVE,
            enabled=True,
            created_at=now,
            updated_at=now,
        )
        assert dto.entry_id == eid
        assert dto.name == "energy-capability"
        assert dto.version == "2.0.0"
        assert dto.registry_type == RegistryType.AGENT
        assert dto.scope == RegistryScope.DOMAIN
        assert dto.status == RLS.ACTIVE
        assert dto.enabled is True
        assert dto.created_at == now

    def test_entry_id_required(self) -> None:
        with pytest.raises(Exception):
            RegistryResponseDTO()


class TestRegistrySearchDTO:
    def test_defaults(self) -> None:
        dto = RegistrySearchDTO()
        assert dto.query == ""
        assert dto.registry_type is None
        assert dto.scope is None
        assert dto.status is None
        assert dto.limit == 20
        assert dto.offset == 0

    def test_with_values(self) -> None:
        dto = RegistrySearchDTO(
            query="forecast",
            registry_type=RegistryType.TOOL,
            scope=RegistryScope.DOMAIN,
            status=RLS.ACTIVE,
            namespace="energy",
            tags=["ml"],
            limit=50,
            offset=10,
        )
        assert dto.query == "forecast"
        assert dto.registry_type == RegistryType.TOOL
        assert dto.scope == RegistryScope.DOMAIN
        assert dto.status == RLS.ACTIVE
        assert dto.limit == 50
        assert dto.offset == 10


class TestRegistryRegistrationDTO:
    def test_defaults(self) -> None:
        dto = RegistryRegistrationDTO()
        assert dto.name == ""
        assert dto.version == "1.0.0"
        assert dto.registry_type == RegistryType.CAPABILITY
        assert dto.scope == RegistryScope.GLOBAL
        assert dto.namespace == "default"
        assert dto.entry_data == {}

    def test_with_values(self) -> None:
        dto = RegistryRegistrationDTO(
            name="energy-capability",
            version="1.0.0",
            registry_type=RegistryType.AGENT,
            scope=RegistryScope.DOMAIN,
            namespace="energy",
            owner_id="user-001",
            tags=["ml"],
            entry_data={"model": "forecast:v2"},
        )
        assert dto.name == "energy-capability"
        assert dto.registry_type == RegistryType.AGENT
        assert dto.entry_data == {"model": "forecast:v2"}


# ===================================================================
# Interfaces — BaseRegistry
# ===================================================================

class TestBaseRegistry:
    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            BaseRegistry()

    def test_abstract_methods_exist(self) -> None:
        methods = [
            "register",
            "deregister",
            "lookup",
            "lookup_by_name",
            "search",
            "list_entries",
            "get_version_history",
            "get_version",
            "health",
            "metrics",
        ]
        for method in methods:
            assert hasattr(BaseRegistry, method)

    def test_all_methods_abstract(self) -> None:
        for name in ["register", "deregister", "lookup"]:
            assert getattr(BaseRegistry, name).__isabstractmethod__


# ===================================================================
# Interfaces — All interfaces
# ===================================================================

class TestInterfaces:
    def test_registry_service_interface(self) -> None:
        methods = [
            "register_entry",
            "get_entry",
            "update_entry",
            "delete_entry",
            "search_entries",
            "activate_entry",
            "suspend_entry",
            "deprecate_entry",
            "health",
            "get_metrics",
        ]
        for method in methods:
            assert hasattr(RegistryService, method)

    def test_registry_manager_interface(self) -> None:
        methods = [
            "create_entry",
            "read_entry",
            "update_entry",
            "delete_entry",
            "search_entries",
            "activate_entry",
            "suspend_entry",
            "deprecate_entry",
            "get_health",
            "get_metrics",
        ]
        for method in methods:
            assert hasattr(RegistryManager, method)

    def test_registry_coordinator_interface(self) -> None:
        methods = [
            "register_entry",
            "get_entry",
            "update_entry",
            "delete_entry",
            "search",
            "activate_entry",
            "suspend_entry",
            "deprecate_entry",
            "health",
            "metrics",
        ]
        for method in methods:
            assert hasattr(RegistryCoordinator, method)

    def test_registry_validator_interface(self) -> None:
        methods = [
            "validate_entry",
            "validate_metadata",
            "validate_namespace",
            "validate_version",
            "validate_lifecycle_transition",
            "validate_scope",
        ]
        for method in methods:
            assert hasattr(RegistryValidator, method)

    def test_registry_searcher_interface(self) -> None:
        methods = [
            "search",
            "search_by_name",
            "search_by_tags",
            "count",
        ]
        for method in methods:
            assert hasattr(RegistrySearcher, method)

    def test_registry_version_manager_interface(self) -> None:
        methods = [
            "create_version",
            "get_version",
            "get_version_history",
            "compare_versions",
            "rollback",
        ]
        for method in methods:
            assert hasattr(RegistryVersionManager, method)

    def test_registry_lifecycle_manager_interface(self) -> None:
        methods = [
            "transition",
            "get_valid_transitions",
            "can_transition",
            "get_history",
        ]
        for method in methods:
            assert hasattr(RegistryLifecycleManager, method)

    def test_registry_health_checker_interface(self) -> None:
        methods = [
            "check_health",
            "is_healthy",
            "get_status_summary",
        ]
        for method in methods:
            assert hasattr(RegistryHealthChecker, method)

    def test_registry_cache_interface(self) -> None:
        methods = [
            "get_entry",
            "set_entry",
            "invalidate_entry",
            "clear",
        ]
        for method in methods:
            assert hasattr(RegistryCache, method)


# ===================================================================
# Imports
# ===================================================================

class TestImports:
    def test_all_exports_importable(self) -> None:
        from adip.registry import (
            BaseRegistry,
            EntryRegistered,
            RegistryEntry,
            RegistryException,
            RegistryRequestDTO,
            RegistryService,
            RegistryType,
        )
        assert RegistryType
        assert RegistryEntry
        assert EntryRegistered
        assert RegistryException
        assert RegistryRequestDTO
        assert BaseRegistry
        assert RegistryService

    def test_all_members_in_all(self) -> None:
        from adip import registry
        expected = {
            "RegistryType",
            "RegistryLifecycleStatus",
            "RegistryScope",
            "RegistryEntry",
            "RegistryMetadata",
            "RegistryVersion",
            "RegistryHealth",
            "RegistryMetrics",
            "RegistrySession",
            "RegistryDecision",
            "RegistryConfidence",
            "RegistryExplainabilityMetadata",
            "RegistrySearchResult",
            "RegistryFilter",
            "RegistryNamespace",
            "RegistryEvent",
            "EntryRegistered",
            "EntryUpdated",
            "EntryValidated",
            "EntryActivated",
            "EntryDeprecated",
            "EntryRemoved",
            "RegistryException",
            "RegistryValidationException",
            "RegistryConflictException",
            "RegistrySearchException",
            "RegistryRequestDTO",
            "RegistryResponseDTO",
            "RegistrySearchDTO",
            "RegistryRegistrationDTO",
            "BaseRegistry",
            "RegistryService",
            "RegistryManager",
            "RegistryCoordinator",
            "RegistryValidator",
            "RegistrySearcher",
            "RegistryVersionManager",
            "RegistryLifecycleManager",
            "RegistryHealthChecker",
            "RegistryCache",
            "RegistryCoordinatorImpl",
            "RegistryManagerImpl",
            "RegistrySessionManager",
            "RegistryConfidenceCalculator",
            "RegistryServiceImpl",
            "IntegrationHooks",
            "RegistryPipelineVersion",
        }
        actual = set(registry.__all__)
        assert actual == expected, f"Missing: {expected - actual}, Extra: {actual - expected}"


# ===================================================================
# Edge Cases
# ===================================================================

class TestEdgeCases:
    def test_entry_empty_tags(self) -> None:
        entry = RegistryEntry(tags=[])
        assert entry.tags == []

    def test_entry_large_metadata(self) -> None:
        large_meta = {"key" + str(i): "value" + str(i) for i in range(1000)}
        entry = RegistryEntry(metadata=large_meta)
        assert len(entry.metadata) == 1000

    def test_health_all_unknown(self) -> None:
        h = RegistryHealth()
        for field in ["overall_status", "validator_status", "searcher_status",
                       "version_manager_status", "lifecycle_manager_status", "cache_status"]:
            assert getattr(h, field) == "UNKNOWN"

    def test_session_default_active(self) -> None:
        s = RegistrySession()
        assert s.status == "ACTIVE"

    def test_decision_confidence_bounds(self) -> None:
        with pytest.raises(Exception):
            RegistryDecision(entry_id=uuid.uuid4(), confidence=-0.1)
        with pytest.raises(Exception):
            RegistryDecision(entry_id=uuid.uuid4(), confidence=1.1)

    def test_search_result_score_bounds(self) -> None:
        entry = RegistryEntry()
        with pytest.raises(Exception):
            RegistrySearchResult(entry=entry, score=-0.1)
        with pytest.raises(Exception):
            RegistrySearchResult(entry=entry, score=1.1)

    def test_filter_default_limit_within_bounds(self) -> None:
        f = RegistryFilter(limit=1)
        assert f.limit == 1
        f = RegistryFilter(limit=1000)
        assert f.limit == 1000

    def test_namespace_allowed_scopes_default(self) -> None:
        n = RegistryNamespace(name="test")
        assert len(n.allowed_scopes) == 6
        assert RegistryScope.GLOBAL in n.allowed_scopes
        assert RegistryScope.USER in n.allowed_scopes

    def test_health_negative_values_rejected(self) -> None:
        with pytest.raises(Exception):
            RegistryHealth(entries_total=-1)
        with pytest.raises(Exception):
            RegistryHealth(error_count=-5)
        with pytest.raises(Exception):
            RegistryHealth(uptime_seconds=-1.0)

    def test_metrics_negative_values_rejected(self) -> None:
        with pytest.raises(Exception):
            RegistryMetrics(entries_total=-1)
        with pytest.raises(Exception):
            RegistryMetrics(cache_hits=-1)

    def test_decision_validation_results_default(self) -> None:
        d = RegistryDecision(entry_id=uuid.uuid4())
        assert d.validation_results == []

    def test_metadata_category_default(self) -> None:
        m = RegistryMetadata()
        assert m.category == ""

    def test_version_snapshot_mutable(self) -> None:
        v = RegistryVersion(entry_id=uuid.uuid4())
        v.snapshot["key"] = "value"
        assert v.snapshot["key"] == "value"

    def test_session_entries_affected_mutable(self) -> None:
        s = RegistrySession(entries_affected=["e1"])
        s.entries_affected.append("e2")
        assert s.entries_affected == ["e1", "e2"]

    def test_filter_tags_mutable(self) -> None:
        f = RegistryFilter(tags=["tag1"])
        f.tags.append("tag2")
        assert f.tags == ["tag1", "tag2"]
