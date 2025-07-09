/**
 * Frontend integration tests with real API calls to backend
 * These tests run against a live backend instance with mocked LLM
 */

import { beforeAll, beforeEach, describe, it, expect, vi } from 'vitest';

// Mock the navigation module for testing
vi.mock('$app/navigation', () => ({
	goto: vi.fn()
}));

// Test configuration
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Type definitions for API responses
interface Store {
	store_id: string;
	name: string;
	description: string;
	infinite_supply: boolean;
	item_count?: number;
}

interface InventoryItem {
	ingredient_name: string;
	quantity: number;
	unit: string;
	added_at: string;
	notes?: string;
}

// Helper function to make API calls
async function apiCall(endpoint: string, options: RequestInit = {}) {
	const response = await fetch(`${API_BASE_URL}${endpoint}`, {
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		},
		...options
	});
	return response;
}

// Helper function to wait for backend to be ready
async function waitForBackend(maxAttempts = 30) {
	for (let i = 0; i < maxAttempts; i++) {
		try {
			const response = await fetch(`${API_BASE_URL}/health`);
			if (response.ok) {
				return true;
			}
		} catch {
			// Backend not ready yet
		}
		await new Promise((resolve) => setTimeout(resolve, 1000));
	}
	throw new Error('Backend not ready after maximum attempts');
}

describe.skip('Frontend Integration Tests', () => {
	beforeAll(async () => {
		// Wait for backend to be ready
		await waitForBackend();
	}, 30000); // Increased timeout

	describe('Store Management Integration', () => {
		let testStoreId: string;

		beforeEach(async () => {
			// Clean state - create a fresh test store
			const response = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify({
					name: 'Frontend Test Store',
					description: 'Store for frontend integration testing',
					infinite_supply: false
				})
			});
			expect(response.status).toBe(201);
			const storeData = await response.json();
			testStoreId = storeData.store_id;
		});

		it('should create store through API and handle response', async () => {
			const storeData = {
				name: 'Integration Test Store',
				description: 'Test store created through API',
				infinite_supply: false
			};

			const response = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify(storeData)
			});

			expect(response.status).toBe(201);
			const responseData = await response.json();

			expect(responseData).toHaveProperty('store_id');
			expect(responseData.name).toBe(storeData.name);
			expect(responseData.description).toBe(storeData.description);
			expect(responseData.infinite_supply).toBe(storeData.infinite_supply);
		});

		it('should retrieve store list through API', async () => {
			const response = await apiCall('/stores');
			expect(response.status).toBe(200);

			const stores = (await response.json()) as Store[];
			expect(Array.isArray(stores)).toBe(true);
			expect(stores.length).toBeGreaterThan(0);

			// Should find our test store
			const testStore = stores.find((store) => store.store_id === testStoreId);
			expect(testStore).toBeDefined();
			expect(testStore!.name).toBe('Frontend Test Store');
		});

		it('should handle store creation validation errors', async () => {
			// Try to create store with missing name
			const response = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify({})
			});

			expect(response.status).toBe(422);
			const errorData = await response.json();
			expect(errorData).toHaveProperty('detail');
		});
	});

	describe('Inventory Management Integration', () => {
		let testStoreId: string;

		beforeEach(async () => {
			// Create a test store
			const response = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify({
					name: 'Inventory Test Store',
					description: 'Store for inventory testing'
				})
			});
			const storeData = await response.json();
			testStoreId = storeData.store_id;
		});

		it('should upload inventory through API with mocked LLM', async () => {
			const inventoryText = '2 lbs carrots, 1 bunch kale';

			const response = await apiCall(`/stores/${testStoreId}/inventory`, {
				method: 'POST',
				body: JSON.stringify({ inventory_text: inventoryText })
			});

			expect(response.status).toBe(201);
			const uploadResult = await response.json();

			expect(uploadResult.success).toBe(true);
			expect(uploadResult.items_added).toBe(2);
			expect(uploadResult.errors).toEqual([]);
		});

		it('should retrieve inventory through API after upload', async () => {
			// First upload some inventory
			await apiCall(`/stores/${testStoreId}/inventory`, {
				method: 'POST',
				body: JSON.stringify({
					inventory_text: '3.5 oz organic spinach, 2.25 cups whole milk, 1/2 cup olive oil'
				})
			});

			// Then retrieve it
			const response = await apiCall(`/stores/${testStoreId}/inventory`);
			expect(response.status).toBe(200);

			const inventory = (await response.json()) as InventoryItem[];
			expect(Array.isArray(inventory)).toBe(true);
			expect(inventory.length).toBe(3);

			// Verify inventory items have expected structure
			inventory.forEach((item) => {
				expect(item).toHaveProperty('ingredient_name');
				expect(item).toHaveProperty('quantity');
				expect(item).toHaveProperty('unit');
				expect(item).toHaveProperty('added_at');
				expect(typeof item.quantity).toBe('number');
				expect(item.quantity).toBeGreaterThan(0);
			});
		});

		it('should handle empty inventory upload', async () => {
			const response = await apiCall(`/stores/${testStoreId}/inventory`, {
				method: 'POST',
				body: JSON.stringify({ inventory_text: '' })
			});

			expect(response.status).toBe(201);
			const uploadResult = await response.json();

			expect(uploadResult.success).toBe(true);
			expect(uploadResult.items_added).toBe(0);
		});

		it('should handle inventory upload to non-existent store', async () => {
			const fakeStoreId = '00000000-0000-0000-0000-000000000000';

			const response = await apiCall(`/stores/${fakeStoreId}/inventory`, {
				method: 'POST',
				body: JSON.stringify({ inventory_text: '1 apple' })
			});

			expect(response.status).toBe(404);
		});
	});

	describe('Full Workflow Integration', () => {
		it('should complete full store creation and inventory workflow', async () => {
			// Step 1: Create store
			const storeResponse = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify({
					name: 'Full Workflow Store',
					description: 'Testing complete workflow',
					infinite_supply: false
				})
			});
			expect(storeResponse.status).toBe(201);
			const store = await storeResponse.json();
			const storeId = store.store_id;

			// Step 2: Upload inventory
			const uploadResponse = await apiCall(`/stores/${storeId}/inventory`, {
				method: 'POST',
				body: JSON.stringify({
					inventory_text: '1 head cabbage, 2 pound beet, 1 bunch radish, 3 ounce lettuce mix'
				})
			});
			expect(uploadResponse.status).toBe(201);
			const uploadResult = await uploadResponse.json();
			expect(uploadResult.items_added).toBe(4);

			// Step 3: Verify store list shows updated item count
			const storesResponse = await apiCall('/stores');
			expect(storesResponse.status).toBe(200);
			const stores = (await storesResponse.json()) as Store[];

			const updatedStore = stores.find((s) => s.store_id === storeId);
			expect(updatedStore).toBeDefined();
			expect(updatedStore!.item_count).toBe(4);

			// Step 4: Verify inventory details
			const inventoryResponse = await apiCall(`/stores/${storeId}/inventory`);
			expect(inventoryResponse.status).toBe(200);
			const inventory = (await inventoryResponse.json()) as InventoryItem[];
			expect(inventory.length).toBe(4);

			// Verify specific items
			const cabbage = inventory.find((item) =>
				item.ingredient_name.toLowerCase().includes('cabbage')
			);
			const beet = inventory.find((item) => item.ingredient_name.toLowerCase().includes('beet'));

			expect(cabbage).toBeDefined();
			expect(cabbage!.quantity).toBe(1);
			expect(cabbage!.unit).toBe('head');

			expect(beet).toBeDefined();
			expect(beet!.quantity).toBe(2);
			expect(beet!.unit).toBe('pound');
		});

		it('should handle multiple stores with separate inventories', async () => {
			// Create two stores
			const store1Response = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify({ name: 'Store One' })
			});
			const store2Response = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify({ name: 'Store Two' })
			});

			const store1 = await store1Response.json();
			const store2 = await store2Response.json();

			// Add different inventory to each
			await apiCall(`/stores/${store1.store_id}/inventory`, {
				method: 'POST',
				body: JSON.stringify({ inventory_text: '2 lbs carrots, 1 bunch kale' })
			});

			await apiCall(`/stores/${store2.store_id}/inventory`, {
				method: 'POST',
				body: JSON.stringify({ inventory_text: '1 apple' })
			});

			// Verify separate inventories
			const inventory1Response = await apiCall(`/stores/${store1.store_id}/inventory`);
			const inventory2Response = await apiCall(`/stores/${store2.store_id}/inventory`);

			const inventory1 = await inventory1Response.json();
			const inventory2 = await inventory2Response.json();

			expect(inventory1.length).toBe(2);
			expect(inventory2.length).toBe(1);

			// Verify store list shows correct counts
			const storesResponse = await apiCall('/stores');
			const stores = (await storesResponse.json()) as Store[];

			const updatedStore1 = stores.find((s) => s.store_id === store1.store_id);
			const updatedStore2 = stores.find((s) => s.store_id === store2.store_id);

			expect(updatedStore1!.item_count).toBe(2);
			expect(updatedStore2!.item_count).toBe(1);
		});
	});

	describe('Error Handling Integration', () => {
		it('should handle network errors gracefully', async () => {
			// Test with invalid endpoint
			const response = await fetch(`${API_BASE_URL}/invalid-endpoint`);
			expect(response.status).toBe(404);
		});

		it('should handle malformed JSON requests', async () => {
			const response = await apiCall('/stores', {
				method: 'POST',
				body: 'invalid json'
			});
			expect(response.status).toBe(422);
		});

		it('should handle CORS for frontend requests', async () => {
			const response = await apiCall('/health');
			expect(response.status).toBe(200);

			// Should not have CORS errors (would throw in browser)
			const healthData = await response.json();
			expect(healthData.status).toBe('healthy');
		});
	});

	describe('Performance Integration', () => {
		it('should handle rapid API requests efficiently', async () => {
			const startTime = Date.now();

			// Make multiple concurrent requests
			const promises = [];
			for (let i = 0; i < 5; i++) {
				promises.push(apiCall('/health'));
			}

			const responses = await Promise.all(promises);
			const endTime = Date.now();

			// All should succeed
			responses.forEach((response) => {
				expect(response.status).toBe(200);
			});

			// Should complete reasonably quickly
			expect(endTime - startTime).toBeLessThan(2000);
		});

		it('should handle large inventory uploads efficiently', async () => {
			// Create store
			const storeResponse = await apiCall('/stores', {
				method: 'POST',
				body: JSON.stringify({ name: 'Performance Test Store' })
			});
			const store = await storeResponse.json();

			// Large inventory text
			const largeInventoryText =
				'apple, banana, carrot, date, eggplant, fig, grape, herb, lemon, jalapeño'.repeat(10);

			const startTime = Date.now();
			const uploadResponse = await apiCall(`/stores/${store.store_id}/inventory`, {
				method: 'POST',
				body: JSON.stringify({ inventory_text: largeInventoryText })
			});
			const endTime = Date.now();

			expect(uploadResponse.status).toBe(201);
			// Should complete in reasonable time even with mocked LLM
			expect(endTime - startTime).toBeLessThan(3000);
		});
	});
});
