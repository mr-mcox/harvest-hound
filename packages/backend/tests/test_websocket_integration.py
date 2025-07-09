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
                "infinite_supply": False
            }
            response = test_client_with_mocks.post("/stores", json=store_data)
            assert response.status_code == 201
            store_id = response.json()["store_id"]
            
            # Should immediately receive WebSocket notification
            store_event = websocket.receive_json()
            assert store_event["type"] == "StoreCreated"
            assert store_event["data"]["name"] == "Real-time CSA Box"
            assert store_event["data"]["store_id"] == store_id
            
            # Step 2: Add inventory to the store
            inventory_data = {"inventory_text": "2 lbs carrots, 1 bunch kale"}
            response = test_client_with_mocks.post(
                f"/stores/{store_id}/inventory", 
                json=inventory_data
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
                    "infinite_supply": False
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
                "infinite_supply": False
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
            
            # Test 2: Inventory addition via REST API
            inventory_data = {"inventory_text": "2 lbs carrots, 1 bunch kale"}
            response = test_client_with_mocks.post(
                f"/stores/{store_id}/inventory", 
                json=inventory_data
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