"""Event bus infrastructure for decoupling event producers from consumers."""

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List, Type, Union

from ..events.domain_events import DomainEvent


class EventBus(ABC):
    """Abstract event bus interface for async publish/subscribe."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered subscribers."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")

    @abstractmethod
    async def subscribe(self, event_type: Type[DomainEvent], handler: Union[Callable[[Any], None], Callable[[Any], Awaitable[None]]]) -> None:
        """Subscribe a handler to events of a specific type."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")

    @abstractmethod
    async def unsubscribe(self, event_type: Type[DomainEvent], handler: Union[Callable[[Any], None], Callable[[Any], Awaitable[None]]]) -> None:
        """Unsubscribe a handler from events of a specific type."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")


class InMemoryEventBus(EventBus):
    """In-memory event bus implementation for development."""

    def __init__(self) -> None:
        self._subscribers: Dict[Type[DomainEvent], List[Union[Callable[[Any], None], Callable[[Any], Awaitable[None]]]]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered subscribers."""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        
        for handler in handlers:
            try:
                # Check if handler is async or sync
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                # In production, this would use proper logging
                # For now, we don't want handler failures to break event publishing
                pass

    async def subscribe(self, event_type: Type[DomainEvent], handler: Union[Callable[[Any], None], Callable[[Any], Awaitable[None]]]) -> None:
        """Subscribe a handler to events of a specific type."""
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    async def unsubscribe(self, event_type: Type[DomainEvent], handler: Union[Callable[[Any], None], Callable[[Any], Awaitable[None]]]) -> None:
        """Unsubscribe a handler from events of a specific type."""
        try:
            self._subscribers[event_type].remove(handler)
        except ValueError:
            # Handler not in list, ignore silently
            pass


class EventBusManager:
    """Injectable service for managing event bus lifecycle."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    async def get_event_bus(self) -> EventBus:
        """Get the configured event bus instance."""
        return self.event_bus