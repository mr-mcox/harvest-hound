"""Event bus infrastructure for decoupling event producers from consumers."""

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type

from ..events.domain_events import DomainEvent


class EventBus(ABC):
    """Abstract event bus interface for async publish/subscribe."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered subscribers."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")

    @abstractmethod
    async def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe a handler to events of a specific type."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")

    @abstractmethod
    async def unsubscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """Unsubscribe a handler from events of a specific type."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")


class InMemoryEventBus(EventBus):
    """In-memory event bus implementation for development."""

    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered subscribers."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")

    async def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe a handler to events of a specific type."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")

    async def unsubscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """Unsubscribe a handler from events of a specific type."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")


class EventBusManager:
    """Injectable service for managing event bus lifecycle."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def get_event_bus(self) -> EventBus:
        """Get the configured event bus instance."""
        raise NotImplementedError("TODO: implement in NEW BEHAVIOR task")