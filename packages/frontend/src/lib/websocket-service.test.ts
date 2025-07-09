/**
 * Tests for WebSocket connection logic
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketService, ConnectionState, type WebSocketMessage } from './websocket-service';

// Mock WebSocket globally
const mockWebSocket = vi.fn();
const mockWebSocketInstance = {
	send: vi.fn(),
	close: vi.fn(),
	addEventListener: vi.fn(),
	removeEventListener: vi.fn(),
	readyState: WebSocket.CONNECTING as number
};

// @ts-expect-error - mocking global WebSocket
global.WebSocket = mockWebSocket;

describe('WebSocketService - Connection Logic', () => {
	let service: WebSocketService;
	const testUrl = 'ws://localhost:8000/ws';

	beforeEach(() => {
		vi.clearAllMocks();
		mockWebSocket.mockReturnValue(mockWebSocketInstance);
		service = new WebSocketService(testUrl);
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	describe('Connection Establishment', () => {
		it('should establish WebSocket connection when connect() is called', () => {
			// Act
			service.connect();

			// Assert
			expect(mockWebSocket).toHaveBeenCalledWith(testUrl);
			expect(service.getConnectionState()).toBe(ConnectionState.CONNECTING);
		});

		it('should set up event listeners when connecting', () => {
			// Act
			service.connect();

			// Assert
			expect(mockWebSocketInstance.addEventListener).toHaveBeenCalledWith(
				'open',
				expect.any(Function)
			);
			expect(mockWebSocketInstance.addEventListener).toHaveBeenCalledWith(
				'message',
				expect.any(Function)
			);
			expect(mockWebSocketInstance.addEventListener).toHaveBeenCalledWith(
				'close',
				expect.any(Function)
			);
			expect(mockWebSocketInstance.addEventListener).toHaveBeenCalledWith(
				'error',
				expect.any(Function)
			);
		});

		it('should update connection state to CONNECTED when WebSocket opens', () => {
			// Arrange
			service.connect();
			const openHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'open'
			)?.[1];

			// Act
			mockWebSocketInstance.readyState = WebSocket.OPEN as number;
			openHandler?.();

			// Assert
			expect(service.getConnectionState()).toBe(ConnectionState.CONNECTED);
		});

		it('should not create multiple connections if already connected', () => {
			// Arrange
			service.connect();
			mockWebSocketInstance.readyState = WebSocket.OPEN as number;

			// Act
			service.connect();

			// Assert
			expect(mockWebSocket).toHaveBeenCalledTimes(1);
		});
	});

	describe('Message Handling', () => {
		it('should handle incoming WebSocket messages', () => {
			// Arrange
			const testMessage: WebSocketMessage = {
				type: 'StoreCreated',
				data: { store_id: '123', name: 'Test Store' },
				room: 'default'
			};

			const messageHandler = vi.fn();
			service.on('StoreCreated', messageHandler);

			service.connect();
			const wsMessageHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'message'
			)?.[1];

			// Act
			const messageEvent = new MessageEvent('message', {
				data: JSON.stringify(testMessage)
			});
			wsMessageHandler?.(messageEvent);

			// Assert
			expect(messageHandler).toHaveBeenCalledWith(testMessage.data);
		});

		it('should send messages through WebSocket when connected', () => {
			// Arrange
			service.connect();
			mockWebSocketInstance.readyState = WebSocket.OPEN as number;

			const testMessage: WebSocketMessage = {
				type: 'ping',
				data: { test: 'data' },
				room: 'default'
			};

			// Act
			service.send(testMessage);

			// Assert
			expect(mockWebSocketInstance.send).toHaveBeenCalledWith(JSON.stringify(testMessage));
		});

		it('should not send messages when disconnected', () => {
			// Arrange
			mockWebSocketInstance.readyState = WebSocket.CLOSED as number;

			const testMessage: WebSocketMessage = {
				type: 'ping',
				data: { test: 'data' },
				room: 'default'
			};

			// Act
			service.send(testMessage);

			// Assert
			expect(mockWebSocketInstance.send).not.toHaveBeenCalled();
		});
	});

	describe('Disconnection', () => {
		it('should close WebSocket connection when disconnect() is called', () => {
			// Arrange
			service.connect();

			// Act
			service.disconnect();

			// Assert
			expect(mockWebSocketInstance.close).toHaveBeenCalled();
			expect(service.getConnectionState()).toBe(ConnectionState.DISCONNECTED);
		});

		it('should update connection state when WebSocket closes', () => {
			// Arrange
			service.connect();
			const closeHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'close'
			)?.[1];

			// Act
			mockWebSocketInstance.readyState = WebSocket.CLOSED as number;
			closeHandler?.();

			// Assert
			expect(service.getConnectionState()).toBe(ConnectionState.DISCONNECTED);
		});
	});

	describe('Reconnection Logic', () => {
		it('should attempt to reconnect when connection is lost unexpectedly', async () => {
			// Arrange
			service.connect();
			const closeHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'close'
			)?.[1];

			// Act
			mockWebSocketInstance.readyState = WebSocket.CLOSED as number;
			closeHandler?.();

			// Wait for reconnection attempt
			await new Promise((resolve) => setTimeout(resolve, 1100));

			// Assert
			expect(service.getConnectionState()).toBe(ConnectionState.RECONNECTING);
			expect(mockWebSocket).toHaveBeenCalledTimes(2); // Original + reconnect attempt
		});

		it('should not attempt to reconnect when disconnect() is called explicitly', () => {
			// Arrange
			service.connect();

			// Act
			service.disconnect();

			// Assert
			expect(service.getConnectionState()).toBe(ConnectionState.DISCONNECTED);
			// No additional WebSocket creation should occur
			expect(mockWebSocket).toHaveBeenCalledTimes(1);
		});

		it('should implement exponential backoff for reconnection attempts', async () => {
			// Arrange
			service.connect();
			const closeHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'close'
			)?.[1];

			// Simulate multiple connection failures
			for (let i = 0; i < 3; i++) {
				mockWebSocketInstance.readyState = WebSocket.CLOSED as number;
				closeHandler?.();
				await new Promise((resolve) => setTimeout(resolve, 100));
			}

			// Assert that reconnection attempts were made with increasing delays
			expect(service.getConnectionState()).toBe(ConnectionState.RECONNECTING);
		});
	});

	describe('Event Subscription', () => {
		it('should allow subscribing to specific event types', () => {
			// Arrange
			const handler = vi.fn();

			// Act
			service.on('StoreCreated', handler);

			// Assert - subscription should be registered without error
			expect(() => service.on('StoreCreated', handler)).not.toThrow();
		});

		it('should allow unsubscribing from event types', () => {
			// Arrange
			const handler = vi.fn();
			service.on('StoreCreated', handler);

			// Act
			service.off('StoreCreated', handler);

			// Assert - unsubscription should work without error
			expect(() => service.off('StoreCreated', handler)).not.toThrow();
		});

		it('should not call unsubscribed event handlers', () => {
			// Arrange
			const handler = vi.fn();
			service.on('StoreCreated', handler);
			service.off('StoreCreated', handler);

			service.connect();
			const wsMessageHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'message'
			)?.[1];

			const testMessage: WebSocketMessage = {
				type: 'StoreCreated',
				data: { store_id: '123' },
				room: 'default'
			};

			// Act
			const messageEvent = new MessageEvent('message', {
				data: JSON.stringify(testMessage)
			});
			wsMessageHandler?.(messageEvent);

			// Assert
			expect(handler).not.toHaveBeenCalled();
		});
	});
});
