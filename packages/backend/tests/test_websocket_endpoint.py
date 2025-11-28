"""
Tests for WebSocket endpoint functionality.

This test suite covers WebSocket connection handling, handshake, error handling,
and message exchange functionality.
"""

from fastapi.testclient import TestClient


class TestWebSocketEndpoint:
    """Test WebSocket endpoint connection and communication."""

    def test_websocket_connection_accepted(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that WebSocket connections are accepted at /ws endpoint."""
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # If we get here, the connection was accepted
            assert websocket is not None

    def test_websocket_joins_default_room(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that WebSocket connections automatically join the default room."""
        with test_client_with_mocks.websocket_connect("/ws"):
            # The connection should be in the default room
            # We'll verify this by checking the connection manager state
            # This will be implemented when we add the endpoint
            pass

    def test_websocket_handles_disconnection_gracefully(
        self, test_client_with_mocks: TestClient
    ) -> None:
        """Test that WebSocket disconnections are handled gracefully."""
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Connection should be established
            assert websocket is not None

        # After context manager exits, disconnection should be handled gracefully
        # No exceptions should be raised

    def test_websocket_message_echo(self, test_client_with_mocks: TestClient) -> None:
        """Test that WebSocket can send and receive messages."""
        with test_client_with_mocks.websocket_connect("/ws") as websocket:
            # Send a test message
            test_message = {"type": "ping", "data": {"message": "hello"}}
            websocket.send_json(test_message)

            # Receive the response
            response = websocket.receive_json()

            # Should receive an echo or acknowledgment
            assert response is not None
            assert "type" in response
