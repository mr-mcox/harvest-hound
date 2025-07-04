<script lang="ts">
	export let onSubmit = (data: { name: string; description: string; infinite_supply: boolean }) => {};

	let name = '';
	let description = '';
	let infinite_supply = false;

	function handleSubmit(event: Event) {
		event.preventDefault();
		onSubmit({ name, description, infinite_supply });
	}
</script>

<div class="container mx-auto p-4 max-w-2xl">
	<h1 class="text-2xl font-bold mb-6">Create New Store</h1>

	<form on:submit={handleSubmit} class="space-y-4">
		<div class="form-control">
			<label class="label" for="name">
				<span class="label-text">Store Name</span>
			</label>
			<input
				id="name"
				type="text"
				bind:value={name}
				placeholder="e.g., CSA Box, Pantry, Freezer"
				class="input"
			/>
		</div>

		<div class="form-control">
			<label class="label" for="description">
				<span class="label-text">Description</span>
			</label>
			<textarea
				id="description"
				bind:value={description}
				placeholder="Optional description of this store"
				class="textarea"
				rows="3"
			></textarea>
		</div>

		<div class="form-control">
			<label class="label cursor-pointer justify-start gap-2" for="infinite_supply">
				<input
					id="infinite_supply"
					type="checkbox"
					bind:checked={infinite_supply}
					class="checkbox"
				/>
				<span class="label-text">Infinite Supply</span>
			</label>
		</div>

		<div class="flex gap-4">
			<button type="submit" class="btn variant-filled-primary">Create Store</button>
			<a href="/stores" class="btn variant-ghost">Cancel</a>
		</div>
	</form>
</div>
