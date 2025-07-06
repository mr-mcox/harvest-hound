<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { apiGet } from '$lib/api';
	import type { InventoryItemWithIngredient } from '$lib/types.js';

	let inventory: InventoryItemWithIngredient[] = [];
	let loading = true;
	let error = '';
	let storeId = '';

	onMount(async () => {
		storeId = $page.params.id;
		await loadInventory();
	});

	async function loadInventory() {
		loading = true;
		error = '';
		try {
			const response = await apiGet(`/stores/${storeId}/inventory`);
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			inventory = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load inventory';
		} finally {
			loading = false;
		}
	}
</script>

<div class="container mx-auto p-4">
	<div class="mb-4">
		<a href="/stores" class="btn variant-ghost">← Back to Stores</a>
	</div>

	<div class="card">
		<div class="card-header">
			<h2 class="text-lg font-semibold">
				{#if loading}
					Loading Inventory...
				{:else}
					Inventory ({inventory.length} items)
				{/if}
			</h2>
		</div>

		{#if loading}
			<div class="card-body text-center">
				<div class="placeholder animate-pulse">Loading inventory items...</div>
			</div>
		{:else if error}
			<div class="card-body">
				<div class="alert variant-filled-error">
					<div class="alert-message">
						<p>{error}</p>
					</div>
				</div>
			</div>
		{:else if inventory.length === 0}
			<div class="card-body text-center text-gray-500">
				<p>No inventory items found.</p>
				<div class="mt-4">
					<a href="/stores/{storeId}/upload" class="btn variant-filled-primary">Upload Items</a>
				</div>
			</div>
		{:else}
			<div class="table-container">
				<table class="table-hover table">
					<thead>
						<tr>
							<th>Ingredient</th>
							<th>Quantity</th>
							<th>Unit</th>
							<th>Notes</th>
						</tr>
					</thead>
					<tbody>
						{#each inventory as item (item.ingredient_name + item.added_at)}
							<tr>
								<td class="font-medium">{item.ingredient_name}</td>
								<td>{item.quantity}</td>
								<td>{item.unit}</td>
								<td>{item.notes || '-'}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="card-footer">
				<a href="/stores/{storeId}/upload" class="btn variant-filled-primary">Upload More Items</a>
			</div>
		{/if}
	</div>
</div>
