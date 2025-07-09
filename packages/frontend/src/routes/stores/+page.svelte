<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { inventoryStore, websocketStore } from '$lib';
	import RealTimeIndicator from '$lib/components/RealTimeIndicator.svelte';
	import StoreList from '$lib/components/StoreList.svelte';

	let unsubscribeWebSocket: (() => void) | null = null;

	// Store subscriptions
	const stores = inventoryStore.stores;
	const loading = inventoryStore.loading;
	const error = inventoryStore.error;
	const lastUpdate = inventoryStore.lastUpdate;

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
	<RealTimeIndicator connectionState={$websocketStore.connectionState} lastUpdate={$lastUpdate} />

	<div class="mb-6">
		<a href="/stores/create" class="btn variant-filled-primary">Create New Store</a>
	</div>

	<StoreList stores={$stores} loading={$loading} error={$error} />
</div>
