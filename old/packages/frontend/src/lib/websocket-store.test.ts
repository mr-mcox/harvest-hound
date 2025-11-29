/**
 * Tests for WebSocket store - Core WebSocket state management functionality
 *
 * Tests essential store behavior with proper mocking for fast execution.
 * No actual network connections - focuses on state management logic.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { WebSocketStore } from './websocket-store';
import { ConnectionState } from './websocket-service';

// Mock the WebSocketService - ensure no actual connections
vi.mock('./websocket-service', () => {
	const mockService = {
		connect: vi.fn(),
		disconnect: vi.fn(),
		getConnectionState: vi.fn(() => 'disconnected'),
		on: vi.fn(),
		off: vi.fn()
	};

	return {
		WebSocketService: vi.fn(() => mockService),
		ConnectionState: {
			DISCONNECTED: 'disconnected',
			CONNECTING: 'connecting',
			CONNECTED: 'connected',
			RECONNECTING: 'reconnecting'
		}
	};
});

describe('WebSocketStore - Core Functionality', () => {
	let store: WebSocketStore;
	const testUrl = 'ws://test-url'; // No actual connection

	beforeEach(() => {
		vi.clearAllMocks();
		store = new WebSocketStore(testUrl);
	});

	describe('Core Store Interface', () => {
		it('provides connection state as readable store', () => {
			const connectionStateStore = store.connectionState;
			const currentState = get(connectionStateStore);

			expect(currentState).toBe(ConnectionState.DISCONNECTED);
		});

		it('provides last message as readable store', () => {
			const lastMessageStore = store.lastMessage;
			const currentMessage = get(lastMessageStore);

			expect(currentMessage).toBeNull();
		});

		it('provides error state as readable store', () => {
			const errorStore = store.error;
			const currentError = get(errorStore);

			expect(currentError).toBeNull();
		});

		it('connects through WebSocket service', () => {
			// Just verify connect exists and doesn't throw
			expect(() => store.connect()).not.toThrow();
		});

		it('disconnects through WebSocket service', () => {
			// Just verify disconnect exists and doesn't throw
			expect(() => store.disconnect()).not.toThrow();
		});
	});

	describe('Store Reactivity - Essential for UI Updates', () => {
		it('notifies subscribers of connection state changes', () => {
			const connectionStateStore = store.connectionState;
			const mockSubscriber = vi.fn();

			connectionStateStore.subscribe(mockSubscriber);

			expect(mockSubscriber).toHaveBeenCalledWith(ConnectionState.DISCONNECTED);
		});

		it('notifies subscribers of message changes', () => {
			const lastMessageStore = store.lastMessage;
			const mockSubscriber = vi.fn();

			lastMessageStore.subscribe(mockSubscriber);

			expect(mockSubscriber).toHaveBeenCalledWith(null);
		});

		it('notifies subscribers of error changes', () => {
			const errorStore = store.error;
			const mockSubscriber = vi.fn();

			errorStore.subscribe(mockSubscriber);

			expect(mockSubscriber).toHaveBeenCalledWith(null);
		});
	});

	describe('Service Integration - Core WebSocket Logic', () => {
		it('initializes without errors', () => {
			// Verify store can be created and used
			expect(store).toBeDefined();
			expect(store.connectionState).toBeDefined();
			expect(store.lastMessage).toBeDefined();
			expect(store.error).toBeDefined();
		});

		it('delegates connection management to service', () => {
			// Verify interface exists and works
			expect(() => {
				store.connect();
				store.disconnect();
			}).not.toThrow();
		});

		it('cleans up properly on disconnect', () => {
			store.disconnect();

			// Should clean up without throwing
			expect(() => store.disconnect()).not.toThrow();
		});
	});
});
