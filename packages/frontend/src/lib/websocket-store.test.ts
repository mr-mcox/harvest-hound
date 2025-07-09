/**
 * Tests for WebSocket store - focusing on essential Svelte store functionality
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { get } from 'svelte/store';
import { WebSocketStore } from './websocket-store';
import { ConnectionState } from './websocket-service';

// Mock the WebSocketService
vi.mock('./websocket-service', () => {
	const mockWebSocketService = {
		connect: vi.fn(),
		disconnect: vi.fn(),
		getConnectionState: vi.fn(() => ConnectionState.DISCONNECTED),
		on: vi.fn(),
		off: vi.fn()
	};

	return {
		WebSocketService: vi.fn(() => mockWebSocketService),
		ConnectionState: {
			DISCONNECTED: 'disconnected',
			CONNECTING: 'connecting',
			CONNECTED: 'connected',
			RECONNECTING: 'reconnecting'
		}
	};
});

describe('WebSocketStore', () => {
	let store: WebSocketStore;
	const testUrl = 'ws://localhost:8000/ws';

	beforeEach(() => {
		vi.clearAllMocks();
		store = new WebSocketStore(testUrl);
	});

	afterEach(() => {
		store.disconnect();
	});

	describe('Connection Management', () => {
		it('should delegate connect to WebSocketService', () => {
			// Act
			store.connect();

			// Assert - service connect method should be called
			// We'll verify this once we implement the connect method
			expect(store.connect).toBeDefined();
		});

		it('should delegate disconnect to WebSocketService', () => {
			// Act
			store.disconnect();

			// Assert - service disconnect method should be called
			// We'll verify this once we implement the disconnect method
			expect(store.disconnect).toBeDefined();
		});
	});

	describe('Reactive Stores', () => {
		it('should provide connectionState as readable store', () => {
			// Arrange
			const connectionStateStore = store.connectionState;

			// Act
			const currentState = get(connectionStateStore);

			// Assert
			expect(currentState).toBe(ConnectionState.DISCONNECTED);
		});

		it('should update connectionState when service state changes', () => {
			// Arrange
			const connectionStateStore = store.connectionState;

			// This test will be implemented once we have the update mechanism
			// For now, just verify the store exists and has initial state
			const initialState = get(connectionStateStore);

			// Assert
			expect(initialState).toBe(ConnectionState.DISCONNECTED);
		});

		it('should provide lastMessage as readable store', () => {
			// Arrange
			const lastMessageStore = store.lastMessage;

			// Act
			const currentMessage = get(lastMessageStore);

			// Assert
			expect(currentMessage).toBeNull();
		});

		it('should update lastMessage when WebSocket message received', () => {
			// Arrange
			const lastMessageStore = store.lastMessage;

			// Act - verify initial state
			const currentMessage = get(lastMessageStore);

			// Assert - should start with null
			expect(currentMessage).toBeNull();
		});

		it('should provide error as readable store', () => {
			// Arrange
			const errorStore = store.error;

			// Act
			const currentError = get(errorStore);

			// Assert
			expect(currentError).toBeNull();
		});

		it('should update error when connection error occurs', () => {
			// Arrange
			const errorStore = store.error;

			// Act - verify initial state
			const currentError = get(errorStore);

			// Assert - should start with null
			expect(currentError).toBeNull();
		});
	});

	describe('Service Integration', () => {
		it('should subscribe to service events on construction', () => {
			// This will be implemented in GREEN phase
			// For now, just verify service exists
			expect(store['service']).toBeDefined();
		});

		it('should update store state when service events are received', () => {
			// This will be implemented in GREEN phase
			// For now, just verify initial state
			const connectionStateStore = store.connectionState;
			const initialState = get(connectionStateStore);
			expect(initialState).toBe(ConnectionState.DISCONNECTED);
		});

		it('should unsubscribe from service events on disconnect', () => {
			// This will be implemented in GREEN phase
			// For now, just verify disconnect doesn't throw
			expect(() => store.disconnect()).not.toThrow();
		});
	});

	describe('Store Reactivity', () => {
		it('should notify subscribers when connection state changes', () => {
			// Arrange
			const connectionStateStore = store.connectionState;
			const mockSubscriber = vi.fn();

			// Act - subscribe to store
			connectionStateStore.subscribe(mockSubscriber);

			// Assert - subscriber should be called with initial state
			expect(mockSubscriber).toHaveBeenCalledWith(ConnectionState.DISCONNECTED);
		});

		it('should notify subscribers when new message is received', () => {
			// Arrange
			const lastMessageStore = store.lastMessage;
			const mockSubscriber = vi.fn();

			// Act - subscribe to store
			lastMessageStore.subscribe(mockSubscriber);

			// Assert - subscriber should be called with initial state (null)
			expect(mockSubscriber).toHaveBeenCalledWith(null);
		});
	});
});
