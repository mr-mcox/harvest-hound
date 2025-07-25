"""
Projection registry for managing event handlers.

Central registry that routes domain events to appropriate projection handlers
following the event-driven architecture pattern from ADR-005.
"""
import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable, DefaultDict, List, Type, Union

from ..events.domain_events import DomainEvent


class ProjectionRegistry:
    """
    Central registry for projection event handlers.
    
    Routes domain events to registered handlers, supporting multiple
    handlers per event type for flexible projection architectures.
    """
    
    def __init__(self) -> None:
        # Use defaultdict to store lists of handlers per event type
        self._handlers: DefaultDict[Type[DomainEvent], List[Union[Callable[[Any], None], Callable[[Any], Awaitable[None]]]]] = defaultdict(list)
    
    def register(self, event_type: Type[DomainEvent], handler: Union[Callable[[Any], None], Callable[[Any], Awaitable[None]]]) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: The domain event class to handle
            handler: Callable that takes the event as parameter (sync or async)
        """
        self._handlers[event_type].append(handler)
    
    def handle(self, event: DomainEvent) -> None:
        """
        Route event to all registered handlers for its type.
        
        Args:
            event: Domain event to be processed
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        # Call all registered handlers for this event type
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # For async handlers, we need to run them in the event loop
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler(event))
                    except RuntimeError:
                        # No event loop running, create one
                        asyncio.run(handler(event))
                else:
                    handler(event)
            except Exception as e:
                # In production, this would use proper logging
                # For now, we'll let exceptions bubble up in tests
                # but in real usage we might want to catch and log
                raise e
    
    def get_handler_count(self, event_type: Type[DomainEvent]) -> int:
        """
        Get number of registered handlers for an event type.
        
        Useful for testing and debugging.
        """
        return len(self._handlers.get(event_type, []))
    
    def clear(self) -> None:
        """
        Clear all registered handlers.
        
        Useful for testing and reconfiguration.
        """
        self._handlers.clear()