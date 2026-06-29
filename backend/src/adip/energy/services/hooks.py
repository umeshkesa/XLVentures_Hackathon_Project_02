"""IntegrationHooks — extension points for the Energy Domain.

Provides hook points for external integrations to observe
energy domain operations. All hooks are exception-isolated.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)

HookCallback = Callable[..., Any]


class IntegrationHooks:
    """Extension hooks for the Energy Domain Package.

    Provides pre/post hooks for asset, sensor, reading, twin,
    alarm, incident, maintenance, session, decision, and error
    operations. All hooks execute with exception isolation.
    """

    def __init__(self) -> None:
        self._pre_register_asset: list[HookCallback] = []
        self._post_register_asset: list[HookCallback] = []
        self._pre_register_sensor: list[HookCallback] = []
        self._post_register_sensor: list[HookCallback] = []
        self._pre_receive_reading: list[HookCallback] = []
        self._post_receive_reading: list[HookCallback] = []
        self._pre_create_twin: list[HookCallback] = []
        self._post_create_twin: list[HookCallback] = []
        self._pre_raise_alarm: list[HookCallback] = []
        self._post_raise_alarm: list[HookCallback] = []
        self._pre_create_incident: list[HookCallback] = []
        self._post_create_incident: list[HookCallback] = []
        self._pre_record_maintenance: list[HookCallback] = []
        self._post_record_maintenance: list[HookCallback] = []
        self._session_created: list[HookCallback] = []
        self._session_completed: list[HookCallback] = []
        self._decision_made: list[HookCallback] = []
        self._on_error: list[HookCallback] = []

    def register_pre_register_asset(self, callback: HookCallback) -> None:
        """Register a hook to run before asset registration."""
        self._pre_register_asset.append(callback)

    def register_post_register_asset(self, callback: HookCallback) -> None:
        """Register a hook to run after asset registration."""
        self._post_register_asset.append(callback)

    def register_pre_register_sensor(self, callback: HookCallback) -> None:
        """Register a hook to run before sensor registration."""
        self._pre_register_sensor.append(callback)

    def register_post_register_sensor(self, callback: HookCallback) -> None:
        """Register a hook to run after sensor registration."""
        self._post_register_sensor.append(callback)

    def register_pre_receive_reading(self, callback: HookCallback) -> None:
        """Register a hook to run before receiving a reading."""
        self._pre_receive_reading.append(callback)

    def register_post_receive_reading(self, callback: HookCallback) -> None:
        """Register a hook to run after receiving a reading."""
        self._post_receive_reading.append(callback)

    def register_pre_create_twin(self, callback: HookCallback) -> None:
        """Register a hook to run before digital twin creation."""
        self._pre_create_twin.append(callback)

    def register_post_create_twin(self, callback: HookCallback) -> None:
        """Register a hook to run after digital twin creation."""
        self._post_create_twin.append(callback)

    def register_pre_raise_alarm(self, callback: HookCallback) -> None:
        """Register a hook to run before raising an alarm."""
        self._pre_raise_alarm.append(callback)

    def register_post_raise_alarm(self, callback: HookCallback) -> None:
        """Register a hook to run after raising an alarm."""
        self._post_raise_alarm.append(callback)

    def register_pre_create_incident(self, callback: HookCallback) -> None:
        """Register a hook to run before creating an incident."""
        self._pre_create_incident.append(callback)

    def register_post_create_incident(self, callback: HookCallback) -> None:
        """Register a hook to run after creating an incident."""
        self._post_create_incident.append(callback)

    def register_pre_record_maintenance(self, callback: HookCallback) -> None:
        """Register a hook to run before recording maintenance."""
        self._pre_record_maintenance.append(callback)

    def register_post_record_maintenance(self, callback: HookCallback) -> None:
        """Register a hook to run after recording maintenance."""
        self._post_record_maintenance.append(callback)

    def register_session_created(self, callback: HookCallback) -> None:
        """Register a hook to run when a session is created."""
        self._session_created.append(callback)

    def register_session_completed(self, callback: HookCallback) -> None:
        """Register a hook to run when a session completes."""
        self._session_completed.append(callback)

    def register_decision_made(self, callback: HookCallback) -> None:
        """Register a hook to run when a decision is made."""
        self._decision_made.append(callback)

    def register_on_error(self, callback: HookCallback) -> None:
        """Register a hook to run on error."""
        self._on_error.append(callback)

    def _fire(self, hooks: list[HookCallback], **kwargs: Any) -> None:
        """Fire all hooks in a list with exception isolation.

        Args:
            hooks: List of hook callbacks to fire.
            kwargs: Keyword arguments to pass to each hook.
        """
        for hook in hooks:
            try:
                hook(**kwargs)
            except Exception:
                log.exception("hook.failed", hook=hook.__name__)

    def run_pre_register_asset(self, **kwargs: Any) -> None:
        """Run all pre-register-asset hooks."""
        self._fire(self._pre_register_asset, **kwargs)

    def run_post_register_asset(self, **kwargs: Any) -> None:
        """Run all post-register-asset hooks."""
        self._fire(self._post_register_asset, **kwargs)

    def run_pre_register_sensor(self, **kwargs: Any) -> None:
        """Run all pre-register-sensor hooks."""
        self._fire(self._pre_register_sensor, **kwargs)

    def run_post_register_sensor(self, **kwargs: Any) -> None:
        """Run all post-register-sensor hooks."""
        self._fire(self._post_register_sensor, **kwargs)

    def run_pre_receive_reading(self, **kwargs: Any) -> None:
        """Run all pre-receive-reading hooks."""
        self._fire(self._pre_receive_reading, **kwargs)

    def run_post_receive_reading(self, **kwargs: Any) -> None:
        """Run all post-receive-reading hooks."""
        self._fire(self._post_receive_reading, **kwargs)

    def run_pre_create_twin(self, **kwargs: Any) -> None:
        """Run all pre-create-twin hooks."""
        self._fire(self._pre_create_twin, **kwargs)

    def run_post_create_twin(self, **kwargs: Any) -> None:
        """Run all post-create-twin hooks."""
        self._fire(self._post_create_twin, **kwargs)

    def run_pre_raise_alarm(self, **kwargs: Any) -> None:
        """Run all pre-raise-alarm hooks."""
        self._fire(self._pre_raise_alarm, **kwargs)

    def run_post_raise_alarm(self, **kwargs: Any) -> None:
        """Run all post-raise-alarm hooks."""
        self._fire(self._post_raise_alarm, **kwargs)

    def run_pre_create_incident(self, **kwargs: Any) -> None:
        """Run all pre-create-incident hooks."""
        self._fire(self._pre_create_incident, **kwargs)

    def run_post_create_incident(self, **kwargs: Any) -> None:
        """Run all post-create-incident hooks."""
        self._fire(self._post_create_incident, **kwargs)

    def run_pre_record_maintenance(self, **kwargs: Any) -> None:
        """Run all pre-record-maintenance hooks."""
        self._fire(self._pre_record_maintenance, **kwargs)

    def run_post_record_maintenance(self, **kwargs: Any) -> None:
        """Run all post-record-maintenance hooks."""
        self._fire(self._post_record_maintenance, **kwargs)

    def run_session_created(self, **kwargs: Any) -> None:
        """Run all session-created hooks."""
        self._fire(self._session_created, **kwargs)

    def run_session_completed(self, **kwargs: Any) -> None:
        """Run all session-completed hooks."""
        self._fire(self._session_completed, **kwargs)

    def run_decision_made(self, **kwargs: Any) -> None:
        """Run all decision-made hooks."""
        self._fire(self._decision_made, **kwargs)

    def run_on_error(self, **kwargs: Any) -> None:
        """Run all on-error hooks."""
        self._fire(self._on_error, **kwargs)


hooks = IntegrationHooks()
