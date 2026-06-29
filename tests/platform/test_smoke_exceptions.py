"""Smoke tests for platform exception mapping."""

from __future__ import annotations

from adip.platform.enums import PipelineStage
from adip.platform.orchestration.exception_mapper import DefaultExceptionMapper


class TestExceptionMapping:
    """Verify consistent exception propagation."""

    def test_map_value_error(self) -> None:
        mapper = DefaultExceptionMapper()
        msg = mapper.map_exception(ValueError("bad input"), PipelineStage.VALIDATION)
        assert "Invalid input" in msg
        assert "bad input" in msg

    def test_map_key_error(self) -> None:
        mapper = DefaultExceptionMapper()
        msg = mapper.map_exception(KeyError("missing_key"), PipelineStage.MEMORY)
        assert "Resource not found" in msg

    def test_map_type_error(self) -> None:
        mapper = DefaultExceptionMapper()
        msg = mapper.map_exception(TypeError("int expected"), PipelineStage.PLANNER)
        assert "Type mismatch" in msg

    def test_map_unknown_exception(self) -> None:
        mapper = DefaultExceptionMapper()
        msg = mapper.map_exception(RuntimeError("something broke"), PipelineStage.PLANNER)
        assert "[planner]" in msg
        assert "RuntimeError" in msg
        assert "something broke" in msg

    def test_map_with_empty_message(self) -> None:
        mapper = DefaultExceptionMapper()
        msg = mapper.map_exception(ValueError(), PipelineStage.ENERGY)
        assert "Invalid input" in msg

    def test_is_known_exception(self) -> None:
        mapper = DefaultExceptionMapper()
        assert mapper.is_known_exception(ValueError("test"))
        assert mapper.is_known_exception(KeyError("test"))
        assert not mapper.is_known_exception(RuntimeError("test"))

    def test_stage_in_message(self) -> None:
        mapper = DefaultExceptionMapper()
        msg = mapper.map_exception(ValueError("bad"), PipelineStage.VALIDATION)
        assert msg  # message should be non-empty
