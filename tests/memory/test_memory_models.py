"""Validation tests for Memory Manager domain models."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.memory.contracts.models import (
    CacheMemory,
    ConversationMemory,
    LearningMemory,
    MemoryContext,
    MemoryMetrics,
    MemoryPolicy,
    MemoryRecord,
    PlanningMemory,
    RecommendationMemory,
    SessionMemory,
    UserMemory,
    WorkflowMemory,
)
from adip.memory.enums import MemoryType, RetentionPolicy

# ─────────────────────────────────────────────────────────────────────────────
# MemoryRecord
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryRecord:
    def test_default_creation(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION)
        assert record.memory_type == MemoryType.SESSION
        assert record.owner_id == ""
        assert record.namespace == "default"
        assert record.version == 1
        assert record.tags == []
        assert record.metadata == {}

    def test_uuid_auto_generated(self) -> None:
        r1 = MemoryRecord(memory_type=MemoryType.SESSION)
        r2 = MemoryRecord(memory_type=MemoryType.SESSION)
        assert r1.memory_id != r2.memory_id

    def test_custom_values(self) -> None:
        rec_id = uuid.uuid4()
        record = MemoryRecord(
            memory_id=rec_id,
            memory_type=MemoryType.WORKFLOW,
            owner_id="user-123",
            namespace="org-alpha",
            tags=["critical", "production"],
            metadata={"env": "prod"},
            version=3,
        )
        assert record.memory_id == rec_id
        assert record.owner_id == "user-123"
        assert record.namespace == "org-alpha"
        assert record.version == 3
        assert "critical" in record.tags

    def test_version_ge_zero(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, version=0)
        assert record.version == 0

    def test_timestamps_auto_set(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION)
        assert record.created_at is not None
        assert record.updated_at is not None

    def test_expires_at_optional(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION)
        assert record.expires_at is None

    def test_memory_type_required(self) -> None:
        with pytest.raises(ValidationError):
            MemoryRecord()


# ─────────────────────────────────────────────────────────────────────────────
# SessionMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestSessionMemory:
    def test_default_creation(self) -> None:
        mem = SessionMemory()
        assert mem.memory_type == MemoryType.SESSION
        assert mem.session_id == ""
        assert mem.state == {}
        assert mem.ttl_seconds is None

    def test_custom_values(self) -> None:
        mem = SessionMemory(
            session_id="sess-001",
            state={"phase": "execution"},
            ttl_seconds=300,
            owner_id="user-42",
        )
        assert mem.session_id == "sess-001"
        assert mem.state["phase"] == "execution"
        assert mem.ttl_seconds == 300
        assert mem.owner_id == "user-42"

    def test_ttl_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            SessionMemory(ttl_seconds=0)

    def test_is_memory_record(self) -> None:
        assert issubclass(SessionMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# ConversationMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestConversationMemory:
    def test_default_creation(self) -> None:
        mem = ConversationMemory()
        assert mem.memory_type == MemoryType.CONVERSATION
        assert mem.messages == []
        assert mem.summary == ""
        assert mem.turn_count == 0
        assert mem.participants == []

    def test_custom_values(self) -> None:
        mem = ConversationMemory(
            conversation_id="conv-001",
            messages=[{"role": "user", "content": "Hello"}],
            summary="Greeting",
            turn_count=1,
            participants=["alice", "bot"],
        )
        assert mem.conversation_id == "conv-001"
        assert len(mem.messages) == 1
        assert mem.summary == "Greeting"
        assert mem.turn_count == 1
        assert "alice" in mem.participants

    def test_is_memory_record(self) -> None:
        assert issubclass(ConversationMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowMemory:
    def test_default_creation(self) -> None:
        mem = WorkflowMemory()
        assert mem.memory_type == MemoryType.WORKFLOW
        assert mem.execution_state == {}
        assert mem.checkpoints == []

    def test_custom_values(self) -> None:
        mem = WorkflowMemory(
            workflow_id="wf-001",
            execution_state={"status": "RUNNING"},
            checkpoints=[{"task": "T1", "status": "completed"}],
        )
        assert mem.workflow_id == "wf-001"
        assert mem.execution_state["status"] == "RUNNING"
        assert len(mem.checkpoints) == 1

    def test_is_memory_record(self) -> None:
        assert issubclass(WorkflowMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# PlanningMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestPlanningMemory:
    def test_default_creation(self) -> None:
        mem = PlanningMemory()
        assert mem.memory_type == MemoryType.PLANNING
        assert mem.plan_version == 1
        assert mem.planning_traces == []
        assert mem.confidence_history == []

    def test_custom_values(self) -> None:
        mem = PlanningMemory(
            plan_id="plan-001",
            plan_version=3,
            confidence_history=[0.85, 0.92],
            plan_data={"tasks": 5},
        )
        assert mem.plan_id == "plan-001"
        assert mem.plan_version == 3
        assert len(mem.confidence_history) == 2
        assert mem.plan_data["tasks"] == 5

    def test_is_memory_record(self) -> None:
        assert issubclass(PlanningMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# RecommendationMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestRecommendationMemory:
    def test_default_creation(self) -> None:
        mem = RecommendationMemory()
        assert mem.memory_type == MemoryType.RECOMMENDATION
        assert mem.decision == ""
        assert mem.outcome == {}

    def test_custom_values(self) -> None:
        mem = RecommendationMemory(
            recommendation_id="rec-001",
            recommendation_data={"action": "approve"},
            decision="accepted",
            outcome={"success": True},
            feedback={"rating": 5},
        )
        assert mem.recommendation_id == "rec-001"
        assert mem.decision == "accepted"
        assert mem.outcome["success"] is True
        assert mem.feedback["rating"] == 5

    def test_is_memory_record(self) -> None:
        assert issubclass(RecommendationMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# LearningMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestLearningMemory:
    def test_default_creation(self) -> None:
        mem = LearningMemory()
        assert mem.memory_type == MemoryType.LEARNING
        assert mem.pattern == ""
        assert mem.recommendation == ""
        assert mem.applicability == []

    def test_custom_values(self) -> None:
        mem = LearningMemory(
            lesson_id="lesson-001",
            pattern="Retry pattern detected",
            context={"failures": 3},
            recommendation="Increase timeout",
            applicability=["workflow", "executor"],
        )
        assert mem.lesson_id == "lesson-001"
        assert "Retry" in mem.pattern
        assert "workflow" in mem.applicability

    def test_is_memory_record(self) -> None:
        assert issubclass(LearningMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# UserMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestUserMemory:
    def test_default_creation(self) -> None:
        mem = UserMemory()
        assert mem.memory_type == MemoryType.USER
        assert mem.preferences == {}
        assert mem.organisation_settings == {}
        assert mem.personal_defaults == {}

    def test_custom_values(self) -> None:
        mem = UserMemory(
            user_id="user-001",
            preferences={"theme": "dark"},
            organisation_settings={"max_tasks": 10},
            personal_defaults={"retry_policy": "immediate"},
        )
        assert mem.user_id == "user-001"
        assert mem.preferences["theme"] == "dark"
        assert mem.organisation_settings["max_tasks"] == 10

    def test_is_memory_record(self) -> None:
        assert issubclass(UserMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# CacheMemory
# ─────────────────────────────────────────────────────────────────────────────


class TestCacheMemory:
    def test_default_creation(self) -> None:
        mem = CacheMemory()
        assert mem.memory_type == MemoryType.CACHE
        assert mem.cache_key == ""
        assert mem.cached_data == {}
        assert mem.access_count == 0

    def test_custom_values(self) -> None:
        mem = CacheMemory(
            cache_key="plan:001",
            cached_data={"result": "ok"},
            ttl_seconds=60,
            access_count=5,
        )
        assert mem.cache_key == "plan:001"
        assert mem.cached_data["result"] == "ok"
        assert mem.ttl_seconds == 60
        assert mem.access_count == 5

    def test_ttl_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            CacheMemory(ttl_seconds=0)

    def test_is_memory_record(self) -> None:
        assert issubclass(CacheMemory, MemoryRecord)


# ─────────────────────────────────────────────────────────────────────────────
# MemoryContext
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryContext:
    def test_default_creation(self) -> None:
        ctx = MemoryContext()
        assert ctx.session is None
        assert ctx.conversation is None
        assert ctx.workflow is None
        assert ctx.planning is None
        assert ctx.recommendation is None
        assert ctx.learning is None
        assert ctx.user is None
        assert ctx.cache is None
        assert ctx.metadata == {}

    def test_with_memory_types(self) -> None:
        ctx = MemoryContext(
            session=SessionMemory(session_id="sess-1"),
            workflow=WorkflowMemory(workflow_id="wf-1"),
            user=UserMemory(user_id="user-1"),
        )
        assert ctx.session is not None
        assert ctx.session.session_id == "sess-1"
        assert ctx.workflow is not None
        assert ctx.workflow.workflow_id == "wf-1"
        assert ctx.user is not None
        assert ctx.user.user_id == "user-1"
        assert ctx.conversation is None

    def test_custom_metadata(self) -> None:
        ctx = MemoryContext(metadata={"source": "planner"})
        assert ctx.metadata["source"] == "planner"


# ─────────────────────────────────────────────────────────────────────────────
# MemoryPolicy
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryPolicy:
    def test_default_policy(self) -> None:
        p = MemoryPolicy()
        assert p.retention_policy == RetentionPolicy.TEMPORARY
        assert p.ttl is None
        assert p.encryption_required is False
        assert p.compression_enabled is False
        assert p.persistence_required is True
        assert p.replication_required is False
        assert p.audit_enabled is True

    def test_custom_policy(self) -> None:
        p = MemoryPolicy(
            retention_policy=RetentionPolicy.LONG_TERM,
            ttl=86400,
            encryption_required=True,
            compression_enabled=True,
            persistence_required=True,
            replication_required=True,
            audit_enabled=False,
        )
        assert p.retention_policy == RetentionPolicy.LONG_TERM
        assert p.ttl == 86400
        assert p.encryption_required is True
        assert p.compression_enabled is True
        assert p.persistence_required is True
        assert p.replication_required is True
        assert p.audit_enabled is False

    def test_ttl_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            MemoryPolicy(ttl=0)

    def test_serialisation_roundtrip(self) -> None:
        original = MemoryPolicy(retention_policy=RetentionPolicy.PERMANENT, ttl=None)
        data = original.model_dump()
        restored = MemoryPolicy(**data)
        assert restored.retention_policy == RetentionPolicy.PERMANENT
        assert restored.ttl is None


# ─────────────────────────────────────────────────────────────────────────────
# MemoryMetrics
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryMetrics:
    def test_default_metrics(self) -> None:
        m = MemoryMetrics()
        assert m.reads == 0
        assert m.writes == 0
        assert m.cache_hits == 0
        assert m.cache_misses == 0
        assert m.retrieval_latency == 0.0
        assert m.storage_latency == 0.0
        assert m.expired_records == 0
        assert m.memory_usage == {}

    def test_custom_metrics(self) -> None:
        m = MemoryMetrics(
            reads=100,
            writes=50,
            cache_hits=80,
            cache_misses=20,
            retrieval_latency=12.5,
            storage_latency=8.3,
            expired_records=5,
            memory_usage={"hot": "256 MB", "warm": "1 GB"},
        )
        assert m.reads == 100
        assert m.writes == 50
        assert m.cache_hits == 80
        assert m.retrieval_latency == 12.5
        assert m.expired_records == 5
        assert m.memory_usage["hot"] == "256 MB"

    def test_counters_ge_zero(self) -> None:
        with pytest.raises(ValueError):
            MemoryMetrics(reads=-1)

    def test_serialisation_roundtrip(self) -> None:
        original = MemoryMetrics(reads=42, writes=10)
        data = original.model_dump()
        restored = MemoryMetrics(**data)
        assert restored.reads == 42
        assert restored.writes == 10
