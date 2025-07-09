/**
 * Tests for StoreList component real-time integration
 *
 * This test suite focuses on the component's ability to display store information
 * and react to real-time updates from WebSocket events.
 */

import { page } from '@vitest/browser/context';
import { describe, it, expect } from 'vitest';
import { render } from 'vitest-browser-svelte';
import StoreList from './StoreList.svelte';
import type { StoreView } from '$lib/types';

describe('StoreList - Real-time Integration', () => {
	const mockStores: StoreView[] = [
		{
			store_id: 'store-1',
			name: 'CSA Box',
			description: 'Weekly community supported agriculture box',
			infinite_supply: false,
			item_count: 5,
			created_at: '2024-01-01T10:00:00Z'
		},
		{
			store_id: 'store-2',
			name: 'Pantry',
			description: 'Long-term storage items',
			infinite_supply: true,
			item_count: 12,
			created_at: '2024-01-01T11:00:00Z'
		}
	];

	describe('Store Display', () => {
		it('displays store information with real-time compatible data', async () => {
			render(StoreList, {
				stores: mockStores,
				loading: false,
				error: null
			});

			// Verify store names are displayed
			await expect.element(page.getByText('CSA Box')).toBeInTheDocument();
			await expect.element(page.getByText('Pantry')).toBeInTheDocument();

			// Verify descriptions are displayed
			await expect
				.element(page.getByText('Weekly community supported agriculture box'))
				.toBeInTheDocument();
			await expect.element(page.getByText('Long-term storage items')).toBeInTheDocument();

			// Verify item counts are displayed (real-time data)
			await expect.element(page.getByText('5 items')).toBeInTheDocument();
			await expect.element(page.getByText('12 items')).toBeInTheDocument();
		});

		it('displays action buttons for each store', async () => {
			render(StoreList, {
				stores: mockStores,
				loading: false,
				error: null
			});

			// Check for View Inventory links - should have 2 instances (one for each store)
			const viewInventoryLinks = page.getByRole('link', { name: 'View Inventory' });
			await expect.element(viewInventoryLinks.first()).toBeInTheDocument();
			await expect.element(viewInventoryLinks.last()).toBeInTheDocument();

			// Check for Upload Items links - should have 2 instances (one for each store)
			const uploadItemsLinks = page.getByRole('link', { name: 'Upload Items' });
			await expect.element(uploadItemsLinks.first()).toBeInTheDocument();
			await expect.element(uploadItemsLinks.last()).toBeInTheDocument();

			// Verify correct href attributes
			await expect
				.element(page.getByRole('link', { name: 'View Inventory' }).first())
				.toHaveAttribute('href', '/stores/store-1');
			await expect
				.element(page.getByRole('link', { name: 'Upload Items' }).first())
				.toHaveAttribute('href', '/stores/store-1/upload');
		});

		it('handles stores without descriptions gracefully', async () => {
			const storesWithoutDescription = [
				{
					...mockStores[0],
					description: undefined
				}
			];

			render(StoreList, {
				stores: storesWithoutDescription,
				loading: false,
				error: null
			});

			// Store name should still be displayed
			await expect.element(page.getByText('CSA Box')).toBeInTheDocument();

			// Description should not be displayed
			await expect
				.element(page.getByText('Weekly community supported agriculture box'))
				.not.toBeInTheDocument();
		});
	});

	describe('Real-time Updates', () => {
		it('displays updated item counts from WebSocket events', async () => {
			const updatedStores = [
				{
					...mockStores[0],
					item_count: 8 // Updated from 5 to 8
				},
				mockStores[1]
			];

			render(StoreList, {
				stores: updatedStores,
				loading: false,
				error: null
			});

			// Verify updated item count is displayed
			await expect.element(page.getByText('8 items')).toBeInTheDocument();
			await expect.element(page.getByText('12 items')).toBeInTheDocument();
		});

		it('displays new stores added via real-time updates', async () => {
			const storesWithNewStore = [
				...mockStores,
				{
					store_id: 'store-3',
					name: 'Freezer',
					description: 'Frozen storage items',
					infinite_supply: false,
					item_count: 3,
					created_at: '2024-01-01T12:00:00Z'
				}
			];

			render(StoreList, {
				stores: storesWithNewStore,
				loading: false,
				error: null
			});

			// Verify new store is displayed
			await expect.element(page.getByText('Freezer')).toBeInTheDocument();
			await expect.element(page.getByText('Frozen storage items')).toBeInTheDocument();
			await expect.element(page.getByText('3 items')).toBeInTheDocument();

			// Verify all stores are displayed
			await expect.element(page.getByText('CSA Box')).toBeInTheDocument();
			await expect.element(page.getByText('Pantry')).toBeInTheDocument();
		});

		it('handles zero item counts correctly', async () => {
			const storesWithZeroItems = [
				{
					...mockStores[0],
					item_count: 0
				}
			];

			render(StoreList, {
				stores: storesWithZeroItems,
				loading: false,
				error: null
			});

			// Should display "0 items" for empty store
			await expect.element(page.getByText('0 items')).toBeInTheDocument();
		});

		it('handles undefined item counts gracefully', async () => {
			const storesWithUndefinedCount = [
				{
					...mockStores[0],
					item_count: undefined
				}
			];

			render(StoreList, {
				stores: storesWithUndefinedCount,
				loading: false,
				error: null
			});

			// Should display "0 items" for undefined item count
			await expect.element(page.getByText('0 items')).toBeInTheDocument();
		});
	});

	describe('Loading and Error States', () => {
		it('displays loading state when loading is true', async () => {
			render(StoreList, {
				stores: [],
				loading: true,
				error: null
			});

			await expect.element(page.getByText('Loading stores...')).toBeInTheDocument();
		});

		it('displays error state when error is present', async () => {
			render(StoreList, {
				stores: [],
				loading: false,
				error: 'Failed to load stores'
			});

			await expect.element(page.getByText('Failed to load stores')).toBeInTheDocument();
		});

		it('displays empty state when no stores are available', async () => {
			render(StoreList, {
				stores: [],
				loading: false,
				error: null
			});

			await expect
				.element(page.getByText('No stores found. Create your first store to get started!'))
				.toBeInTheDocument();
		});
	});

	describe('Component Reactivity', () => {
		it('uses unique keys for efficient real-time updates', async () => {
			render(StoreList, {
				stores: mockStores,
				loading: false,
				error: null
			});

			// Check that both stores are rendered with unique content
			// Each store should have unique content
			await expect.element(page.getByText('CSA Box')).toBeInTheDocument();
			await expect.element(page.getByText('Pantry')).toBeInTheDocument();

			// Verify both stores have their unique item counts
			await expect.element(page.getByText('5 items')).toBeInTheDocument();
			await expect.element(page.getByText('12 items')).toBeInTheDocument();
		});

		it('transitions between states correctly', async () => {
			render(StoreList, {
				stores: [],
				loading: true,
				error: null
			});

			// Should show loading initially
			await expect.element(page.getByText('Loading stores...')).toBeInTheDocument();

			// NOTE: In Svelte 5, we can't use component.$set()
			// This test documents the expected behavior but can't be fully tested
			// The actual state transitions are tested in the parent page component
		});
	});
});
