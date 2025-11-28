"""
Integration test demonstrating the complete WebSocket real-time update flow.

This test validates the end-to-end user scenario where actions performed via
REST API result in real-time updates being pushed to WebSocket clients.
"""

from fastapi.testclient import TestClient


class TestWebSocketIntegration:
    """Test complete WebSocket integration scenarios."""

    def test_complete_store_and_inventory_workflow_with_websocket_updates(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test complete workflow: create store, add inventory, all via WebSocket."""
        # Connect to WebSocket to receive real-time updates
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Step 1: Create a store via REST API
            store_data = {
                "name": "Real-time CSA Box",
                "description": "Testing real-time updates",
                "infinite_supply": False,
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201
            store_id = response.json()["store_id"]

            # Should receive WebSocket notifications from unified creation
            store_created_event = websocket.receive_json()
            assert store_created_event["type"] == "StoreCreated"
            assert store_created_event["data"]["name"] == "Real-time CSA Box"
            assert store_created_event["data"]["store_id"] == store_id

            # Should also receive StoreCreatedWithInventory event (unified flow)
            unified_event = websocket.receive_json()
            assert unified_event["type"] == "StoreCreatedWithInventory"
            assert unified_event["data"]["store_id"] == store_id
            assert (
                unified_event["data"]["successful_items"] == 0
            )  # No inventory provided
            assert unified_event["data"]["error_message"] is None

            # Step 2: Add inventory to the store
            inventory_data = {"inventory_text": "2 lbs carrots, 1 bunch kale"}
            response = test_client_with_mocks.post(
                f"/stores/{store_id}/inventory", json=inventory_data
            )
            assert response.status_code == 201

            # Should receive WebSocket notifications for each inventory item
            inventory_events = []
            for _ in range(2):  # carrots and kale
                event = websocket.receive_json()
                inventory_events.append(event)

            # Verify all inventory events
            for event in inventory_events:
                assert event["type"] == "InventoryItemAdded"
                assert event["data"]["store_id"] == store_id
                assert event["room"] == "default"

            # Step 3: Verify we can still receive regular WebSocket messages
            ping_message = {"type": "ping", "data": {"test": "integration"}}
            websocket.send_json(ping_message)

            echo_response = websocket.receive_json()
            assert echo_response["type"] == "echo"
            assert echo_response["data"]["test"] == "integration"

            # Demonstrate that the WebSocket connection remains active
            # and can handle both domain events and direct messages

    def test_multiple_websocket_clients_receive_same_domain_events(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that multiple WebSocket clients receive the same domain events."""
        # Connect two WebSocket clients
        with test_client_with_mocks.websocket_connect("/ws") as websocket1:
            with test_client_with_mocks.websocket_connect("/ws") as websocket2:
                # Trigger a domain event via REST API
                store_data = {
                    "name": "Multi-client Test Store",
                    "description": "Testing multi-client event broadcasting",
                    "infinite_supply": False,
                }
                response = test_client_with_mocks.post("/stores", json=store_data)
                assert response.status_code == 201
                store_id = response.json()["store_id"]

                # Both clients should receive the same StoreCreated event
                store_event1 = websocket1.receive_json()
                store_event2 = websocket2.receive_json()

                # Verify both events are identical
                assert store_event1["type"] == "StoreCreated"
                assert store_event2["type"] == "StoreCreated"
                assert store_event1["data"] == store_event2["data"]
                assert store_event1["data"]["store_id"] == store_id
                assert store_event2["data"]["store_id"] == store_id
                assert store_event1["room"] == "default"
                assert store_event2["room"] == "default"

    def test_rest_api_actions_trigger_websocket_events(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that REST API actions trigger corresponding WebSocket events."""
        # Connect WebSocket client to receive events
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Test 1: Store creation via REST API
            store_data = {
                "name": "REST API Test Store",
                "description": "Testing REST to WebSocket flow",
                "infinite_supply": False,
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201
            store_id = response.json()["store_id"]

            # Verify WebSocket receives StoreCreated event
            store_event = websocket.receive_json()
            assert store_event["type"] == "StoreCreated"
            assert store_event["data"]["store_id"] == store_id
            assert store_event["data"]["name"] == "REST API Test Store"
            assert store_event["room"] == "default"

            # Also consume the StoreCreatedWithInventory event from unified flow
            unified_event = websocket.receive_json()
            assert unified_event["type"] == "StoreCreatedWithInventory"
            assert unified_event["data"]["store_id"] == store_id

            # Test 2: Inventory addition via REST API
            inventory_data = {"inventory_text": "2 lbs carrots, 1 bunch kale"}
            response = test_client_with_mocks.post(
                f"/stores/{store_id}/inventory", json=inventory_data
            )
            assert response.status_code == 201

            # Verify WebSocket receives InventoryItemAdded events
            inventory_events = []
            for _ in range(2):  # carrots and kale
                event = websocket.receive_json()
                inventory_events.append(event)

            # Verify all inventory events are correct
            for event in inventory_events:
                assert event["type"] == "InventoryItemAdded"
                assert event["data"]["store_id"] == store_id
                assert event["room"] == "default"
                # Verify the item has expected structure
                assert "ingredient_id" in event["data"]
                assert "quantity" in event["data"]
                assert "added_at" in event["data"]

    def test_websocket_connection_lifecycle_scenarios(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test WebSocket connection lifecycle: connect, disconnect, reconnect."""
        # Test 1: Basic connection lifecycle
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Verify connection is established
            store_data = {
                "name": "Connection Test Store",
                "description": "Testing connection lifecycle",
                "infinite_supply": False,
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201

            # Should receive the event
            event = websocket.receive_json()
            assert event["type"] == "StoreCreated"
            assert event["data"]["name"] == "Connection Test Store"
            assert event["room"] == "default"

        # Connection is now closed (exited context manager)

        # Test 2: Reconnection works
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Verify reconnection works by sending a message
            ping_message = {"type": "ping", "data": {"reconnect": "test"}}
            websocket.send_json(ping_message)

            echo_response = websocket.receive_json()
            assert echo_response["type"] == "echo"
            assert echo_response["data"]["reconnect"] == "test"

            # Verify reconnected client can still receive domain events
            store_data = {
                "name": "Reconnected Store",
                "description": "Testing reconnection functionality",
                "infinite_supply": False,
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201

            # Should receive the event on reconnected client
            event = websocket.receive_json()
            assert event["type"] == "StoreCreated"
            assert event["data"]["name"] == "Reconnected Store"
            assert event["room"] == "default"

        # Test 3: Multiple connect/disconnect cycles
        for cycle in range(3):
            with test_client_with_mocks.websocket_connect("/ws") as websocket:
                # Test basic functionality in each cycle
                ping_message = {"type": "ping", "data": {"cycle": cycle}}
                websocket.send_json(ping_message)

                echo_response = websocket.receive_json()
                assert echo_response["type"] == "echo"
                assert echo_response["data"]["cycle"] == cycle

    def test_rapid_events_maintain_correct_sequence_across_clients(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that rapid domain events maintain correct sequence across multiple
        clients."""
        # Connect two WebSocket clients
        with test_client_with_mocks.websocket_connect("/ws") as websocket1:
            with test_client_with_mocks.websocket_connect("/ws") as websocket2:
                # Create stores rapidly and verify order
                store_names = ["Store A", "Store B", "Store C"]
                created_store_ids = []

                # Create stores in rapid succession
                for name in store_names:
                    store_data = {
                        "name": name,
                        "description": f"Rapid creation test - {name}",
                        "infinite_supply": False,
                    }
                    response = test_client_with_mocks.post("/stores", json=store_data)
                    assert response.status_code == 201
                    created_store_ids.append(response.json()["store_id"])

                # Collect events from both clients
                events_client1 = []
                events_client2 = []

                # Each store creation now emits 2 events: StoreCreated +
                # StoreCreatedWithInventory
                for _ in range(len(store_names) * 2):
                    event1 = websocket1.receive_json()
                    event2 = websocket2.receive_json()
                    events_client1.append(event1)
                    events_client2.append(event2)

                # Verify events are identical across clients
                assert len(events_client1) == len(events_client2)
                for event1, event2 in zip(events_client1, events_client2):
                    # Events can be either StoreCreated or StoreCreatedWithInventory
                    assert event1["type"] in [
                        "StoreCreated",
                        "StoreCreatedWithInventory",
                    ]
                    assert event2["type"] in [
                        "StoreCreated",
                        "StoreCreatedWithInventory",
                    ]
                    assert (
                        event1["type"] == event2["type"]
                    )  # Same type for both clients
                    assert event1["data"] == event2["data"]
                    assert event1["room"] == "default"
                    assert event2["room"] == "default"

                # Verify StoreCreated events maintain creation order
                store_created_events_client1 = [
                    e for e in events_client1 if e["type"] == "StoreCreated"
                ]
                store_created_events_client2 = [
                    e for e in events_client2 if e["type"] == "StoreCreated"
                ]
                assert len(store_created_events_client1) == len(store_names)
                assert len(store_created_events_client2) == len(store_names)

                for i, (event1, event2) in enumerate(
                    zip(store_created_events_client1, store_created_events_client2)
                ):
                    assert event1["data"]["name"] == store_names[i]
                    assert event2["data"]["name"] == store_names[i]
                    assert event1["data"]["store_id"] == created_store_ids[i]
                    assert event2["data"]["store_id"] == created_store_ids[i]
