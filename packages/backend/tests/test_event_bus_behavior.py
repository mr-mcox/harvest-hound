"""Tests for event bus behavior (NEW BEHAVIOR - TDD approach)."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.events.domain_events import StoreCreated
from app.infrastructure.event_bus import InMemoryEventBus


class TestInMemoryEventBusPublish:
    """Test InMemoryEventBus.publish() calls registered handlers."""

    @pytest.mark.asyncio
    async def test_publish_calls_registered_sync_handler(self) -> None:
        """Event bus should call synchronous handlers when event is published."""
        # Given
        event_bus = InMemoryEventBus()
        handler = Mock()
        event = StoreCreated(
            store_id=uuid4(),
            name="Test Store",
            description="Test",
            infinite_supply=False,
            created_at=datetime.now()
        )
        
        # When
        await event_bus.subscribe(StoreCreated, handler)
        await event_bus.publish(event)
        
        # Then
        handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_calls_registered_async_handler(self) -> None:
        """Event bus should call asynchronous handlers when event is published."""
        # Given
        event_bus = InMemoryEventBus()
        handler = AsyncMock()
        event = StoreCreated(
            store_id=uuid4(),
            name="Test Store",
            description="Test",
            infinite_supply=False,
            created_at=datetime.now()
        )
        
        # When
        await event_bus.subscribe(StoreCreated, handler)
        await event_bus.publish(event)
        
        # Then
        handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_calls_multiple_handlers(self) -> None:
        """Event bus should call all registered handlers for an event type."""
        # Given
        event_bus = InMemoryEventBus()
        handler1 = Mock()
        handler2 = AsyncMock()
        event = StoreCreated(
            store_id=uuid4(),
            name="Test Store",
            description="Test",
            infinite_supply=False,
            created_at=datetime.now()
        )
        
        # When
        await event_bus.subscribe(StoreCreated, handler1)
        await event_bus.subscribe(StoreCreated, handler2)
        await event_bus.publish(event)
        
        # Then
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_with_no_subscribers_does_not_error(self) -> None:
        """Event bus should handle publishing with no subscribers gracefully."""
        # Given
        event_bus = InMemoryEventBus()
        event = StoreCreated(
            store_id=uuid4(),
            name="Test Store",
            description="Test",
            infinite_supply=False,
            created_at=datetime.now()
        )
        
        # When / Then - should not raise
        await event_bus.publish(event)


class TestInMemoryEventBusSubscribe:
    """Test InMemoryEventBus.subscribe() registers handlers correctly."""

    @pytest.mark.asyncio
    async def test_subscribe_registers_handler(self) -> None:
        """Event bus should register handlers for subscription."""
        # Given
        event_bus = InMemoryEventBus()
        handler = Mock()
        
        # When
        await event_bus.subscribe(StoreCreated, handler)
        
        # Then - handler should be in subscribers
        assert handler in event_bus._subscribers[StoreCreated]

    @pytest.mark.asyncio
    async def test_subscribe_same_handler_twice_only_registers_once(self) -> None:
        """Event bus should not register the same handler multiple times."""
        # Given
        event_bus = InMemoryEventBus()
        handler = Mock()
        
        # When
        await event_bus.subscribe(StoreCreated, handler)
        await event_bus.subscribe(StoreCreated, handler)
        
        # Then - handler should only appear once
        assert event_bus._subscribers[StoreCreated].count(handler) == 1


class TestInMemoryEventBusUnsubscribe:
    """Test InMemoryEventBus.unsubscribe() removes handlers correctly."""

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_handler(self) -> None:
        """Event bus should remove handlers when unsubscribed."""
        # Given
        event_bus = InMemoryEventBus()
        handler = Mock()
        await event_bus.subscribe(StoreCreated, handler)
        
        # When
        await event_bus.unsubscribe(StoreCreated, handler)
        
        # Then - handler should be removed
        assert handler not in event_bus._subscribers[StoreCreated]

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_handler_does_not_error(self) -> None:
        """Event bus should handle unsubscribing non-existent handlers gracefully."""
        # Given
        event_bus = InMemoryEventBus()
        handler = Mock()
        
        # When / Then - should not raise
        await event_bus.unsubscribe(StoreCreated, handler)