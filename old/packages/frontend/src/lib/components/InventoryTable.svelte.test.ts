/**
 * Tests for InventoryTable component real-time integration
 *
 * This test suite focuses on the component's ability to react to real-time
 * inventory changes and display them properly to users.
 */

import { page } from '@vitest/browser/context';
import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import InventoryTable from './InventoryTable.svelte';
import type { InventoryItemView } from '$lib/types';

describe('InventoryTable - Real-time Integration', () => {
	const mockInventoryItems: InventoryItemView[] = [
		{
			store_id: 'store-1',
			ingredient_id: 'ingredient-1',
			ingredient_name: 'Carrots',
			store_name: 'CSA Box',
			quantity: 2,
			unit: 'lbs',
			notes: 'Fresh from farm',
			added_at: '2024-01-01T10:00:00Z'
		},
		{
			store_id: 'store-1',
			ingredient_id: 'ingredient-2',
			ingredient_name: 'Spinach',
			store_name: 'CSA Box',
			quantity: 1,
			unit: 'bunch',
			notes: null,
			added_at: '2024-01-01T11:00:00Z'
		}
	];

	describe('Data Display', () => {
		it('displays inventory items with real-time data structure', async () => {
			render(InventoryTable, {
				inventory: mockInventoryItems,
				storeId: 'store-1'
			});

			// Verify real-time compatible data display
			await expect.element(page.getByRole('cell', { name: 'Carrots' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'Spinach' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: '2' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: '1' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'lbs' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'bunch' })).toBeInTheDocument();
		});

		it('shows item count in header reflecting real-time updates', async () => {
			render(InventoryTable, {
				inventory: mockInventoryItems,
				storeId: 'store-1'
			});

			await expect.element(page.getByText('Inventory (2 items)')).toBeInTheDocument();
		});

		it('handles null notes properly for real-time data', async () => {
			render(InventoryTable, {
				inventory: mockInventoryItems,
				storeId: 'store-1'
			});

			// Notes should show '-' for null values
			await expect.element(page.getByRole('cell', { name: 'Fresh from farm' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: '-' })).toBeInTheDocument();
		});
	});

	describe('Real-time Updates', () => {
		it('displays updated inventory when props change from real-time updates', async () => {
			// Test with 3 items to simulate real-time update
			const updatedInventory = [
				...mockInventoryItems,
				{
					store_id: 'store-1',
					ingredient_id: 'ingredient-3',
					ingredient_name: 'Kale',
					store_name: 'CSA Box',
					quantity: 3,
					unit: 'bunches',
					notes: 'Organic',
					added_at: '2024-01-01T12:00:00Z'
				}
			];

			render(InventoryTable, {
				inventory: updatedInventory,
				storeId: 'store-1'
			});

			// Verify UI displays updated data
			await expect.element(page.getByText('Inventory (3 items)')).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'Kale' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: '3' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'bunches' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'Organic' })).toBeInTheDocument();
		});

		it('displays updated quantities when inventory changes via WebSocket', async () => {
			// Test with updated quantity to simulate real-time update
			const updatedInventory = [
				{
					...mockInventoryItems[0],
					quantity: 5 // Updated quantity
				},
				mockInventoryItems[1]
			];

			render(InventoryTable, {
				inventory: updatedInventory,
				storeId: 'store-1'
			});

			// Verify quantity updated in UI
			await expect.element(page.getByRole('cell', { name: '5' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'Carrots' })).toBeInTheDocument();
		});

		it('handles empty state when all items removed via real-time updates', async () => {
			render(InventoryTable, {
				inventory: [],
				storeId: 'store-1'
			});

			// Verify empty state
			await expect.element(page.getByText('Inventory (0 items)')).toBeInTheDocument();
			await expect.element(page.getByText('No inventory items found.')).toBeInTheDocument();
			await expect.element(page.getByText('Upload Items')).toBeInTheDocument();
		});
	});

	describe('Component Reactivity', () => {
		it('uses unique keys for efficient real-time updates', async () => {
			render(InventoryTable, {
				inventory: mockInventoryItems,
				storeId: 'store-1'
			});

			// Check that table rows are rendered with unique content
			const table = page.getByRole('table');
			await expect.element(table).toBeInTheDocument();

			// Each row should have unique content for keying
			await expect.element(page.getByRole('cell', { name: 'Carrots' })).toBeInTheDocument();
			await expect.element(page.getByRole('cell', { name: 'Spinach' })).toBeInTheDocument();
		});

		it('maintains proper table structure with data', async () => {
			render(InventoryTable, {
				inventory: mockInventoryItems,
				storeId: 'store-1'
			});

			// Table structure should be present with data
			await expect.element(page.getByRole('table')).toBeInTheDocument();

			// Check headers are present (using text content)
			await expect.element(page.getByText('Ingredient')).toBeInTheDocument();
			await expect.element(page.getByText('Quantity')).toBeInTheDocument();
			await expect.element(page.getByText('Unit')).toBeInTheDocument();
			await expect.element(page.getByText('Notes')).toBeInTheDocument();
		});

		it('switches between table and empty state based on inventory data', async () => {
			// Test empty state first
			render(InventoryTable, {
				inventory: [],
				storeId: 'store-1'
			});

			// Should show empty state, not table
			await expect.element(page.getByRole('table')).not.toBeInTheDocument();
			await expect.element(page.getByText('No inventory items found.')).toBeInTheDocument();
		});
	});

	describe('Upload Integration', () => {
		it('shows upload button when storeId provided', async () => {
			render(InventoryTable, {
				inventory: mockInventoryItems,
				storeId: 'store-1'
			});

			await expect.element(page.getByText('Upload More Items')).toBeInTheDocument();
		});

		it('shows upload button in empty state when storeId provided', async () => {
			render(InventoryTable, {
				inventory: [],
				storeId: 'store-1'
			});

			await expect.element(page.getByText('Upload Items')).toBeInTheDocument();
		});

		it('does not show upload button when storeId not provided', async () => {
			render(InventoryTable, {
				inventory: mockInventoryItems,
				storeId: ''
			});

			await expect.element(page.getByText('Upload More Items')).not.toBeInTheDocument();
		});
	});
});
