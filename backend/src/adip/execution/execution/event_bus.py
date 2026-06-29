"""RuntimeEventBus — publish/subscribe event bus for execution events.

Provides an in-memory publish/subscribe event bus for
execution runtime events, supporting task events and
execution lifecycle events with multiple subscribers.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

from adip.execution.execution.models import EventBusMessage

log = structlog.get_logger(__name__)

EventHandler = Callable[[EventBusMessage], None]


class RuntimeEventBus:
    """In-memory publish/subscribe event bus for execution runtime events."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._messages: list[EventBusMessage] = []

    def subscribe(
        self,
        topic: str,
        handler: EventHandler,
        correlation_id: str = "",
    ) -> None:
        """Subscribe to events on a topic.

        Args:
            topic: The topic to subscribe to (task, execution, checkpoint, retry, compensation).
            handler: Callback function to handle events.
            correlation_id: Optional correlation ID for tracing.
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        log.info(
            "event_bus.subscribed",
            topic=topic,
            handler_count=len(self._subscribers[topic]),
            correlation_id=correlation_id,
        )

    def unsubscribe(
        self,
        topic: str,
        handler: EventHandler,
        correlation_id: str = "",
    ) -> bool:
        """Unsubscribe a handler from a topic.

        Args:
            topic: The topic to unsubscribe from.
            handler: The handler to remove.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if handler was removed, False otherwise.
        """
        if topic in self._subscribers and handler in self._subscribers[topic]:
            self._subscribers[topic].remove(handler)
            log.info(
                "event_bus.unsubscribed",
                topic=topic,
                correlation_id=correlation_id,
            )
            return True
        return False

    def publish(
        self,
        topic: str,
        event_type: str,
        session_id: str = "",
        task_id: str = "",
        payload: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> EventBusMessage:
        """Publish an event to all subscribers of a topic.

        Args:
            topic: The event topic.
            event_type: Type of event within the topic.
            session_id: Session ID associated with this event.
            task_id: Task ID associated with this event.
            payload: Event payload data.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The published EventBusMessage.
        """
        message = EventBusMessage(
            topic=topic,
            event_type=event_type,
            session_id=session_id,
            task_id=task_id,
            payload=payload or {},
        )
        self._messages.append(message)

        handlers = self._subscribers.get(topic, [])
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                log.error(
                    "event_bus.handler_error",
                    topic=topic,
                    error=str(e),
                    correlation_id=correlation_id,
                )

        log.info(
            "event_bus.published",
            topic=topic,
            event_type=event_type,
            session_id=session_id,
            task_id=task_id,
            handler_count=len(handlers),
            correlation_id=correlation_id,
        )
        return message

    def publish_task_event(
        self,
        event_type: str,
        session_id: str = "",
        task_id: str = "",
        payload: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> EventBusMessage:
        """Publish a task-related event.

        Args:
            event_type: Type of task event (started, completed, failed).
            session_id: Session ID.
            task_id: Task ID.
            payload: Event payload.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The published EventBusMessage.
        """
        return self.publish(
            topic="task",
            event_type=event_type,
            session_id=session_id,
            task_id=task_id,
            payload=payload,
            correlation_id=correlation_id,
        )

    def publish_execution_event(
        self,
        event_type: str,
        session_id: str = "",
        payload: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> EventBusMessage:
        """Publish an execution lifecycle event.

        Args:
            event_type: Type of execution event (started, completed, failed, cancelled).
            session_id: Session ID.
            payload: Event payload.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The published EventBusMessage.
        """
        return self.publish(
            topic="execution",
            event_type=event_type,
            session_id=session_id,
            payload=payload,
            correlation_id=correlation_id,
        )

    def get_messages(
        self,
        topic: str | None = None,
        session_id: str | None = None,
    ) -> list[EventBusMessage]:
        """Get published messages with optional filtering.

        Args:
            topic: Optional topic filter.
            session_id: Optional session ID filter.

        Returns:
            Filtered list of EventBusMessage.
        """
        messages = self._messages
        if topic:
            messages = [m for m in messages if m.topic == topic]
        if session_id:
            messages = [m for m in messages if m.session_id == session_id]
        return messages

    def clear(self) -> None:
        """Clear all messages and subscribers."""
        self._messages.clear()
        self._subscribers.clear()
