<script lang="ts">
	import type { InventoryUploadResult } from '$lib/types.js';

	export let onSubmit: (data: { inventoryText: string }) => Promise<InventoryUploadResult>;
	export let storeId: string = '';

	let inventoryText = '';
	let loading = false;
	let error = '';
	let success = '';

	async function handleSubmit(event: Event) {
		event.preventDefault();

		// Clear previous messages
		error = '';
		success = '';
		loading = true;

		try {
			const result = await onSubmit({ inventoryText });
			success = `Successfully added ${result.items_added} items to inventory`;

			// Clear the form on success
			inventoryText = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Upload failed';
		} finally {
			loading = false;
		}
	}
</script>

<div class="container mx-auto max-w-4xl p-4">
	<h1 class="mb-6 text-2xl font-bold">Upload Inventory</h1>

	<form on:submit={handleSubmit} class="space-y-4">
		<div class="form-control">
			<label class="label" for="inventory">
				<span class="label-text">Inventory Items</span>
			</label>
			<textarea
				id="inventory"
				bind:value={inventoryText}
				placeholder="Enter inventory items&#10;2 lbs carrots&#10;1 bunch kale&#10;3 tomatoes"
				class="textarea h-64"
			></textarea>
		</div>

		{#if error}
			<div class="alert variant-filled-error">
				<div class="alert-message">
					<p>{error}</p>
				</div>
			</div>
		{/if}

		{#if success}
			<div class="alert variant-filled-success">
				<div class="alert-message">
					<p>{success}</p>
				</div>
			</div>
		{/if}

		<div class="flex gap-4">
			<button type="submit" disabled={loading} class="btn variant-filled-primary">
				{loading ? 'Uploading...' : 'Upload Inventory'}
			</button>
			{#if storeId}
				<a href="/stores/{storeId}" class="btn variant-ghost">Cancel</a>
			{/if}
		</div>
	</form>
</div>
