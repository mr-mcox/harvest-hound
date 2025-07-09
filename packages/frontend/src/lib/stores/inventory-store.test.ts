/**
 * Tests for inventory store with real-time WebSocket integration
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { inventoryStore } from './inventory-store';

// Mock the WebSocket store
vi.mock('../websocket-store', () => ({
	websocketStore: {
		lastMessage: { subscribe: vi.fn(() => vi.fn()) }, // Return unsubscribe function
		connect: vi.fn(),
		disconnect: vi.fn()
	}
}));

// Mock the API
vi.mock('../api', () => ({
	apiGet: vi.fn()
}));

describe('InventoryStore', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		inventoryStore.reset();
	});

	describe('Initial State', () => {
		it('should have correct initial state', () => {
			const stores = get(inventoryStore.stores);
			const loading = get(inventoryStore.loading);
			const error = get(inventoryStore.error);

			expect(stores).toEqual([]);
			expect(loading).toBe(false);
			expect(error).toBeNull();
		});
	});

	describe('Store Management', () => {
		it('should provide reactive stores for state', () => {
			const storeInventory = inventoryStore.getInventoryForStore('test-store-id');
			const inventory = get(storeInventory);

			expect(inventory).toEqual([]);
		});

		it('should clear inventory for specific store', () => {
			// This is a unit test for the clearInventoryForStore method
			expect(() => inventoryStore.clearInventoryForStore('test-id')).not.toThrow();
		});
	});

	describe('WebSocket Integration', () => {
		it('should provide subscription method for WebSocket events', () => {
			// Test that subscribeToWebSocketEvents returns a function
			const unsubscribe = inventoryStore.subscribeToWebSocketEvents();
			expect(typeof unsubscribe).toBe('function');
			
			// Clean up
			unsubscribe();
		});
	});
});