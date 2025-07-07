<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { apiGet } from '$lib/api';
	import type { InventoryItemView } from '$lib/types.js';
	import InventoryTable from '$lib/components/InventoryTable.svelte';

	let inventory: InventoryItemView[] = [];
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

	{#if loading}
		<div class="card">
			<div class="card-header">
				<h2 class="text-lg font-semibold">Loading Inventory...</h2>
			</div>
			<div class="card-body text-center">
				<div class="placeholder animate-pulse">Loading inventory items...</div>
			</div>
		</div>
	{:else if error}
		<div class="card">
			<div class="card-body">
				<div class="alert variant-filled-error">
					<div class="alert-message">
						<p>{error}</p>
					</div>
				</div>
			</div>
		</div>
	{:else}
		<InventoryTable {inventory} {storeId} />
	{/if}
</div>
