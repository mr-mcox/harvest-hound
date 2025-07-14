<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { apiPost } from '$lib/api';
	import type { InventoryUploadResult } from '$lib/types.js';
	import InventoryUpload from '$lib/components/InventoryUpload.svelte';

	let storeId = '';

	onMount(() => {
		storeId = $page.params.id;
	});

	async function handleSubmit(data: { inventoryText: string }): Promise<InventoryUploadResult> {
		const response = await apiPost(`/stores/${storeId}/inventory`, {
			inventory_text: data.inventoryText
		});

		if (!response.ok) {
			// Parse the detailed error response from backend
			try {
				const errorResponse = await response.json();
				const errors = errorResponse.detail?.errors || [`HTTP error! status: ${response.status}`];
				throw new Error(errors.join(', '));
			} catch {
				// Fallback if we can't parse the error response
				throw new Error(`HTTP error! status: ${response.status}`);
			}
		}

		return await response.json();
	}
</script>

<InventoryUpload onSubmit={handleSubmit} {storeId} />
