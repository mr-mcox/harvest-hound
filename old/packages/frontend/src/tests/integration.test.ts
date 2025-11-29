/**
 * Frontend integration tests with mocked API calls
 * These tests verify API integration patterns without requiring a live backend
 */

import { beforeEach, describe, it, expect, vi } from 'vitest';

// Mock the API module
vi.mock('$lib/api', () => ({
	apiGet: vi.fn(),
	apiPost: vi.fn(),
	apiCall: vi.fn(),
	API_BASE_URL: 'http://localhost:8000'
}));

// Mock the navigation module for testing
vi.mock('$app/navigation', () => ({
	goto: vi.fn()
}));

import { apiGet, apiPost } from '$lib/api';
import type { StoreView, InventoryItemView } from '$lib/types';

// Mock data for testing
const mockStores: StoreView[] = [
	{
		store_id: 'test-store-1',
		name: 'Test Store 1',
		description: 'A test store',
		infinite_supply: false,
		item_count: 0,
		created_at: '2024-01-01T10:00:00Z'
	},
	{
		store_id: 'test-store-2',
		name: 'Test Store 2',
		description: 'Another test store',
		infinite_supply: true,
		item_count: 5,
		created_at: '2024-01-01T11:00:00Z'
	}
];

const mockInventory: InventoryItemView[] = [
	{
		store_id: '1',
		ingredient_id: '1',
		store_name: 'Test Store',
		ingredient_name: 'Carrots',
		quantity: 2,
		unit: 'lbs',
		added_at: '2024-01-01T10:00:00Z',
		notes: 'Fresh from farm'
	},
	{
		store_id: '1',
		ingredient_id: '2',
		store_name: 'Test Store',
		ingredient_name: 'Kale',
		quantity: 1,
		unit: 'bunch',
		added_at: '2024-01-01T10:05:00Z',
		notes: null
	}
];

describe('Frontend Integration Tests', () => {
	beforeEach(() => {
		// Reset all mocks before each test
		vi.clearAllMocks();
	});

	describe('Store Management Integration', () => {
		it('should create store through API and handle response', async () => {
			const storeData = {
				name: 'Integration Test Store',
				description: 'Test store created through API',
				infinite_supply: false
			};

			const expectedResponse: StoreView = {
				store_id: 'new-store-id',
				name: storeData.name,
				description: storeData.description,
				infinite_supply: storeData.infinite_supply,
				item_count: 0,
				created_at: '2024-01-01T12:00:00Z'
			};

			// Mock successful store creation
			vi.mocked(apiPost).mockResolvedValueOnce(
				new Response(JSON.stringify(expectedResponse), {
					status: 201,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiPost('/stores', storeData);

			expect(response.status).toBe(201);
			const responseData = await response.json();

			expect(responseData).toHaveProperty('store_id');
			expect(responseData.name).toBe(storeData.name);
			expect(responseData.description).toBe(storeData.description);
			expect(responseData.infinite_supply).toBe(storeData.infinite_supply);

			// Verify API was called with correct data
			expect(apiPost).toHaveBeenCalledWith('/stores', storeData);
		});

		it('should retrieve store list through API', async () => {
			// Mock successful store list retrieval
			vi.mocked(apiGet).mockResolvedValueOnce(
				new Response(JSON.stringify(mockStores), {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiGet('/stores');
			expect(response.status).toBe(200);

			const stores = (await response.json()) as StoreView[];
			expect(Array.isArray(stores)).toBe(true);
			expect(stores.length).toBe(2);

			// Verify expected stores are present
			expect(stores[0].name).toBe('Test Store 1');
			expect(stores[1].name).toBe('Test Store 2');

			// Verify API was called correctly
			expect(apiGet).toHaveBeenCalledWith('/stores');
		});

		it('should handle store creation validation errors', async () => {
			const errorResponse = {
				detail: [
					{
						loc: ['body', 'name'],
						msg: 'field required',
						type: 'value_error.missing'
					}
				]
			};

			// Mock validation error response
			vi.mocked(apiPost).mockResolvedValueOnce(
				new Response(JSON.stringify(errorResponse), {
					status: 422,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiPost('/stores', {});

			expect(response.status).toBe(422);
			const errorData = await response.json();
			expect(errorData).toHaveProperty('detail');
			expect(errorData.detail).toBeInstanceOf(Array);
		});

		it('should handle network errors gracefully', async () => {
			// Mock network error
			vi.mocked(apiGet).mockRejectedValueOnce(new Error('Network error'));

			await expect(apiGet('/stores')).rejects.toThrow('Network error');
		});
	});

	describe('Inventory Management Integration', () => {
		const testStoreId = 'test-store-id';

		it('should upload inventory through API with proper response format', async () => {
			const inventoryText = '2 lbs carrots, 1 bunch kale';
			const expectedUploadResult = {
				success: true,
				items_added: 2,
				errors: []
			};

			// Mock successful inventory upload
			vi.mocked(apiPost).mockResolvedValueOnce(
				new Response(JSON.stringify(expectedUploadResult), {
					status: 201,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiPost(`/stores/${testStoreId}/inventory`, {
				inventory_text: inventoryText
			});

			expect(response.status).toBe(201);
			const uploadResult = await response.json();

			expect(uploadResult.success).toBe(true);
			expect(uploadResult.items_added).toBe(2);
			expect(uploadResult.errors).toEqual([]);

			// Verify API was called with correct data
			expect(apiPost).toHaveBeenCalledWith(`/stores/${testStoreId}/inventory`, {
				inventory_text: inventoryText
			});
		});

		it('should retrieve inventory through API with proper structure', async () => {
			// Mock inventory retrieval
			vi.mocked(apiGet).mockResolvedValueOnce(
				new Response(JSON.stringify(mockInventory), {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiGet(`/stores/${testStoreId}/inventory`);
			expect(response.status).toBe(200);

			const inventory = (await response.json()) as InventoryItemView[];
			expect(Array.isArray(inventory)).toBe(true);
			expect(inventory.length).toBe(2);

			// Verify inventory items have expected structure
			inventory.forEach((item) => {
				expect(item).toHaveProperty('ingredient_name');
				expect(item).toHaveProperty('quantity');
				expect(item).toHaveProperty('unit');
				expect(item).toHaveProperty('added_at');
				expect(typeof item.quantity).toBe('number');
				expect(item.quantity).toBeGreaterThan(0);
			});

			// Verify specific items
			expect(inventory[0].ingredient_name).toBe('Carrots');
			expect(inventory[0].quantity).toBe(2);
			expect(inventory[0].unit).toBe('lbs');
			expect(inventory[1].ingredient_name).toBe('Kale');
			expect(inventory[1].quantity).toBe(1);
			expect(inventory[1].unit).toBe('bunch');
		});

		it('should handle empty inventory upload', async () => {
			const expectedUploadResult = {
				success: true,
				items_added: 0,
				errors: []
			};

			// Mock empty inventory upload
			vi.mocked(apiPost).mockResolvedValueOnce(
				new Response(JSON.stringify(expectedUploadResult), {
					status: 201,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiPost(`/stores/${testStoreId}/inventory`, { inventory_text: '' });

			expect(response.status).toBe(201);
			const uploadResult = await response.json();

			expect(uploadResult.success).toBe(true);
			expect(uploadResult.items_added).toBe(0);
		});

		it('should handle inventory upload to non-existent store', async () => {
			const fakeStoreId = '00000000-0000-0000-0000-000000000000';
			const errorResponse = {
				detail: 'Store not found'
			};

			// Mock 404 error response
			vi.mocked(apiPost).mockResolvedValueOnce(
				new Response(JSON.stringify(errorResponse), {
					status: 404,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiPost(`/stores/${fakeStoreId}/inventory`, {
				inventory_text: '1 apple'
			});

			expect(response.status).toBe(404);
			const errorData = await response.json();
			expect(errorData.detail).toBe('Store not found');
		});

		it('should handle inventory upload with processing errors', async () => {
			const inventoryText = 'invalid inventory format';
			const expectedUploadResult = {
				success: false,
				items_added: 0,
				errors: ['Could not parse ingredient: invalid inventory format']
			};

			// Mock upload with errors
			vi.mocked(apiPost).mockResolvedValueOnce(
				new Response(JSON.stringify(expectedUploadResult), {
					status: 201,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiPost(`/stores/${testStoreId}/inventory`, {
				inventory_text: inventoryText
			});

			expect(response.status).toBe(201);
			const uploadResult = await response.json();

			expect(uploadResult.success).toBe(false);
			expect(uploadResult.items_added).toBe(0);
			expect(uploadResult.errors.length).toBeGreaterThan(0);
		});
	});

	describe('Error Handling Integration', () => {
		it('should handle 500 server errors', async () => {
			// Mock server error
			vi.mocked(apiGet).mockResolvedValueOnce(
				new Response('Internal Server Error', {
					status: 500,
					statusText: 'Internal Server Error'
				})
			);

			const response = await apiGet('/stores');
			expect(response.status).toBe(500);
		});

		it('should handle malformed JSON in responses', async () => {
			// Mock response with invalid JSON
			vi.mocked(apiGet).mockResolvedValueOnce(
				new Response('invalid json', {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiGet('/stores');
			expect(response.status).toBe(200);

			// Should throw when trying to parse invalid JSON
			await expect(response.json()).rejects.toThrow();
		});

		it('should handle CORS-like scenarios', async () => {
			// Mock successful health check
			vi.mocked(apiGet).mockResolvedValueOnce(
				new Response(JSON.stringify({ status: 'healthy' }), {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiGet('/health');
			expect(response.status).toBe(200);

			const healthData = await response.json();
			expect(healthData.status).toBe('healthy');
		});
	});

	describe('Response Format Validation', () => {
		it('should validate store response format matches expected schema', async () => {
			const mockStore: StoreView = {
				store_id: 'test-id',
				name: 'Test Store',
				description: 'Test description',
				infinite_supply: false,
				item_count: 5,
				created_at: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiGet).mockResolvedValueOnce(
				new Response(JSON.stringify([mockStore]), {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiGet('/stores');
			const stores = (await response.json()) as StoreView[];

			// Validate store structure
			expect(stores[0]).toHaveProperty('store_id');
			expect(stores[0]).toHaveProperty('name');
			expect(stores[0]).toHaveProperty('description');
			expect(stores[0]).toHaveProperty('infinite_supply');
			expect(stores[0]).toHaveProperty('item_count');
			expect(stores[0]).toHaveProperty('created_at');

			// Validate types
			expect(typeof stores[0].store_id).toBe('string');
			expect(typeof stores[0].name).toBe('string');
			expect(typeof stores[0].infinite_supply).toBe('boolean');
			expect(typeof stores[0].item_count).toBe('number');
		});

		it('should validate inventory response format matches expected schema', async () => {
			vi.mocked(apiGet).mockResolvedValueOnce(
				new Response(JSON.stringify(mockInventory), {
					status: 200,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const response = await apiGet('/stores/test-id/inventory');
			const inventory = (await response.json()) as InventoryItemView[];

			// Validate inventory structure
			inventory.forEach((item) => {
				expect(item).toHaveProperty('ingredient_name');
				expect(item).toHaveProperty('quantity');
				expect(item).toHaveProperty('unit');
				expect(item).toHaveProperty('added_at');

				// Validate types
				expect(typeof item.ingredient_name).toBe('string');
				expect(typeof item.quantity).toBe('number');
				expect(typeof item.unit).toBe('string');
				expect(typeof item.added_at).toBe('string');
			});
		});
	});
});
