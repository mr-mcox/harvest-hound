"""
WebSocket event subscriber for broadcasting domain events to WebSocket clients.

This module handles the integration between the event bus and WebSocket connections,
transforming domain events into WebSocket messages and broadcasting them to appropriate rooms.
"""

from typing import Any, Dict

from app.events.domain_events import DomainEvent, InventoryItemAdded, StoreCreated, StoreCreatedWithInventory
from app.infrastructure.websocket_manager import ConnectionManager, WebSocketMessage


class WebSocketEventSubscriber:
    """
    Subscribes to domain events and broadcasts them to WebSocket clients.
    
    This class handles the transformation of domain events into WebSocket messages
    and manages the broadcasting to appropriate room connections.
    """
    
    def __init__(self, connection_manager: ConnectionManager) -> None:
        """
        Initialize the WebSocket event subscriber.
        
        Args:
            connection_manager: The connection manager for WebSocket broadcasting
        """
        self.connection_manager = connection_manager
    
    async def handle_store_created(self, event: StoreCreated) -> None:
        """
        Handle StoreCreated events and broadcast to WebSocket clients.
        
        Args:
            event: The StoreCreated domain event
        """
        # Transform domain event to WebSocket message
        ws_message = WebSocketMessage(
            type="StoreCreated",
            data={
                "store_id": str(event.store_id),
                "name": event.name,
                "description": event.description,
                "infinite_supply": event.infinite_supply,
                "created_at": event.created_at.isoformat(),
            },
            room="default"
        )
        
        # Broadcast to all connections in default room
        await self.connection_manager.broadcast_to_room(ws_message, "default")
    
    async def handle_inventory_item_added(self, event: InventoryItemAdded) -> None:
        """
        Handle InventoryItemAdded events and broadcast to WebSocket clients.
        
        Args:
            event: The InventoryItemAdded domain event
        """
        # Transform domain event to WebSocket message
        ws_message = WebSocketMessage(
            type="InventoryItemAdded",
            data={
                "store_id": str(event.store_id),
                "ingredient_id": str(event.ingredient_id),
                "quantity": event.quantity,
                "unit": event.unit,
                "notes": event.notes,
                "added_at": event.added_at.isoformat(),
            },
            room="default"
        )
        
        # Broadcast to all connections in default room
        await self.connection_manager.broadcast_to_room(ws_message, "default")
    
    async def handle_store_created_with_inventory(self, event: StoreCreatedWithInventory) -> None:
        """
        Handle StoreCreatedWithInventory events and broadcast to WebSocket clients.
        
        Args:
            event: The StoreCreatedWithInventory domain event
        """
        # Transform domain event to WebSocket message
        ws_message = WebSocketMessage(
            type="StoreCreatedWithInventory",
            data={
                "store_id": str(event.store_id),
                "successful_items": event.successful_items,
                "error_message": event.error_message,
            },
            room="default"
        )
        
        # Broadcast to all connections in default room
        await self.connection_manager.broadcast_to_room(ws_message, "default")
    
    def transform_domain_event_to_websocket_message(
        self, event: DomainEvent
    ) -> WebSocketMessage:
        """
        Transform a domain event into a WebSocket message.
        
        Args:
            event: The domain event to transform
            
        Returns:
            WebSocket message ready for broadcasting
        """
        event_type = event.__class__.__name__
        
        # Convert event to dict, handling UUID and datetime serialization
        event_data = event.model_dump()
        
        # Convert UUID fields to strings
        for key, value in event_data.items():
            if hasattr(value, 'hex'):  # UUID objects
                event_data[key] = str(value)
            elif hasattr(value, 'isoformat'):  # datetime objects
                event_data[key] = value.isoformat()
        
        return WebSocketMessage(
            type=event_type,
            data=event_data,
            room="default"
        )