<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { inventoryStore, websocketStore } from '$lib';
	import InventoryTable from '$lib/components/InventoryTable.svelte';
	import RealTimeIndicator from '$lib/components/RealTimeIndicator.svelte';

	let storeId = '';
	let unsubscribeWebSocket: (() => void) | null = null;

	// Reactive subscriptions to centralized store
	$: inventory = inventoryStore.getInventoryForStore(storeId);
	$: loading = inventoryStore.loading;
	$: error = inventoryStore.error;
	$: lastUpdate = inventoryStore.lastUpdate;

	onMount(async () => {
		storeId = $page.params.id;
		
		// Connect to WebSocket for real-time updates
		websocketStore.connect();
		
		// Subscribe to WebSocket events for inventory updates
		unsubscribeWebSocket = inventoryStore.subscribeToWebSocketEvents();
		
		// Load initial inventory data
		await inventoryStore.loadInventoryForStore(storeId);
	});

	onDestroy(() => {
		// Clean up WebSocket subscription
		if (unsubscribeWebSocket) {
			unsubscribeWebSocket();
		}
		
		// Clear store data for this store when leaving page
		// This prevents stale data when navigating between stores
		inventoryStore.clearInventoryForStore(storeId);
	});
</script>

<div class="container mx-auto p-4">
	<div class="mb-4">
		<a href="/stores" class="btn variant-ghost">← Back to Stores</a>
	</div>

	<!-- Real-time connection status -->
	<RealTimeIndicator 
		connectionState={$websocketStore.connectionState} 
		lastUpdate={$lastUpdate} 
	/>
	
	{#if $loading}
		<div class="card">
			<div class="card-header">
				<h2 class="text-lg font-semibold">Loading Inventory...</h2>
			</div>
			<div class="card-body text-center">
				<div class="placeholder animate-pulse">Loading inventory items...</div>
			</div>
		</div>
	{:else if $error}
		<div class="card">
			<div class="card-body">
				<div class="alert variant-filled-error">
					<div class="alert-message">
						<p>{$error}</p>
					</div>
				</div>
			</div>
		</div>
	{:else}
		<InventoryTable inventory={$inventory} {storeId} />
	{/if}
</div>
