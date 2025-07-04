import { page } from '@vitest/browser/context';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import InventoryTablePage from './+page.svelte';
import type { InventoryItemWithIngredient } from '$lib/types.js';

describe('Inventory Table Display', () => {
	it('should display correct table headers for inventory columns', async () => {
		// Arrange
		const mockInventory: InventoryItemWithIngredient[] = [
			{
				store_id: 'test-store-id',
				ingredient_id: 'test-ingredient-id',
				ingredient_name: 'Carrots',
				quantity: 2,
				unit: 'lbs',
				notes: 'Fresh from garden',
				added_at: '2024-01-01T00:00:00Z'
			}
		];

		// Act
		render(InventoryTablePage, { props: { inventory: mockInventory } });

		// Assert - Check all required column headers are present in table
		const table = page.getByRole('table');
		await expect.element(table).toBeInTheDocument();

		// Check headers by text content within the table
		const ingredientHeader = table.getByText('Ingredient');
		const quantityHeader = table.getByText('Quantity');
		const unitHeader = table.getByText('Unit');
		const notesHeader = table.getByText('Notes');

		await expect.element(ingredientHeader).toBeInTheDocument();
		await expect.element(quantityHeader).toBeInTheDocument();
		await expect.element(unitHeader).toBeInTheDocument();
		await expect.element(notesHeader).toBeInTheDocument();
	});

	it('should display inventory data in correct table columns', async () => {
		// Arrange
		const mockInventory: InventoryItemWithIngredient[] = [
			{
				store_id: 'test-store-id',
				ingredient_id: 'test-ingredient-id-1',
				ingredient_name: 'Carrots',
				quantity: 2,
				unit: 'lbs',
				notes: 'Fresh from garden',
				added_at: '2024-01-01T00:00:00Z'
			},
			{
				store_id: 'test-store-id',
				ingredient_id: 'test-ingredient-id-2',
				ingredient_name: 'Kale',
				quantity: 1,
				unit: 'bunch',
				notes: null,
				added_at: '2024-01-01T00:00:00Z'
			}
		];

		// Act
		render(InventoryTablePage, { props: { inventory: mockInventory } });

		// Assert - Check first row data
		const carrotCell = page.getByRole('cell', { name: 'Carrots' });
		const quantityCell = page.getByRole('cell', { name: '2' });
		const unitCell = page.getByRole('cell', { name: 'lbs' });
		const notesCell = page.getByRole('cell', { name: 'Fresh from garden' });

		await expect.element(carrotCell).toBeInTheDocument();
		await expect.element(quantityCell).toBeInTheDocument();
		await expect.element(unitCell).toBeInTheDocument();
		await expect.element(notesCell).toBeInTheDocument();

		// Assert - Check second row data
		const kaleCell = page.getByRole('cell', { name: 'Kale' });
		const bunchCell = page.getByRole('cell', { name: 'bunch' });

		await expect.element(kaleCell).toBeInTheDocument();
		await expect.element(bunchCell).toBeInTheDocument();
	});

	it('should display empty state message when no inventory items provided', async () => {
		// Arrange
		const emptyInventory: InventoryItemWithIngredient[] = [];

		// Act
		render(InventoryTablePage, { props: { inventory: emptyInventory } });

		// Assert
		const emptyMessage = page.getByText('No inventory items found.');
		await expect.element(emptyMessage).toBeInTheDocument();

		// Should not show table when empty
		const table = page.getByRole('table');
		await expect.element(table).not.toBeInTheDocument();
	});

	it('should display item count in header', async () => {
		// Arrange
		const mockInventory: InventoryItemWithIngredient[] = [
			{
				store_id: 'test-store-id', ingredient_id: 'test-ingredient-id-1',
				ingredient_name: 'Carrots', quantity: 2, unit: 'lbs',
				notes: null, added_at: '2024-01-01T00:00:00Z'
			},
			{
				store_id: 'test-store-id', ingredient_id: 'test-ingredient-id-2',
				ingredient_name: 'Kale', quantity: 1, unit: 'bunch',
				notes: null, added_at: '2024-01-01T00:00:00Z'
			},
			{
				store_id: 'test-store-id', ingredient_id: 'test-ingredient-id-3',
				ingredient_name: 'Tomatoes', quantity: 3, unit: 'pieces',
				notes: null, added_at: '2024-01-01T00:00:00Z'
			}
		];

		// Act
		render(InventoryTablePage, { props: { inventory: mockInventory } });

		// Assert
		const headerWithCount = page.getByText('Inventory (3 items)');
		await expect.element(headerWithCount).toBeInTheDocument();
	});

	it('should handle missing notes field gracefully', async () => {
		// Arrange
		const mockInventory: InventoryItemWithIngredient[] = [
			{
				store_id: 'test-store-id',
				ingredient_id: 'test-ingredient-id',
				ingredient_name: 'Carrots',
				quantity: 2,
				unit: 'lbs',
				notes: null, // null notes should show as dash
				added_at: '2024-01-01T00:00:00Z'
			}
		];

		// Act
		render(InventoryTablePage, { props: { inventory: mockInventory } });

		// Assert - Should show dash for missing notes
		const dashCell = page.getByRole('cell', { name: '-' });
		await expect.element(dashCell).toBeInTheDocument();
	});

	it('should display multiple inventory items in separate table rows', async () => {
		// Arrange
		const mockInventory: InventoryItemWithIngredient[] = [
			{
				store_id: 'test-store-id', ingredient_id: 'test-ingredient-id-1',
				ingredient_name: 'Carrots', quantity: 2, unit: 'lbs', notes: 'Fresh',
				added_at: '2024-01-01T00:00:00Z'
			},
			{
				store_id: 'test-store-id', ingredient_id: 'test-ingredient-id-2',
				ingredient_name: 'Kale', quantity: 1, unit: 'bunch', notes: 'Organic',
				added_at: '2024-01-01T00:00:00Z'
			},
			{
				store_id: 'test-store-id', ingredient_id: 'test-ingredient-id-3',
				ingredient_name: 'Tomatoes', quantity: 5, unit: 'pieces', notes: null,
				added_at: '2024-01-01T00:00:00Z'
			}
		];

		// Act
		render(InventoryTablePage, { props: { inventory: mockInventory } });

		// Assert - All items should be visible
		await expect.element(page.getByRole('cell', { name: 'Carrots' })).toBeInTheDocument();
		await expect.element(page.getByRole('cell', { name: 'Kale' })).toBeInTheDocument();
		await expect.element(page.getByRole('cell', { name: 'Tomatoes' })).toBeInTheDocument();

		// Check quantities
		await expect.element(page.getByRole('cell', { name: '2' })).toBeInTheDocument();
		await expect.element(page.getByRole('cell', { name: '1' })).toBeInTheDocument();
		await expect.element(page.getByRole('cell', { name: '5' })).toBeInTheDocument();

		// Check units
		await expect.element(page.getByRole('cell', { name: 'lbs' })).toBeInTheDocument();
		await expect.element(page.getByRole('cell', { name: 'bunch' })).toBeInTheDocument();
		await expect.element(page.getByRole('cell', { name: 'pieces' })).toBeInTheDocument();
	});
});
