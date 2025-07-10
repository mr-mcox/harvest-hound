/**
 * Tests for WebSocket service - Core connection management
 *
 * Tests essential connection logic with mocked WebSocket for fast execution.
 * No actual network connections - focuses on connection state management.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketService, ConnectionState, type WebSocketMessage } from './websocket-service';

// Mock WebSocket to prevent actual connections
const mockWebSocketInstance = {
	send: vi.fn(),
	close: vi.fn(),
	addEventListener: vi.fn(),
	removeEventListener: vi.fn(),
	readyState: WebSocket.CONNECTING as number
};

const mockWebSocket = vi.fn(() => mockWebSocketInstance);

// @ts-expect-error - mocking global WebSocket for tests
global.WebSocket = mockWebSocket;

describe('WebSocketService - Core Connection Management', () => {
	let service: WebSocketService;
	const testUrl = 'ws://test-url'; // No actual connection

	beforeEach(() => {
		vi.clearAllMocks();
		// Reset mock instance state
		mockWebSocketInstance.readyState = WebSocket.CONNECTING;
		service = new WebSocketService(testUrl);
	});

	afterEach(() => {
		service.disconnect();
		vi.clearAllMocks();
	});

	describe('Core Connection Logic', () => {
		it('establishes WebSocket connection when connect() called', () => {
			service.connect();

			expect(mockWebSocket).toHaveBeenCalledWith(testUrl);
			expect(service.getConnectionState()).toBe(ConnectionState.CONNECTING);
		});

		it('sets up required event listeners', () => {
			service.connect();

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

		it('updates state to CONNECTED when socket opens', () => {
			service.connect();
			const openHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'open'
			)?.[1];

			mockWebSocketInstance.readyState = WebSocket.OPEN as number;
			openHandler?.();

			expect(service.getConnectionState()).toBe(ConnectionState.CONNECTED);
		});

		it('prevents multiple connections', () => {
			service.connect();
			mockWebSocketInstance.readyState = WebSocket.OPEN as number;
			service.connect();

			expect(mockWebSocket).toHaveBeenCalledTimes(1);
		});
	});

	describe('Message Handling - Core Event Logic', () => {
		it('handles incoming WebSocket messages', () => {
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

			const messageEvent = new MessageEvent('message', {
				data: JSON.stringify(testMessage)
			});
			wsMessageHandler?.(messageEvent);

			expect(messageHandler).toHaveBeenCalledWith(testMessage.data);
		});

		it('sends messages when connected', () => {
			service.connect();
			mockWebSocketInstance.readyState = WebSocket.OPEN as number;

			const testMessage: WebSocketMessage = {
				type: 'ping',
				data: { test: 'data' },
				room: 'default'
			};

			// Act
			service.send(testMessage);

			expect(mockWebSocketInstance.send).toHaveBeenCalledWith(JSON.stringify(testMessage));
		});

		it('does not send when disconnected', () => {
			mockWebSocketInstance.readyState = WebSocket.CLOSED as number;

			const testMessage: WebSocketMessage = {
				type: 'ping',
				data: { test: 'data' },
				room: 'default'
			};

			service.send(testMessage);

			expect(mockWebSocketInstance.send).not.toHaveBeenCalled();
		});
	});

	describe('Connection Lifecycle', () => {
		it('closes connection when disconnect() called', () => {
			service.connect();
			service.disconnect();

			expect(mockWebSocketInstance.close).toHaveBeenCalled();
			expect(service.getConnectionState()).toBe(ConnectionState.DISCONNECTED);
		});

		it('updates state when WebSocket closes', () => {
			service.connect();
			const closeHandler = mockWebSocketInstance.addEventListener.mock.calls.find(
				(call) => call[0] === 'close'
			)?.[1];

			mockWebSocketInstance.readyState = WebSocket.CLOSED as number;
			closeHandler?.();

			expect(service.getConnectionState()).toBe(ConnectionState.DISCONNECTED);
		});
	});

	describe('Event Subscription - Core Event Bus', () => {
		it('allows subscribing to event types', () => {
			const handler = vi.fn();

			expect(() => service.on('StoreCreated', handler)).not.toThrow();
		});

		it('allows unsubscribing from event types', () => {
			const handler = vi.fn();
			service.on('StoreCreated', handler);

			expect(() => service.off('StoreCreated', handler)).not.toThrow();
		});

		it('does not call unsubscribed handlers', () => {
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

			const messageEvent = new MessageEvent('message', {
				data: JSON.stringify(testMessage)
			});
			wsMessageHandler?.(messageEvent);

			expect(handler).not.toHaveBeenCalled();
		});
	});
});
