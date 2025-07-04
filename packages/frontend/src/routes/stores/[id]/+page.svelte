<script lang="ts">
	export let inventory: Array<{
		ingredient_name: string;
		quantity: number;
		unit: string;
		notes?: string;
	}> = [];
</script>

<div class="container mx-auto p-4">
	<div class="card">
		<div class="card-header">
			<h2 class="text-lg font-semibold">Inventory ({inventory.length} items)</h2>
		</div>

		{#if inventory.length === 0}
			<div class="card-body text-center text-gray-500">
				<p>No inventory items found.</p>
			</div>
		{:else}
			<div class="table-container">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>Ingredient</th>
							<th>Quantity</th>
							<th>Unit</th>
							<th>Notes</th>
						</tr>
					</thead>
					<tbody>
						{#each inventory as item}
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
		{/if}
	</div>
</div>
