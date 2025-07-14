<script lang="ts">
	import type { InventoryItemView } from '$lib/types.js';

	export let inventory: InventoryItemView[];
	export let storeId: string = '';
</script>

<div class="card" data-testid="inventory-table">
	<div class="card-header">
		<h2 class="text-lg font-semibold">
			Inventory ({inventory.length} items)
		</h2>
	</div>

	{#if inventory.length === 0}
		<div class="card-body text-center text-gray-500">
			<p>No inventory items found.</p>
			{#if storeId}
				<div class="mt-4">
					<a
						href="/stores/{storeId}/upload"
						class="btn variant-filled-primary"
						data-testid="add-inventory-button">Upload Items</a
					>
				</div>
			{/if}
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
						<tr data-testid="inventory-row">
							<td class="font-medium">{item.ingredient_name}</td>
							<td>{item.quantity}</td>
							<td>{item.unit}</td>
							<td>{item.notes || '-'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		{#if storeId}
			<div class="card-footer">
				<a
					href="/stores/{storeId}/upload"
					class="btn variant-filled-primary"
					data-testid="add-inventory-button">Upload More Items</a
				>
			</div>
		{/if}
	{/if}
</div>
