"""Event publisher service for publishing events after storage."""

import asyncio
import logging
from typing import Optional

from ..events.domain_events import DomainEvent
from .event_bus import EventBus

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing events after they are stored."""

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus

    async def publish_async(self, event: DomainEvent) -> None:
        """Publish event asynchronously."""
        if self.event_bus is None:
            return

        try:
            await self.event_bus.publish(event)
        except Exception as e:
            logger.warning(
                "Failed to publish event %s: %s",
                event.__class__.__name__,
                str(e),
                exc_info=True,
            )

    def publish_sync(self, event: DomainEvent) -> None:
        """Publish event synchronously (creates async task or runs in new loop)."""
        if self.event_bus is None:
            return

        try:
            # Try to use existing event loop if available
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish_async(event))
        except RuntimeError:
            # No event loop running, create one for this publish
            try:
                asyncio.run(self.publish_async(event))
            except Exception as e:
                logger.warning(
                    "Failed to publish event %s: %s",
                    event.__class__.__name__,
                    str(e),
                    exc_info=True,
                )
