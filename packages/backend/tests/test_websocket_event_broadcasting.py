"""
Tests for WebSocket event broadcasting functionality.

This test suite covers the end-to-end flow of domain events being broadcast
over WebSocket connections when they occur in the system.
"""

from fastapi.testclient import TestClient


class TestWebSocketEventBroadcasting:
    """Test WebSocket event broadcasting integration."""

    def test_store_created_event_broadcasts_to_websocket(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that StoreCreated events are broadcast to WebSocket clients."""
        # Connect to WebSocket before creating store
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Create a store via REST API
            store_data = {
                "name": "Test Store",
                "description": "A test store",
                "infinite_supply": False,
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201

            # Should receive WebSocket message about store creation
            ws_message = websocket.receive_json()

            # Verify the message structure
            assert ws_message["type"] == "StoreCreated"
            assert ws_message["room"] == "default"
            assert "data" in ws_message

            # Verify event data
            event_data = ws_message["data"]
            assert event_data["name"] == "Test Store"
            assert event_data["description"] == "A test store"
            assert event_data["infinite_supply"] is False
            assert "store_id" in event_data
            assert "created_at" in event_data

    def test_inventory_item_added_event_broadcasts_to_websocket(
        self, test_client_with_mocks: TestClient, created_store_id: str
    ) -> None:
        """Test that InventoryItemAdded events are broadcast to WebSocket clients."""
        # Connect to WebSocket before adding inventory
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Add inventory via REST API
            inventory_data = {"inventory_text": "2 lbs carrots, 1 bunch kale"}
            response = test_client_with_mocks.post(
                f"/stores/{created_store_id}/inventory", json=inventory_data
            )
            assert response.status_code == 201

            # Should receive WebSocket messages about inventory items being added
            # We expect multiple messages for multiple items
            messages = []
            for _ in range(2):  # carrots and kale
                ws_message = websocket.receive_json()
                messages.append(ws_message)

            # Check that all messages are InventoryItemAdded events
            for message in messages:
                assert message["type"] == "InventoryItemAdded"
                assert message["room"] == "default"
                assert "data" in message

                event_data = message["data"]
                assert "store_id" in event_data
                assert "ingredient_id" in event_data
                assert "quantity" in event_data
                assert "unit" in event_data
                assert "added_at" in event_data

    def test_multiple_websocket_clients_receive_same_events(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that multiple WebSocket clients receive the same domain events."""
        # Connect two WebSocket clients
        with test_client_with_mocks.websocket_connect("/ws") as websocket1:
            with test_client_with_mocks.websocket_connect("/ws") as websocket2:
                # Create a store via REST API
                store_data = {
                    "name": "Multi-Client Test Store",
                    "description": "Testing multiple clients",
                    "infinite_supply": False,
                }
                response = test_client_with_mocks.post("/stores", json=store_data)
                assert response.status_code == 201

                # Both clients should receive the same event
                message1 = websocket1.receive_json()
                message2 = websocket2.receive_json()

                assert message1["type"] == message2["type"] == "StoreCreated"
                assert message1["room"] == message2["room"] == "default"
                assert message1["data"] == message2["data"]

    def test_websocket_message_format_matches_schema(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that WebSocket messages match the expected schema format."""
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Trigger a domain event
            store_data = {
                "name": "Schema Test Store",
                "description": "Testing message schema",
                "infinite_supply": True,
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201

            # Receive and validate message structure
            ws_message = websocket.receive_json()

            # Should match WebSocketMessage schema
            assert isinstance(ws_message, dict)
            assert "type" in ws_message
            assert "data" in ws_message
            assert "room" in ws_message

            assert isinstance(ws_message["type"], str)
            assert isinstance(ws_message["data"], dict)
            assert isinstance(ws_message["room"], str)
            assert ws_message["room"] == "default"

    def test_store_created_with_inventory_event_broadcasts_to_websocket(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that StoreCreatedWithInventory events are broadcast to WebSocket
        clients."""
        # Connect to WebSocket before creating store with inventory
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Create a store with inventory via REST API (unified creation)
            store_data = {
                "name": "Test Store with Inventory",
                "description": "A test store created with inventory",
                "infinite_supply": False,
                "inventory_text": "2 lbs carrots, 1 bunch kale",
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201

            # Should receive messages: StoreCreated, InventoryItemAdded (2x),
            # StoreCreatedWithInventory
            messages = []
            for _ in range(
                4
            ):  # Expect 4 messages: StoreCreated + 2 InventoryItemAdded +
                # StoreCreatedWithInventory
                ws_message = websocket.receive_json()
                messages.append(ws_message)

            # Find the StoreCreatedWithInventory message
            store_with_inventory_messages = [
                msg
                for msg in messages
                if msg.get("type") == "StoreCreatedWithInventory"
            ]

            assert len(store_with_inventory_messages) == 1, (
                f"Expected 1 StoreCreatedWithInventory event but got message types: "
                f"{[msg.get('type') for msg in messages]}"
            )
            ws_message = store_with_inventory_messages[0]

            # Verify the message structure
            assert ws_message["type"] == "StoreCreatedWithInventory"
            assert ws_message["room"] == "default"
            assert "data" in ws_message

            # Verify event data
            event_data = ws_message["data"]
            assert "store_id" in event_data
            assert event_data["successful_items"] == 2  # carrots and kale
            assert event_data["error_message"] is None
