"""DefaultMemoryService — enterprise facade for all memory operations.

MemoryService is the ONLY public entry point to the Memory Platform.
Responsibilities:

    • Validate requests
    • Authentication hook
    • Authorization hook
    • Audit hook
    • Logging
    • Metrics
    • Correlation IDs
    • Create MemorySession
    • Call MemoryManager

MemoryService must never access stores directly.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.memory.contracts.models import MemoryContext, MemoryPolicy, MemoryRecord
from adip.memory.enums import MemoryOperation, MemoryType
from adip.memory.execution.audit_manager import AuditManager
from adip.memory.interfaces import MemoryManager, MemoryService
from adip.memory.orchestration.session import MemorySession

log = structlog.get_logger(__name__)


class DefaultMemoryService(MemoryService):
    """Enterprise facade for memory operations.

    Provides validation, authentication, authorization, audit,
    logging, metrics, correlation IDs, and MemorySession management
    around the MemoryManager.
    """

    def __init__(
        self,
        manager: MemoryManager,
        audit: AuditManager | None = None,
    ) -> None:
        self._manager = manager
        self._audit = audit or AuditManager()
        self._sessions: list[MemorySession] = []

    async def store(
        self,
        record: MemoryRecord,
        owner_id: str | None = None,
        policy: MemoryPolicy | None = None,
    ) -> MemoryRecord:
        correlation_id = self._generate_correlation_id()
        session = self._create_session("store", owner_id or record.owner_id)

        self._authenticate(session)
        self._authorise("store", record)

        log.info(
            "service.store",
            memory_id=str(record.memory_id),
            memory_type=record.memory_type.value,
            domain=record.memory_domain.value,
            correlation_id=correlation_id,
            session_id=str(session.session_id),
        )

        try:
            result = await self._manager.create(record)
        except Exception:
            log.exception(
                "service.store.error",
                memory_id=str(record.memory_id),
                correlation_id=correlation_id,
            )
            raise

        session.record_operation("store", str(result.memory_id))
        self._audit.record(result, MemoryOperation.CREATE, correlation_id=correlation_id)
        self._complete_session(session)

        log.info(
            "service.store.complete",
            memory_id=str(result.memory_id),
            correlation_id=correlation_id,
            duration_ms=self._session_duration(session),
        )
        return result

    async def retrieve(
        self,
        memory_id: str,
        owner_id: str | None = None,
    ) -> MemoryRecord | None:
        correlation_id = self._generate_correlation_id()
        session = self._create_session("retrieve", owner_id or "")

        self._authenticate(session)
        self._authorise("retrieve", memory_id=memory_id)

        log.info(
            "service.retrieve",
            memory_id=memory_id,
            correlation_id=correlation_id,
            session_id=str(session.session_id),
        )

        try:
            result = await self._manager.read(memory_id)
        except Exception:
            log.exception(
                "service.retrieve.error",
                memory_id=memory_id,
                correlation_id=correlation_id,
            )
            raise

        session.record_operation("retrieve", memory_id if result else None)
        self._complete_session(session)

        log.info(
            "service.retrieve.complete",
            memory_id=memory_id,
            found=result is not None,
            correlation_id=correlation_id,
        )
        return result

    async def remove(
        self,
        memory_id: str,
        owner_id: str | None = None,
    ) -> bool:
        correlation_id = self._generate_correlation_id()
        session = self._create_session("remove", owner_id or "")

        self._authenticate(session)
        self._authorise("remove", memory_id=memory_id)

        log.info(
            "service.remove",
            memory_id=memory_id,
            correlation_id=correlation_id,
            session_id=str(session.session_id),
        )

        try:
            result = await self._manager.delete(memory_id)
        except Exception:
            log.exception(
                "service.remove.error",
                memory_id=memory_id,
                correlation_id=correlation_id,
            )
            raise

        if result:
            self._audit.record_raw(memory_id, MemoryOperation.DELETE, correlation_id=correlation_id)

        session.record_operation("remove", memory_id if result else None)
        self._complete_session(session)

        log.info(
            "service.remove.complete",
            memory_id=memory_id,
            deleted=result,
            correlation_id=correlation_id,
        )
        return result

    async def find(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        correlation_id = self._generate_correlation_id()
        session = self._create_session("find", owner_id or "")

        log.info(
            "service.find",
            correlation_id=correlation_id,
            session_id=str(session.session_id),
        )

        try:
            results = await self._manager.search(
                memory_type=memory_type,
                owner_id=owner_id,
                namespace=namespace,
                tags=tags,
                limit=limit,
                offset=offset,
            )
        except Exception:
            log.exception(
                "service.find.error",
                correlation_id=correlation_id,
            )
            raise

        session.record_operation("find")
        self._complete_session(session)

        log.info(
            "service.find.complete",
            count=len(results),
            correlation_id=correlation_id,
        )
        return results

    async def context(self, **identifiers: str) -> MemoryContext:
        correlation_id = self._generate_correlation_id()
        session = self._create_session("context", identifiers.get("owner_id", ""))

        log.info(
            "service.context",
            correlation_id=correlation_id,
            session_id=str(session.session_id),
        )

        try:
            result = await self._manager.get_context(**identifiers)
        except Exception:
            log.exception(
                "service.context.error",
                correlation_id=correlation_id,
            )
            raise

        session.record_operation("context")
        self._complete_session(session)

        return result

    # ── Session Management ────────────────────────────────────────────────

    def get_sessions(self) -> list[MemorySession]:
        """Return all recorded sessions."""
        return list(self._sessions)

    def get_session(self, session_id: str) -> MemorySession | None:
        """Return a specific session by ID."""
        for s in self._sessions:
            if str(s.session_id) == session_id:
                return s
        return None

    # ── Internal ──────────────────────────────────────────────────────────

    @staticmethod
    def _generate_correlation_id() -> str:
        return str(uuid.uuid4())

    def _create_session(self, operation: str, owner_id: str) -> MemorySession:
        session = MemorySession(owner_id=owner_id)
        session.record_operation(operation)
        self._sessions.append(session)
        return session

    @staticmethod
    def _complete_session(session: MemorySession) -> None:
        session.complete()

    @staticmethod
    def _session_duration(session: MemorySession) -> float:
        if session.started_at and session.completed_at:
            return round((session.completed_at - session.started_at).total_seconds() * 1000, 2)
        return 0.0

    def _authenticate(self, session: MemorySession) -> None:
        """Placeholder authentication hook.

        Future implementations will verify the caller's identity
        using the session's owner_id.
        """
        pass

    def _authorise(self, operation: str, record: MemoryRecord | None = None, **kwargs: Any) -> None:
        """Placeholder authorisation check.

        Future implementations will enforce access control policies
        based on the caller's identity, the memory type, and the
        requested operation.
        """
        pass
