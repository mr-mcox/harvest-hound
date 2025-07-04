<script lang="ts">
	export let onSubmit = (data: { inventoryText: string }) => {};

	let inventoryText = '';

	function handleSubmit(event: Event) {
		event.preventDefault();
		onSubmit({ inventoryText });
	}
</script>

<div class="container mx-auto p-4 max-w-4xl">
	<h1 class="text-2xl font-bold mb-6">Upload Inventory</h1>

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

		<div class="flex gap-4">
			<button type="submit" class="btn variant-filled-primary">Upload Inventory</button>
			<a href="/stores" class="btn variant-ghost">Cancel</a>
		</div>
	</form>
</div>
