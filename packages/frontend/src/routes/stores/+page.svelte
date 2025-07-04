<script lang="ts">
	import { onMount } from 'svelte';

	let stores: any[] = [];
	let loading = false;
	let error = '';

	onMount(async () => {
		await loadStores();
	});

	async function loadStores() {
		loading = true;
		error = '';
		try {
			const response = await fetch('/api/stores');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			stores = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load stores';
		} finally {
			loading = false;
		}
	}
</script>

<div class="container mx-auto p-4">
	<h1 class="text-2xl font-bold mb-6">Inventory Stores</h1>

	<div class="mb-6">
		<a href="/stores/create" class="btn variant-filled-primary">Create New Store</a>
	</div>

	{#if loading}
		<div class="text-center">
			<div class="placeholder animate-pulse">Loading stores...</div>
		</div>
	{:else if error}
		<div class="alert variant-filled-error">
			<div class="alert-message">
				<p>{error}</p>
			</div>
		</div>
	{:else if stores.length === 0}
		<div class="text-center text-gray-500">
			<p>No stores found. Create your first store to get started!</p>
		</div>
	{:else}
		<div class="grid gap-4">
			{#each stores as store}
				<div class="card p-4">
					<h3 class="text-lg font-semibold">{store.name}</h3>
					{#if store.description}
						<p class="text-gray-600 mt-1">{store.description}</p>
					{/if}
					<div class="mt-2 flex gap-2">
						<a href="/stores/{store.store_id}" class="btn variant-filled-secondary btn-sm">View Inventory</a>
						<a href="/stores/{store.store_id}/upload" class="btn variant-filled-primary btn-sm">Upload Items</a>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
