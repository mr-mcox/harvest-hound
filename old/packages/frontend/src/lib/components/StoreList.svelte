<script lang="ts">
	import type { StoreView } from '$lib/types';

	export let stores: StoreView[];
	export let loading: boolean = false;
	export let error: string | null = null;
</script>

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
		{#each stores as store (store.store_id)}
			<div class="card p-4" data-testid="store-item">
				<div class="flex items-start justify-between">
					<div>
						<h3 class="text-lg font-semibold">{store.name}</h3>
						{#if store.description}
							<p class="mt-1 text-gray-600">{store.description}</p>
						{/if}
					</div>
					<div class="chip variant-soft-primary text-xs">
						{store.item_count || 0} items
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
