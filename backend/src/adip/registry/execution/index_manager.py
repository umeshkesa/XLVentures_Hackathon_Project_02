"""RegistryIndexManager — maintains logical indexes for fast lookups.

Supports name, tag, label, namespace, and type indexes.
Placeholder implementation using in-memory dictionaries.
"""

from __future__ import annotations

import structlog

from adip.registry.contracts.models import RegistryEntry
from adip.registry.enums import RegistryType

log = structlog.get_logger(__name__)


class RegistryIndexManager:
    """Maintains logical indexes for registry entries.

    Indexes:
        - Name Index: entry name → entry
        - Tag Index: tag → list of entries
        - Label Index: metadata label → list of entries
        - Namespace Index: namespace → list of entries
        - Type Index: registry type → list of entries
    """

    def __init__(self) -> None:
        self._name_index: dict[str, RegistryEntry] = {}
        self._tag_index: dict[str, list[RegistryEntry]] = {}
        self._label_index: dict[str, list[RegistryEntry]] = {}
        self._namespace_index: dict[str, list[RegistryEntry]] = {}
        self._type_index: dict[str, list[RegistryEntry]] = {}

    def index_entry(self, entry: RegistryEntry) -> None:
        """Index a registry entry across all index types."""
        log.info("registry_index_manager.index_entry", entry_id=str(entry.entry_id), name=entry.name)
        self._index_name(entry)
        self._index_tags(entry)
        self._index_labels(entry)
        self._index_namespace(entry)
        self._index_type(entry)

    def remove_entry(self, entry: RegistryEntry) -> None:
        """Remove an entry from all indexes."""
        log.info("registry_index_manager.remove_entry", entry_id=str(entry.entry_id), name=entry.name)
        self._name_index.pop(entry.name, None)
        for tag_entries in self._tag_index.values():
            tag_entries[:] = [e for e in tag_entries if e.entry_id != entry.entry_id]
        for label_entries in self._label_index.values():
            label_entries[:] = [e for e in label_entries if e.entry_id != entry.entry_id]
        ns_entries = self._namespace_index.get(entry.namespace, [])
        ns_entries[:] = [e for e in ns_entries if e.entry_id != entry.entry_id]
        type_entries = self._type_index.get(entry.registry_type.value, [])
        type_entries[:] = [e for e in type_entries if e.entry_id != entry.entry_id]

    def clear(self) -> int:
        """Clear all indexes. Returns total count of indexed entries."""
        total = (
            len(self._name_index)
            + sum(len(v) for v in self._tag_index.values())
            + sum(len(v) for v in self._label_index.values())
            + sum(len(v) for v in self._namespace_index.values())
            + sum(len(v) for v in self._type_index.values())
        )
        self._name_index.clear()
        self._tag_index.clear()
        self._label_index.clear()
        self._namespace_index.clear()
        self._type_index.clear()
        return total

    # ── index lookups ─────────────────────────────────────────────

    def get_by_name(self, name: str) -> RegistryEntry | None:
        """Look up an entry by exact name."""
        return self._name_index.get(name)

    def get_by_tag(self, tag: str) -> list[RegistryEntry]:
        """Get entries matching a tag."""
        return self._tag_index.get(tag, [])

    def get_by_label(self, label_key: str) -> list[RegistryEntry]:
        """Get entries matching a metadata label key."""
        return self._label_index.get(label_key, [])

    def get_by_namespace(self, namespace: str) -> list[RegistryEntry]:
        """Get entries in a namespace."""
        return self._namespace_index.get(namespace, [])

    def get_by_type(self, registry_type: RegistryType) -> list[RegistryEntry]:
        """Get entries of a registry type."""
        return self._type_index.get(registry_type.value, [])

    # ── index sizes ───────────────────────────────────────────────

    def name_index_size(self) -> int:
        return len(self._name_index)

    def tag_index_size(self) -> int:
        return sum(len(v) for v in self._tag_index.values())

    def label_index_size(self) -> int:
        return sum(len(v) for v in self._label_index.values())

    def namespace_index_size(self) -> int:
        return sum(len(v) for v in self._namespace_index.values())

    def type_index_size(self) -> int:
        return sum(len(v) for v in self._type_index.values())

    def total_index_size(self) -> int:
        """Total number of index entries across all indexes."""
        return (
            self.name_index_size()
            + self.tag_index_size()
            + self.label_index_size()
            + self.namespace_index_size()
            + self.type_index_size()
        )

    # ── private helpers ───────────────────────────────────────────

    def _index_name(self, entry: RegistryEntry) -> None:
        self._name_index[entry.name] = entry

    def _index_tags(self, entry: RegistryEntry) -> None:
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(entry)

    def _index_labels(self, entry: RegistryEntry) -> None:
        for key in entry.metadata:
            if key not in self._label_index:
                self._label_index[key] = []
            self._label_index[key].append(entry)

    def _index_namespace(self, entry: RegistryEntry) -> None:
        ns = entry.namespace
        if ns not in self._namespace_index:
            self._namespace_index[ns] = []
        self._namespace_index[ns].append(entry)

    def _index_type(self, entry: RegistryEntry) -> None:
        rt = entry.registry_type.value
        if rt not in self._type_index:
            self._type_index[rt] = []
        self._type_index[rt].append(entry)
