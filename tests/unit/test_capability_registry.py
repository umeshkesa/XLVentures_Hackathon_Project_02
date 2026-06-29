"""Unit tests for the standalone capability registry."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.registries.capability_registry import (
    Capability,
    CapabilityAlreadyRegisteredError,
    CapabilityNotFoundError,
    CapabilityQuery,
    CapabilityRegistry,
    CapabilityUpdate,
    InMemoryCapabilityStorage,
)


def make_capability(**overrides: object) -> Capability:
    """Build a representative capability with optional field overrides."""
    values: dict[str, object] = {
        "name": "Document Search",
        "description": "Search indexed technical documents",
        "category": "tool",
        "tags": {"search", "knowledge"},
        "inputs": {"query", "filters"},
        "outputs": {"documents"},
    }
    values.update(overrides)
    return Capability.model_validate(values)


def make_registry(
    storage: InMemoryCapabilityStorage | None = None,
) -> CapabilityRegistry:
    """Build a registry through its injectable storage boundary."""
    return CapabilityRegistry(storage or InMemoryCapabilityStorage())


class TestCapabilityModel:
    """Verify metadata normalization and model invariants."""

    def test_matching_metadata_is_normalized(self) -> None:
        capability = make_capability(
            category=" TOOL ",
            tags={" Search ", "KNOWLEDGE"},
            inputs={" Query "},
        )

        assert capability.category == "tool"
        assert capability.tags == frozenset({"search", "knowledge"})
        assert capability.inputs == frozenset({"query"})

    def test_model_is_immutable(self) -> None:
        capability = make_capability()

        with pytest.raises(ValidationError):
            capability.name = "Changed"  # type: ignore[misc]

    @pytest.mark.parametrize("field", ["name", "category", "version"])
    def test_required_text_rejects_blank_values(self, field: str) -> None:
        with pytest.raises(ValidationError):
            make_capability(**{field: "   "})

    def test_matching_terms_must_be_strings(self) -> None:
        with pytest.raises(ValidationError, match="must be strings"):
            make_capability(tags={1, 2})


class TestCapabilityRegistryLifecycle:
    """Verify registry CRUD operations."""

    @pytest.mark.asyncio
    async def test_register_list_and_lookup(self) -> None:
        registry = make_registry()
        capability = make_capability()

        registered = await registry.register(capability)

        assert registered is capability
        assert await registry.lookup(capability.id) is capability
        assert await registry.list() == [capability]

    @pytest.mark.asyncio
    async def test_multiple_implementations_may_share_a_name(self) -> None:
        registry = make_registry()
        first = make_capability(priority=1)
        second = make_capability(priority=2)

        await registry.register(first)
        await registry.register(second)

        assert await registry.list() == [second, first]

    @pytest.mark.asyncio
    async def test_duplicate_id_is_rejected(self) -> None:
        registry = make_registry()
        capability = make_capability()
        await registry.register(capability)

        with pytest.raises(CapabilityAlreadyRegisteredError):
            await registry.register(capability)

    @pytest.mark.asyncio
    async def test_update_preserves_id_and_original_model(self) -> None:
        registry = make_registry()
        original = make_capability()
        await registry.register(original)

        updated = await registry.update(
            original.id,
            CapabilityUpdate(tags={"search", "semantic"}, priority=10),
        )

        assert updated.id == original.id
        assert updated.tags == frozenset({"search", "semantic"})
        assert updated.priority == 10
        assert original.tags == frozenset({"search", "knowledge"})
        assert await registry.lookup(original.id) is updated

    @pytest.mark.asyncio
    async def test_update_unknown_id_raises(self) -> None:
        registry = make_registry()

        with pytest.raises(CapabilityNotFoundError):
            await registry.update(uuid.uuid4(), CapabilityUpdate(priority=1))

    @pytest.mark.asyncio
    async def test_unregister_reports_if_capability_existed(self) -> None:
        registry = make_registry()
        capability = make_capability()
        await registry.register(capability)

        assert await registry.unregister(capability.id) is True
        assert await registry.unregister(capability.id) is False
        assert await registry.lookup(capability.id) is None

    @pytest.mark.asyncio
    async def test_list_supports_pagination(self) -> None:
        registry = make_registry()
        low = make_capability(name="A", priority=1)
        high = make_capability(name="B", priority=2)
        await registry.register(low)
        await registry.register(high)

        assert await registry.list(offset=1, limit=1) == [low]
        with pytest.raises(ValueError, match="offset"):
            await registry.list(offset=-1)
        with pytest.raises(ValueError, match="limit"):
            await registry.list(limit=0)


class TestCapabilityMatching:
    """Verify conjunctive matching over advertised metadata."""

    @pytest.mark.asyncio
    async def test_search_matches_all_metadata_constraints(self) -> None:
        registry = make_registry()
        matching = make_capability()
        wrong_category = make_capability(category="agent")
        missing_output = make_capability(outputs={"summary"})
        for capability in (matching, wrong_category, missing_output):
            await registry.register(capability)

        results = await registry.search(
            CapabilityQuery(
                category="TOOL",
                tags={"SEARCH"},
                inputs={"query"},
                outputs={"documents"},
            )
        )

        assert results == [matching]

    @pytest.mark.asyncio
    async def test_requested_terms_must_be_advertised_subsets(self) -> None:
        registry = make_registry()
        capability = make_capability()
        await registry.register(capability)

        assert await registry.search(CapabilityQuery(tags={"search"})) == [capability]
        assert await registry.search(CapabilityQuery(tags={"search", "ocr"})) == []
        assert await registry.search(CapabilityQuery(inputs={"unknown"})) == []
        assert await registry.search(CapabilityQuery(outputs={"summary"})) == []

    @pytest.mark.asyncio
    async def test_text_search_is_case_insensitive_across_metadata(self) -> None:
        registry = make_registry()
        capability = make_capability()
        await registry.register(capability)

        assert await registry.search(CapabilityQuery(text="TECHNICAL")) == [capability]
        assert await registry.search(CapabilityQuery(text="knowledge")) == [capability]
        assert await registry.search(CapabilityQuery(text="missing")) == []


class RecordingStorage(InMemoryCapabilityStorage):
    """Test adapter proving the service depends on the storage protocol."""

    def __init__(self) -> None:
        super().__init__()
        self.add_calls = 0

    async def add(self, capability: Capability) -> bool:
        self.add_calls += 1
        return await super().add(capability)


@pytest.mark.asyncio
async def test_storage_is_dependency_injected() -> None:
    storage = RecordingStorage()
    registry = make_registry(storage)

    await registry.register(make_capability())

    assert storage.add_calls == 1
