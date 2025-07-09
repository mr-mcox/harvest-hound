<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { inventoryStore, websocketStore } from '$lib';
	import RealTimeIndicator from '$lib/components/RealTimeIndicator.svelte';

	let unsubscribeWebSocket: (() => void) | null = null;

	// Reactive subscriptions to centralized store
	$: stores = inventoryStore.stores;
	$: loading = inventoryStore.loading;
	$: error = inventoryStore.error;
	$: lastUpdate = inventoryStore.lastUpdate;

	onMount(async () => {
		// Connect to WebSocket for real-time updates
		websocketStore.connect();
		
		// Subscribe to WebSocket events for store updates
		unsubscribeWebSocket = inventoryStore.subscribeToWebSocketEvents();
		
		// Load initial stores data
		await inventoryStore.loadStores();
	});

	onDestroy(() => {
		// Clean up WebSocket subscription
		if (unsubscribeWebSocket) {
			unsubscribeWebSocket();
		}
	});
</script>

<div class="container mx-auto p-4">
	<h1 class="mb-6 text-2xl font-bold">Inventory Stores</h1>

	<!-- Real-time connection status -->
	<RealTimeIndicator 
		connectionState={$websocketStore.connectionState} 
		lastUpdate={$lastUpdate} 
	/>

	<div class="mb-6">
		<a href="/stores/create" class="btn variant-filled-primary">Create New Store</a>
	</div>

	{#if $loading}
		<div class="text-center">
			<div class="placeholder animate-pulse">Loading stores...</div>
		</div>
	{:else if $error}
		<div class="alert variant-filled-error">
			<div class="alert-message">
				<p>{$error}</p>
			</div>
		</div>
	{:else if $stores.length === 0}
		<div class="text-center text-gray-500">
			<p>No stores found. Create your first store to get started!</p>
		</div>
	{:else}
		<div class="grid gap-4">
			{#each $stores as store (store.store_id)}
				<div class="card p-4">
					<div class="flex justify-between items-start">
						<div>
							<h3 class="text-lg font-semibold">{store.name}</h3>
							{#if store.description}
								<p class="mt-1 text-gray-600">{store.description}</p>
							{/if}
						</div>
						<div class="chip variant-soft-primary text-xs">
							{store.item_count} items
						</div>
					</div>
					<div class="mt-2 flex gap-2">
						<a href="/stores/{store.store_id}" class="btn variant-filled-secondary btn-sm"
							>View Inventory</a
						>
						<a href="/stores/{store.store_id}/upload" class="btn variant-filled-primary btn-sm"
							>Upload Items</a
						>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
